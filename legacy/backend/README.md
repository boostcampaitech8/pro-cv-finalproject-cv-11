# Backend API Server

간단한 FastAPI 서버 (depth 1 구조)

## 파일 구조

```
backend/
├── main.py              # FastAPI 앱 (엔트리 포인트)
├── services.py          # 비즈니스 로직 (더미 데이터 포함)
├── dummy_events.json    # 더미 이벤트 데이터
└── README.md
```

## 실행 방법

```bash
cd backend
python main.py
```

또는

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

- `GET /health` - 서버 상태 확인
- `POST /api/v1/upload` - 영상 업로드 및 분석 시작
- `GET /api/v1/tasks/{task_id}/status` - 작업 상태 조회
- `GET /api/v1/tasks/{task_id}/results` - 분석 결과 조회
- `POST /api/v1/generate-content` - LLM 콘텐츠 생성
- `POST /api/v1/generate-report` - 신고 양식 생성

## 현재 상태

- 모든 기능이 더미 데이터로 동작
- 모델 없이도 테스트 가능
- 실제 모델 연결 시 `services.py`의 함수들만 수정하면 됨

