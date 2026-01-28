# Help: Project File Guide (자세한 설명)

## 루트
- `.env` / `.env.example`  
  FE·BE·DB가 공통으로 참조하는 환경변수 파일. `docker compose` 실행 시 자동 로드된다. 기본 DB 계정(app/app), CORS 허용 도메인, 프런트 API 베이스 URL, GPU SSH 정보 등이 포함된다. `.env.example`는 템플릿이며 실제 값은 `.env`에 작성한다.  
  - 사용 예: 값 수정 후 `docker compose up --build`로 재기동하여 반영.
- `.gitignore`  
  루트 전역 ignore 규칙(.env, node_modules, 빌드산출물 등)을 정의.
  - 사용 예: 새로 생긴 로그/캐시가 git status에 뜨면 패턴을 추가해 제외.
- `compose.yaml`  
  통합 개발용 Docker Compose. 서비스: `db`(Postgres 16), `backend`(FastAPI), `frontend`(Vite). 포트 매핑 5432/8000/5173. `~/.ssh`를 백엔드에 read-only로 마운트하여 SSH 사용 가능하게 한다.
  - 사용 예: `docker compose up --build`로 전체 스택 기동, `docker compose logs backend -f`로 서버 로그 모니터링.
- `Main.md`  
  작업 로그와 현재 스택 상태를 정리한 문서.
  - 사용 예: 팀 공유용으로 최근 변경사항을 순서대로 기록.
- `gpu.md`  
  GPU 서버 SSH 접속 방법, 포트 사용 예, `.env` 설정법을 상세히 안내.
  - 사용 예: 새 GPU 서버 지급 시 IP/포트만 바꿔 그대로 따라하기.
- `help.md`  
  이 파일. 전체 파일들의 용도와 역할을 상세 설명.

## backend/ (FastAPI 백엔드)
- `.env.example`  
  백엔드 단독 실행 시 참고할 수 있는 예제 환경파일(현재는 루트 `.env`가 주로 사용됨).
- `.gitignore`  
  백엔드 전용 ignore 규칙(venv, __pycache__, 빌드 캐시 등).
- `.pylintrc`  
  pylint 설정 파일. 코드 스타일/품질 검사 규칙을 정의.  
  - 사용 예: `uv run pylint app` 실행 시 규칙 적용.
  - 로컬이나 CI에서 pylint를 실행할 때만 적용됩니다. 현재 Dockerfile에도 pylint 실행 단계가 없으니 “선택적 품질 도구 설정 파일”로 보면 될듯
