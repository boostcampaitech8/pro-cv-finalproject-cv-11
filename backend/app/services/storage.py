import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import STORAGE_BASE_DIR

VIDEO_DIR = STORAGE_BASE_DIR / "videos"
CLIP_DIR = STORAGE_BASE_DIR / "clips"
IMG_DIR = STORAGE_BASE_DIR / "imgs"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload_file(upload_file: UploadFile, dest_dir: Path = VIDEO_DIR) -> Path:
    """Save an UploadFile to the local storage directory."""
    ensure_dir(dest_dir)
    dest_path = dest_dir / upload_file.filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return dest_path

# --- GCP placeholder (commented) ---
# The following snippet can replace the local saver when a GCS bucket is ready.
# from google.cloud import storage
# def upload_to_gcs(upload_file: UploadFile, bucket_name: str, dest_path: str) -> str:
#     client = storage.Client()
#     bucket = client.bucket(bucket_name)
#     blob = bucket.blob(dest_path)
#     blob.upload_from_file(upload_file.file, content_type=upload_file.content_type)
#     return blob.public_url  # or gs:// path


def build_example_clip_path(task_id: int, index: int) -> str:
    """Return a demo clip path that the FE can render; file may not physically exist."""
    ensure_dir(CLIP_DIR)
    return str(CLIP_DIR / f"task_{task_id}_clip_{index:04d}.mp4")


def build_example_plate_path(task_id: int, index: int) -> str:
    ensure_dir(IMG_DIR)
    return str(IMG_DIR / f"task_{task_id}_plate_{index:04d}.jpg")
