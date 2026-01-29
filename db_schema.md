- 재수정한 SQL 테이블 생성
    
    CREATE TABLE `분석 결과` (
    `result_id`	bigint	NOT NULL, ← 고유키
    `task_id`	bigint	NOT NULL, ← 왜래키
    `event_type_id`	bigint	NOT NULL
    `clip_path`	varchar	NULLABLE,
    `occurred_time`	datetime	NULLABLE,
    `license_plate_img`	varchar	NULLABLE,
    `license_plate_text`	varchar	NULLABLE,
    `result_created_at`	datetime	NOT NULL
    );
    
    CREATE TABLE `분석 이벤트 타입` (
    `event_type_id`	bigint	NOT NULL ← 고유키
    `event_name`	varchar	NOT NULL,
    );
    
    CREATE TABLE `작업` (
    
    `task_id`	bigint	NOT NULL, ← 고유키 
    `video_id`	bigint	NOT NULL, ← 외래키 (유니크)
    `status`	status	NOT NULL,
    `task_created_at`	datetime	NOT NULL
    );
    
    CREATE TABLE `원본영상` (
    `video_id`	bigint	NOT NULL, ← 고유키 
    `filename`	varchar	NOT NULL,
    `filepath`	varchar	NOT NULL,
    `uploaded_at`	datetime	NOT NULL
    );
    
    CREATE TABLE `신고 정보` (
    `report_id`	bigint	NOT NULL, ← 고유키
    `result_id`	bigint	NOT NULL, ← 왜래키
    `title`	varchar	NOT NULL,
    `description`	text	NOT NULL,
    `occurred_time`	datetime	NOT NULL,
    `report_created_at`	datetime	NOT NULL
    );