- `Dockerfile`  
  python:3.11 기반. `uv` 설치 후 의존성 editable 설치, `openssh-client` 포함. 작업 디렉터리 `/app`, 포트 8000 노출, 기본 명령은 `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
  - 사용 예: `docker compose build backend`로 이미지 생성, 개발 서버 기동.
- `Makefile`  
  로컬 개발 유틸 명령 모음. `install`(uv 환경+의존성), `run`(로컬 uvicorn), `deploy`(이전 docker-compose 사용), `clean` 등.
  - 사용 예: 도커 없이 로컬에서 `make install && make run`.
  - 개발자마다 다른 명령을 외우지 않고 동일한 워크플로를 쓰도록 돕는 것이 목적입니다. 도커 안 쓰는 로컬 개발이나 CI 스크립트에도 재사용 가능
- `README.md`  
  백엔드 개발 개요와 구조 설명. ML 관련 안내는 제거되었고 일반 앱 구조만 남아 있음.
  - 사용 예: 새 팀원이 백엔드 구조 파악할 때 참고.
- `pyproject.toml`  
  패키지 메타/의존성 정의. 런타임 의존성: fastapi, uvicorn, requests, loguru, sqlalchemy, psycopg 등. dev 의존성에는 pytest, black 등이 포함.
  - 사용 예: `uv pip install -e .` 실행 시 이 목록 설치.
- `requirements.txt`  
  런타임 의존성 버전 핀 목록. 도커 빌드나 단순 pip 설치 시 사용 가능.
  - 사용 예: `pip install -r requirements.txt`로 최소 환경 구성.
- `tests/`  
  최소 Pytest 스위트. 현재는 연결 체크 엔드포인트(`/api/v1/connect_check`, `/api/v1/db_check`)를 sqlite 인메모리로 패치해 검증하는 `test_connect.py`가 있다.
  - 사용 예: `uv run pytest tests/test_connect.py -q`로 BE 의존성 없이 빠른 연기 테스트 실행.
- `notebooks/.gitkeep`  
  노트북 폴더를 git에 유지하기 위한 더미 파일.
  - 사용 예: 새 노트북을 `backend/notebooks`에 추가하면 폴더가 이미 추적되어 있어 바로 커밋 가능.
  - “빈 폴더라도 버전관리에서 구조를 유지”하려는 용도"

### backend/app/ (애플리케이션 코드)
- `__init__.py`  
  앱 패키지 초기화.
- `db.py`  
  `DATABASE_URL`로 SQLAlchemy `engine`, `SessionLocal`, `Base`를 구성. DB 세션을 얻을 때 `SessionLocal()` 사용.  
  - 사용 예: `with SessionLocal() as db: db.execute(...)` 형태로 트랜잭션 처리.
    - 파이썬 컨텍스트 매니저로 DB 세션을 열고 자동으로 정리하는 패턴, 
- `main.py`  
  FastAPI 앱 생성. `API_PREFIX`(`/api`) 하위에 라우터 등록, 스타트업 이벤트 추가, CORS 미들웨어 설정(`ALLOWED_ORIGINS`).
  - 사용 예: 로컬 실행 시 `uv run uvicorn app.main:app --reload --port 8000`.

### backend/app/api/
- `__init__.py`  
  라우터 패키지 초기화.
- `routes/api.py`  
  상위 APIRouter. 현재 `connect` 라우터를 포함해 `/api/v1` 네임스페이스를 구성.  
  - 사용 예: 새로운 엔드포인트 모듈을 만들면 여기서 `include_router`로 연결.
- `routes/connect.py`  
  헬스/연결 점검용 엔드포인트 제공.  
  - `GET /api/v1/connect_check`: FE → BE 연결 확인(정상 시 200 OK JSON).  
  - `GET /api/v1/db_check`: BE → DB 연결 확인(SELECT 1 실행, 실패 시 503 반환).
  - 사용 예: 프런트 `Connection Checks` 카드의 두 버튼이 이 엔드포인트들을 호출.

### backend/app/core/
- `config.py`  
  `.env`를 읽어 설정값을 로드(API_PREFIX, DEBUG, DATABASE_URL, ALLOWED_ORIGINS 등). loguru/표준 로깅 레벨도 여기서 결정한다.  
  - 사용 예: 배포 환경에서 `ALLOWED_ORIGINS`를 쉼표 구분으로 지정해 CORS 범위 확장.
- `events.py`  
  앱 스타트업 시 DB 메타데이터를 생성(`Base.metadata.create_all`). 모델 프리로딩 로직은 제거됨.
  - 사용 예: 컨테이너가 올라올 때 자동으로 테이블이 생성되므로 별도 마이그레이션 없이 초기 개발 가능.
- `logging.py`  
  `InterceptHandler` 등 loguru와 표준 로거를 연결하는 유틸(모듈 import 시 사용).
  - 사용 예: 표준 `logging` 호출도 loguru 포맷으로 출력되어 로그 수집 일관성 유지.
  - 표준 logging API를 써도 InterceptHandler가 가로채 loguru로 흘려보냄, 
    - 따라서 loguru가 설정한 포맷/레벨/싱크(예: stderr, 파일, JSON 로그 등)로 동일하게 출력되어, 표준 로그와 loguru 로그가 뒤섞여도 한 가지 포맷으로 수집

### backend/app/models/
- `log.py`  
  `RequestLog` SQLAlchemy 모델. 요청/응답 JSON을 `request_logs` 테이블에 저장하기 위한 스키마. (현재 예측 엔드포인트는 제거됐지만 테이블 스키마는 남아 있음.)  
  - 사용 예: 향후 API 요청 로깅을 복구할 때 이 모델을 재사용해 INSERT 수행. -> 크게 안건들 듯

## frontend/ (Vite + React 프런트엔드)
- `.gitignore`  
  프런트 전용 ignore( node_modules, dist 등 ).
- `Dockerfile`  
  node:20-alpine 기반. `npm ci` 후 `npm run dev -- --host --port 5173`로 개발 서버 실행.  
  - 사용 예: `docker compose build frontend` 시 프런트 개발용 이미지 생성.
- `README.md`  
  Vite 기본 안내.
  - 사용 예: Vite 스크립트나 기본 폴더 구조를 잊었을 때 참고.
- `eslint.config.js`  
  ESLint 설정(React Hooks, Refresh 플러그인 포함).
  - 사용 예: `npm run lint` 실행 시 이 규칙이 적용되어 코드 품질 검사.
- `vite.config.js`  
  Vite 설정 파일. 플러그인 로드, 개발 서버 옵션 등 정의.
  - 사용 예: 프록시 설정이나 Base 경로 변경이 필요할 때 수정.
- `package.json` / `package-lock.json`  
  프런트 의존성 및 스크립트 정의(react 19, vite 7 등).
  - 사용 예: 새 라이브러리 추가 후 버전이 여기 반영됨.
- `node_modules/.package-lock.json`  
  npm 내부 메타데이터 파일(자동 생성, 보통 git 무시 대상).
- `index.html`  
  Vite 엔트리 HTML, `#root` 엘리먼트 제공.
  - 사용 예: 메타태그나 글로벌 스크립트 삽입이 필요할 때 수정.
- `public/vite.svg`  
  기본 Vite 아이콘.
- `src/main.jsx`  
  React 진입점. `App` 컴포넌트를 `#root`에 마운트.
  - 사용 예: 전역 Provider(예: React Query, Theme) 추가 시 여기에서 래핑.
- `src/App.jsx`  
  FE↔BE, BE↔DB 연결 확인용 UI. 두 버튼으로 `/api/v1/connect_check`, `/api/v1/db_check` 호출 결과를 표시.
  - 사용 예: 새로운 API 테스트 버튼을 추가해 빠르게 통신 검증.
- `src/App.css`  
  카드/버튼/그리드 등 페이지 전반 스타일. 색상·레이아웃 정의.
  - 사용 예: 테마 컬러나 레이아웃 조정 시 수정.
- `src/index.css`  
  전역 기본 스타일과 폰트 설정.
  - 사용 예: 리셋 스타일이나 폰트 패밀리 변경 시 수정.
