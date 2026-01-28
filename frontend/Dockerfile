# Vite + React dev container
FROM node:20-alpine

WORKDIR /app

# Install dependencies first to leverage Docker layer cache
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Copy source (rest is bind-mounted in dev for hot reload)
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]






# 설명용
# # Vite + React 개발용 컨테이너 베이스 이미지
# # Node.js 20 LTS + Alpine Linux (가볍고 빠름)
# FROM node:20-alpine

# # 컨테이너 안에서 작업할 기본 디렉토리 설정
# WORKDIR /app

# # -----------------------------
# # 1️⃣ 의존성 먼저 설치 (캐시 활용)
# # -----------------------------

# # 패키지 정의 파일만 먼저 복사
# # → 소스 코드가 바뀌어도 의존성 설치 단계는 캐시 재사용 가능
# COPY package.json package-lock.json ./

# # package-lock.json 기준으로 정확한 버전 설치
# # --legacy-peer-deps:
# #   peer dependency 충돌을 무시하고 설치 (Vite/React 조합에서 자주 필요)
# RUN npm ci --legacy-peer-deps

# # -----------------------------
# # 2️⃣ 소스 코드 복사
# # -----------------------------

# # 전체 소스 복사
# # (개발 모드에서는 docker-compose에서 bind mount로 덮어씌워짐)
# COPY . .

# # -----------------------------
# # 3️⃣ 개발 서버 설정
# # -----------------------------

# # Vite 개발 서버 포트
# # (실제 포트 매핑은 docker-compose에서 수행)
# EXPOSE 5173

# # 컨테이너 시작 시 실행할 기본 명령
# # npm run dev:
# #   package.json의 "dev" 스크립트 실행
# # --host 0.0.0.0:
# #   컨테이너 외부(브라우저)에서 접근 가능하게 함
# # --port 5173:
# #   개발 서버 포트 고정
# CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
