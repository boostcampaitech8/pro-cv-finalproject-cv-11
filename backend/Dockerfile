FROM python:3.11.0

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# SSH client for talking to remote GPU server
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /root/.ssh && chmod 700 /root/.ssh

COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip install --system -e .  # Installs dependencies using uv

ARG DEV=false
RUN if [ "$DEV" = "true" ] ; then uv pip install -e .[dev] ; fi

COPY ./app/ ./
# COPY ./ml/model/ ./ml/model/

ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]





# 설명용
# # Python 3.11 공식 이미지 사용
# # (FastAPI, SQLAlchemy, 최신 라이브러리와 궁합 좋음)
# FROM python:3.11.0

# # Python 출력 버퍼링 비활성화
# # → 로그가 바로바로 stdout에 찍힘 (Docker 로그 수집 필수 옵션)
# ENV PYTHONUNBUFFERED 1

# # 컨테이너 내부 작업 디렉토리
# WORKDIR /app

# # -----------------------------
# # 1️⃣ SSH 클라이언트 설치
# # -----------------------------
# # 원격 GPU 서버, 외부 서버 등에 SSH로 접속하기 위함
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends openssh-client && \
#     rm -rf /var/lib/apt/lists/* && \        # apt 캐시 삭제 → 이미지 크기 감소
#     mkdir -p /root/.ssh && chmod 700 /root/.ssh
#                                             # SSH 키 디렉토리 생성 + 권한 설정

# # -----------------------------
# # 2️⃣ Python 의존성 설치
# # -----------------------------

# # 프로젝트 의존성 정의 파일만 먼저 복사
# # → 코드 변경 시에도 의존성 레이어 캐시 재사용
# COPY pyproject.toml ./

# # pip 최신화 + uv 설치 + 의존성 설치
# RUN pip install --upgrade pip && \
#     pip install uv && \
#     uv pip install --system -e .            # uv로 pyproject.toml 기반 의존성 설치
#                                             # --system: venv 없이 컨테이너 전체에 설치
#                                             # -e . : editable 모드 (개발 시 코드 반영)

# # -----------------------------
# # 3️⃣ 개발용 의존성 (선택)
# # -----------------------------

# # 빌드 시 인자로 DEV=true를 주면 dev dependency 설치
# ARG DEV=false
# RUN if [ "$DEV" = "true" ] ; then uv pip install -e .[dev] ; fi
#                                             # pytest, linters 등 개발용 패키지

# # -----------------------------
# # 4️⃣ 애플리케이션 코드 복사
# # -----------------------------

# # FastAPI 애플리케이션 코드 복사
# COPY ./app/ ./

# # ML 모델 파일 복사용 (현재는 주석 처리)
# # COPY ./ml/model/ ./ml/model/

# # -----------------------------
# # 5️⃣ Python 모듈 경로 설정
# # -----------------------------

# # /app 디렉토리를 Python 모듈 검색 경로에 추가
# # → from app.xxx import ... 가능
# ENV PYTHONPATH "${PYTHONPATH}:/app"

# # -----------------------------
# # 6️⃣ 서버 실행 설정
# # -----------------------------

# # FastAPI 서버 포트
# EXPOSE 8000

# # 컨테이너 시작 시 uvicorn 실행
# # main:app → main.py의 app 객체
# # --host 0.0.0.0 → 컨테이너 외부 접근 허용
# # --port 8000 → 서버 포트
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
