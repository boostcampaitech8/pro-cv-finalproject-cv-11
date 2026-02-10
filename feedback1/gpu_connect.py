import json
import os
import shlex
import select
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import paramiko

from app.core import config

import logging

logger = logging.getLogger(__name__)


@dataclass
class GPUSettings:
    """Collected SSH/GPU runtime settings pulled from environment."""

    host: str = config.GPU_SSH_HOST
    user: str = config.GPU_SSH_USER
    port: int = config.GPU_SSH_PORT
    key_path: str = config.GPU_SSH_KEY_PATH
    password: str = str(config.GPU_SSH_PASSWORD) if config.GPU_SSH_PASSWORD else ""
    remote_in_dir: str = config.GPU_REMOTE_IN_DIR
    remote_out_dir: str = config.GPU_REMOTE_OUT_DIR
    remote_script: str = config.GPU_REMOTE_SCRIPT
    remote_python: str = config.GPU_REMOTE_PYTHON
    remote_venv: str = config.GPU_REMOTE_VENV
    visible_devices: str = config.GPU_VISIBLE_DEVICES
    remote_result_file: str = config.GPU_REMOTE_RESULT_FILE
    bucket: str = config.GCS_BUCKET_NAME


def _open_ssh_client(cfg: GPUSettings) -> paramiko.SSHClient:
    """Return a connected Paramiko SSHClient."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_path = os.path.expanduser(cfg.key_path) if cfg.key_path else None
    client.connect(
        hostname=cfg.host,
        port=cfg.port,
        username=cfg.user,
        key_filename=key_path,
        password=cfg.password or None,
        timeout=10,
    )
    return client


def _sftp_mkdir_p(sftp: paramiko.SFTPClient, remote_path: str) -> None:
    """Create remote directories like `mkdir -p`."""
    parts = Path(remote_path).parts
    current = ""
    for part in parts:
        current = os.path.join(current, part)
        try:
            sftp.stat(current)
        except IOError:
            sftp.mkdir(current)


def stream_remote_logs(
    stdout: paramiko.ChannelFile,
    stderr: paramiko.ChannelFile,
    logger: logging.Logger,
    job_id: str,
) -> None:
    while True:
        rl, _, _ = select.select([stdout.channel], [], [], 0.5)

        if stdout.channel in rl:
            if stdout.channel.recv_ready():
                line = stdout.channel.recv(1024).decode("utf-8", "ignore")
                if line:
                    for l in line.rstrip().splitlines():
                        logger.info("[GPU][job=%s] %s", job_id, l)

            if stdout.channel.recv_stderr_ready():
                line = stdout.channel.recv_stderr(1024).decode("utf-8", "ignore")
                if line:
                    for l in line.rstrip().splitlines():
                        logger.error("[GPU][job=%s] %s", job_id, l)

            if stdout.channel.exit_status_ready():
                break

def run_remote_inference(
    local_input: Optional[Path],
    job_meta: Dict[str, Any],
    cfg: Optional[GPUSettings] = None,
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    cfg = cfg or GPUSettings()
    job_id = job_id or job_meta.get("job_id")
    if not job_id:
        raise ValueError("job_id is required")

    if "input_path" not in job_meta:
        raise ValueError("job_meta must contain input_path")

    client = _open_ssh_client(cfg)
    sftp = client.open_sftp()

    try:
        remote_job_dir = f"{cfg.remote_in_dir}/{job_id}"
        remote_job_json = f"{remote_job_dir}/job.json"
        remote_result = f"{cfg.remote_out_dir}/{job_id}/{cfg.remote_result_file}"

        # ensure dirs
        _sftp_mkdir_p(sftp, remote_job_dir)
        _sftp_mkdir_p(sftp, cfg.remote_out_dir)

        job_meta = dict(job_meta)
        job_meta.setdefault("job_id", job_id)
        job_meta.setdefault("out_root", cfg.remote_out_dir)

        remote_input_path = job_meta["input_path"]

        # ✅ local input이면: input_path 위치로 업로드
        if local_input:
            _sftp_mkdir_p(sftp, str(Path(remote_input_path).parent))
            sftp.put(str(local_input), remote_input_path)

        # ❌ input_path 건드리지 않음
        # ❌ input_url도 여기서 만들지 않음 (caller 책임)

        with sftp.open(remote_job_json, "w", bufsize=65536) as f:
            f.write(json.dumps(job_meta, ensure_ascii=False))

        gpu_env = f"CUDA_VISIBLE_DEVICES={cfg.visible_devices} " if cfg.visible_devices else ""
        venv_activate = ""
        if cfg.remote_venv:
            venv_path = cfg.remote_venv.rstrip("/")
            venv_activate = f"source {shlex.quote(venv_path)}/bin/activate && "
        
        work_dir = "/data/ephemeral/home/model_connect"

        base_cmd = (
            f"{venv_activate}"
            f"cd {work_dir} && "
            f"{gpu_env}{shlex.quote(cfg.remote_python)} "
            f"{shlex.quote(cfg.remote_script)} --job {shlex.quote(remote_job_json)} --bucket {shlex.quote(cfg.bucket)}"
        )
        cmd = f"bash -lc {shlex.quote(base_cmd)}"

        stdin, stdout, stderr = client.exec_command(cmd, timeout=3600, get_pty=True)
        stream_remote_logs(stdout, stderr, logger, job_id)
        rc = stdout.channel.recv_exit_status()

        out_txt = stdout.read().decode("utf-8", "ignore")
        err_txt = stderr.read().decode("utf-8", "ignore")

        if rc != 0:
            raise RuntimeError(
                f"Remote failed rc={rc}\nSTDOUT:\n{out_txt}\nSTDERR:\n{err_txt}"
            )

        local_result = Path(tempfile.gettempdir()) / f"{job_id}_result.json"
        sftp.get(remote_result, str(local_result))
        result_data = json.loads(local_result.read_text())

        result_data.setdefault("job_id", job_id)
        result_data.setdefault("stdout", out_txt.strip())
        return result_data

    finally:
        try:
            sftp.close()
        finally:
            client.close()
