# Black Duck Web에서 실행하셔야합니다!

## Quick Start
1. **Prerequisites**
   - Docker: https://docs.docker.com/get-docker/
   - Docker Compose: https://docs.docker.com/compose/install/
   - `.env` 준비: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `REDIS_URL`, `ALLOWED_ORIGINS`, `VITE_API_BASE_URL` 등 구성
2. **Run**
   ```bash
   docker compose up --build
   ```
   - 백엔드: http://localhost:8000
   - 프론트엔드(Vite dev): http://localhost:5173


### 궁금한 부분 (현재 코드 기준)

현재 run_remote_inference 함수 내부에서,
매 job 요청마다 아래와 같은 흐름으로 SSH 연결이 이루어지고 있습니다.

> _open_ssh_client()를 통해 매번 새로운 SSHClient 생성 및 connect

job 수행 완료 후 client.close()로 연결 종료
이 구조는 구현은 명확하지만, job이 빈번하게 발생하는 경우 아래와 같은 부분이 조금 궁금합니다.

SSH 연결을 매 요청마다 새로 여는 방식이 성능/리소스 측면에서 효율적인지


현재 구조에서는
SFTP 디렉터리 생성 -> 파일 업로드 -> 원격 실행 -> 결과 다운로드
가 모두 단일 SSH 세션 안에서 순차적으로 처리되는데,
이 방식이 일반적인 GPU 원격 실행 아키텍처로 보았을 때 적절한지 궁금합니다.

### 피드백 받고 싶은 부분

SSH connect를 job 단위로 매번 새로 여는 구조가 적절한지,
아니면 어떻게 개선하는 것이 일반적인지 궁금합니다.

Paramiko + SSH 기반 실행 방식이
소규모/저빈도 job 기준에서는 충분히 합리적인 선택인지
혹은 추후 트래픽 증가를 고려하면 '어떻게' 구조적으로 한계가 있는 방식인지 의견을 듣고 싶습니다.