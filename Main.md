# Project Log (FE-BE-DB Compose + GPU SSH)

_Date_: 2026-01-28 (UTC−05 assumed)

## What was done
1) Added dev Dockerfile for Vite React app at `frontend/Dockerfile` (Node 20, runs `npm run dev --host --port 5173`).
2) Hardened backend image in `backend/Dockerfile` with `openssh-client`, SSH folder prep, and exposed port 8000 to match compose command.
3) Enhanced root `compose.yaml`:
   - Shared `.env` for db/backend/frontend variables
   - Mounted host `~/.ssh` read-only into backend so it can SSH to GPU server
   - Passed GPU SSH env (`GPU_SSH_HOST/GPU_SSH_USER/GPU_SSH_PORT`) to backend
4) Created `.env` + `.env.example` with sane defaults for Postgres, backend, frontend, and GPU SSH settings.
5) Added root `.gitignore` to keep `.env`, build artifacts, and virtualenv noise out of VCS.
6) Backend code tweaks (user edits on 2026-01-25):
   - Switched internal imports to absolute `app.*` paths (e.g., `app.core`, `app.db`), so running under compose with `/app` bind mount keeps imports consistent.
   - Startup handler (`core/events.py`) now focuses on DB table creation; model preloading remains disabled by default (`preload_model` kept commented).
7) Connectivity endpoints added (2026-01-25):
   - `GET /api/v1/connect_check` → FE→BE 핑
   - `GET /api/v1/db_check` → BE→DB 핑 (`SELECT 1`)
8) ML 로직 제거 (2026-01-25):
   - 로컬/원격 모델 관련 코드, 엔드포인트, 테스트, env 설정, `backend/ml` 디렉터리 삭제
9) 최소 Pytest 복구 (2026-01-25):
   - `backend/tests/test_connect.py`에서 sqlite 인메모리를 사용해 `/api/v1/connect_check`와 `/api/v1/db_check` 정상 응답을 검증
10) DB 스키마 초안 추가 (2026-01-28):
   - `db_schema.md`에 원본영상/작업/분석 이벤트 타입/분석 결과/신고 정보 테이블 정의 정리

## Updates 2026-01-29
1) 전체 API 구현 (FastAPI): 업로드/파일반환/메타조회, task 시작/폴링, 결과 목록, 결과 수정·삭제, 이벤트 타입 조회, 신고 생성·조회.
2) 비디오 업로드는 로컬 `backend/storage/videos`에 저장하며 GCS 업로드 코드는 주석으로 포함해 추후 전환 가능.
3) 분석 시작 시 요청 이벤트 타입을 `task_events` 테이블에 기록하고, 백그라운드 데모 워커가 결과를 생성해 COMPLETED로 전환. GPU SSH 실행 예제는 Paramiko 주석으로 남김.
4) 기본 이벤트 타입 시드(불법 유턴/신호 위반/불법 주정차/과속) 자동 삽입, 최신 스키마를 `db_schema.md`에 반영.

## How to run locally (dev)
- Make sure Docker/Compose is running.
- Edit `.env` if needed (copy from `.env.example`). Key defaults:
  - `VITE_API_BASE_URL=http://localhost:8000/api`
  - `POSTGRES_*` and `DATABASE_URL` already aligned for the db container
  - `GPU_SSH_HOST/USER/PORT` placeholders for your remote GPU box
- Start stack: `docker compose up --build`
  - Backend: http://localhost:8000
  - Frontend (Vite dev): http://localhost:5173
  - Postgres: localhost:5432 (container name `db`)

## Enabling SSH to the GPU server from backend
- Place your SSH key on the host (e.g., `~/.ssh/id_rsa`) and ensure permissions are 600.
- Add the GPU host key once on the host: `ssh-keyscan -H $GPU_SSH_HOST >> ~/.ssh/known_hosts`.
- Compose automatically mounts `~/.ssh` into the backend container at `/root/.ssh` (read-only) and `openssh-client` is installed there.
- Test from inside the container:
  - `docker compose exec backend ssh -p $GPU_SSH_PORT $GPU_SSH_USER@$GPU_SSH_HOST 'nvidia-smi'`
- If you prefer an agent instead of mounting keys, run `ssh-agent` on the host and forward the socket into the container (adjust volume mounting accordingly).

## Notes on folders
- `backend/` FastAPI app (uvicorn served via compose). 현재 엔드포인트: `/api/v1/connect_check`, `/api/v1/db_check`, `/api/v1/videos*`, `/api/v1/tasks*`, `/api/v1/results*`, `/api/v1/event-types`, `/api/v1/reports*`.
- `frontend/` React + Vite dev server; hot reload via bind mount. UI도 연결 체크만 노출.
- `compose.yaml` at repo root coordinates db/backend/frontend + SSH mount.

## Next checks
- 필요 시 새로운 모델 API를 GPU 서버에서 HTTP로 제공하고, 추후 백엔드에 연동 코드를 추가
- CI와 프로덕션용 Dockerfile(정적 빌드, 백엔드 서버) 준비
