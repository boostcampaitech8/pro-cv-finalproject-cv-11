# 현재 DB 스키마 (FastAPI + SQLAlchemy 기준)

> 실제 생성되는 테이블/열을 소스 코드와 동일하게 정리했습니다. 기본값은 `timezone=True` now()이며, `create_all`이 ALTER를 수행하지 않으므로 기존 DB는 수동 마이그레이션이 필요합니다.

## Enum
```sql
CREATE TYPE service_status AS ENUM ('UPLOADING','PROCESSING','COMPLETED','FAILED');
```

## 테이블
```sql
CREATE TABLE videos (
  id            SERIAL PRIMARY KEY,
  filename      VARCHAR(255) NOT NULL,
  filepath      VARCHAR(512) NOT NULL,
  uploaded_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tasks (
  id            SERIAL PRIMARY KEY,
  video_id      INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  status        service_status NOT NULL DEFAULT 'UPLOADING',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_tasks_video UNIQUE (video_id)
);

CREATE TABLE task_events (
  id            SERIAL PRIMARY KEY,
  task_id       INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  event_type_id INTEGER NOT NULL REFERENCES event_types(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_task_events UNIQUE (task_id, event_type_id)
);

CREATE TABLE event_types (
  id          SERIAL PRIMARY KEY,
  event_name  VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE analysis_results (
  id                 SERIAL PRIMARY KEY,
  task_id            INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  event_type_id      INTEGER NOT NULL REFERENCES event_types(id) ON DELETE CASCADE,
  clip_path          VARCHAR(512),
  occurred_time      TIMESTAMPTZ,
  license_plate_img  VARCHAR(512),
  license_plate_text VARCHAR(512),
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE reports (
  id            SERIAL PRIMARY KEY,
  result_id     INTEGER NOT NULL REFERENCES analysis_results(id) ON DELETE SET NULL,
  title         VARCHAR(255) NOT NULL,
  description   TEXT NOT NULL,
  occurred_time TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE request_logs (
  id       SERIAL PRIMARY KEY,
  request  TEXT NOT NULL,
  response TEXT NOT NULL
);
```

## 시드 데이터
- 애플리케이션 시작 시 기본 이벤트 타입이 자동 삽입됨 (중복 방지):
  - 1: 불법 유턴
  - 2: 신호 위반
  - 3: 불법 주정차
  - 4: 과속
