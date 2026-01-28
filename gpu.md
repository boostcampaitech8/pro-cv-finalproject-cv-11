# GPU 서버 연동 가이드

## 1) SSH 접속 설정 (호스트 기준)
- 키 저장: `~/.ssh/cv-11-3_key.pem`
- 권한: `chmod 600 ~/.ssh/cv-11-3_key.pem`
- 호스트키 등록(1회): `ssh-keyscan -p 31541 10.28.228.37 >> ~/.ssh/known_hosts`
- 접속 테스트: `ssh -i ~/.ssh/cv-11-3_key.pem -p 31541 root@10.28.228.37`

## 2) 백엔드 컨테이너에서 동일 키 사용
- compose가 `~/.ssh`를 read-only로 마운트함 → 추가 설정 불필요
- 컨테이너 내부 테스트:
  `docker compose exec backend ssh -i /root/.ssh/cv-11-3_key.pem -p 31541 root@10.28.228.37 'hostname'`

## 3) GPU 서버에서 모델 서비스 띄우기 (예시)
- GPU 서버에서 Docker나 uvicorn 등으로 HTTP 엔드포인트를 띄우고 포트 범위 30993~31000 중 하나 사용 (예: 30993)
- 서비스 예: `uvicorn app:app --host 0.0.0.0 --port 30993` 또는 `docker run -p 30993:8000 your-model-image`

## 4) 로컬/백엔드에서 모델 URL 설정
- `.env`에 설정: `MODEL_URL=http://10.28.228.37:30993`
- 반영: `docker compose restart backend` (또는 `up --build`)
- 백엔드는 `MODEL_URL`이 있으면 요청을 GPU 서버로 포워딩함 (`POST {MODEL_URL}/predict` with `{"data": ...}`)

## 5) 연결 확인 플로우
- FE → BE: `GET /api/v1/connect_check` (프런트 버튼으로 실행)
- BE → DB: `GET /api/v1/db_check`
- BE → GPU 모델: `curl -X POST http://10.28.228.37:30993/predict -d '{"data":[[0,0,0,0,0]]}' -H 'Content-Type: application/json'` (GPU 서버에서 모델이 떠 있어야 응답)

## 6) 트러블슈팅
- 권한 오류: 키 파일 600인지 확인
- 연결 거부: 포트(31541, 30993 등) 방화벽/보안그룹 열려 있는지 확인
- DNS 대신 IP 사용 권장: `10.28.228.37`
