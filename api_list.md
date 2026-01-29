- API 최최종
    
    ## 공통 응답 포맷 (권장)
    
    - Content-Type: JSON
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "요청이 성공했습니다.",
      "data": {}
    }
    ```
    
    ---
    
    # STEP 1 - 업로드 (`UPLOADING`)
    
    ## 1) 비디오 업로드 API (GCS 업로드 + DB 저장)
    
    **기본 정보**
    
    - Method: `POST`
    - Path: `/api/v1/videos`
    - 권한: (예) 로그인 사용자
    - 설명: 원본 영상을 업로드하고 `원본영상(video)`을 생성. 동시에 `작업(task)`을 만들고 status를 `UPLOADING`으로 기록
    - 현재 구현: 로컬 `backend/storage/videos`에 저장 후 DB 기록. GCS 업로드 코드는 주석으로 포함되어 있어 연결 후 교체 가능.
    
    **요청 형식**
    
    - Request Body
        - Content-Type: `multipart/form-data`
            - `file`: video file (mp4 등)
    
    **응답 형식**
    
    - Content-Type: JSON
    
    ```json
    {
      "status": 201,
      "success": true,
      "message": "비디오 업로드가 완료되었습니다.",
      "data": {
        "video": {
          "video_id": 101,
          "filename": "sample.mp4",
          "filepath": "gs://bucket/path/sample.mp4",
          "uploaded_at": "2026-01-29T10:11:12Z"
        },
        "task": {
          "task_id": 9001,
          "video_id": 101,
          "status": "UPLOADING",
          "task_created_at": "2026-01-29T10:11:12Z"
        }
      }
    }
    
    ```
    
    > 참고(옵션): 대용량/트래픽 고려하면 “Presigned URL 방식”으로 업로드 URL 발급 / 업로드 완료 콜백 API를 별도로 두는 것도 좋아. 다만 너희 설명 기준으론 위 1개 API로도 구성 가능.
    > 
    
    ---
    
    ## 2) 비디오 반환(다운로드/스트리밍) API
    
    **기본 정보**
    
    - Method: `GET`
    - Path: `/api/v1/videos/file`
    - 권한: (예) 로그인 사용자
    - 설명: 비디오 이름(또는 id)로 실제 파일을 반환(다운로드/스트리밍)
    
    **요청 형식**
    
    - Query Parameter
        - `filename`: 비디오 파일명 (예: sample.mp4)
    
    **응답 형식**
    
    - Content-Type: `video/mp4` (또는 실제 파일 타입)
    - Response Body: 바이너리 파일 스트림
    
    **에러 응답 예시**
    
    ```json
    {
      "status": 404,
      "success": false,
      "message": "해당 filename의 비디오를 찾을 수 없습니다.",
      "data": null
    }
    
    ```
    
    ---
    
    ## (권장) 3) 비디오 메타/현재 상태 조회 API
    
    **기본 정보**
    
    - Method: `GET`
    - Path: `/api/v1/videos/{video_id}`
    - 권한: (예) 로그인 사용자
    - 설명: 원본영상 메타 + 연결된 작업(task)의 상태 확인 (클라이언트 화면 구성에 유용)
    
    **요청 형식**
    
    - URL Parameter
        - `video_id`: 원본영상 ID
    
    **응답 형식**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "비디오 정보를 조회했습니다.",
      "data": {
        "video_id": 101,
        "filename": "sample.mp4",
        "filepath": "gs://bucket/path/sample.mp4",
        "uploaded_at": "2026-01-29T10:11:12Z",
        "task": {
          "task_id": 9001,
          "status": "UPLOADING"
        }
      }
    }
    
    ```
    
    ---
    
    # STEP 2 - 분석
    
    ## 4) 인자 체크 및 분석 시작 API (비동기 시작) `PROCESSING`
    
    **기본 정보**
    
    - Method: `POST`
    - Path: `/api/v1/tasks/{task_id}/start`
    - 권한: (예) 로그인 사용자
    - 설명: 선택한 분석 Task(event_type)들을 저장하고, Celery 비동기 작업을 시작. task status를 `PROCESSING`으로 변경
    - 현재 구현: 백그라운드 데모 작업이 결과를 생성해 `COMPLETED`로 전환. GPU 서버 SSH 실행 예제는 코드에 주석으로 포함.
    
    **요청 형식**
    
    - URL Parameter
        - `task_id`: 작업 ID
    - Request Body
        - Content-Type: JSON
    
    ```json
    {
      "event_type_ids": [1, 3, 7]
    }
    
    ```
    
    **응답 형식**
    
    ```json
    {
      "status": 202,
      "success": true,
      "message": "분석을 시작했습니다.",
      "data": {
        "task_id": 9001,
        "video_id": 101,
        "status": "PROCESSING",
        "requested_event_type_ids": [1, 3, 7]
      }
    }
    
    ```
    
    > 너희가 적은 흐름대로라면: 이 API는 “task 생성/갱신 + Celery 시작”만 하고 끝.
    > 
    
    ---
    
    ## 5) 분석 확인(폴링) API: `PROCESSING` / `COMPLETED` + 결과(클립 pth) 반환
    
    **기본 정보**
    
    - Method: `GET`
    - Path: `/api/v1/tasks/{task_id}`
    - 권한: (예) 로그인 사용자
    - 설명:
        - 아직 분석이 덜 끝났으면 `PROCESSING` 반환
        - 결과 파일이 감지되어 DB 반영까지 끝났으면 `COMPLETED` + 분석 결과(클립들) 반환
        - (서버 내부 동작) 결과 파일 발견 시 트랜잭션으로 `분석결과 INSERT` + `task COMPLETED UPDATE`
    
    **요청 형식**
    
    - URL Parameter
        - `task_id`: 작업 ID
    
    **응답 형식 (분석 중)**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "분석이 진행 중입니다.",
      "data": {
        "task_id": 9001,
        "status": "PROCESSING"
      }
    }
    
    ```
    
    **응답 형식 (완료 + 클립/결과 포함)**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "분석이 완료되었습니다.",
      "data": {
        "task": {
          "task_id": 9001,
          "video_id": 101,
          "status": "COMPLETED"
        },
        "results": [
          {
            "result_id": 50001,
            "event_type": {
              "event_type_id": 1,
              "event_name": "불법 유턴"
            },
            "clip_path": "gs://bucket/clips/101/clip_0001.mp4",
            "occurred_time": "2026-01-29T10:13:40Z",
            "license_plate_img": "gs://bucket/plates/101/plate_0001.jpg",
            "license_plate_text": "12가3456",
            "result_created_at": "2026-01-29T10:15:01Z"
          }
        ]
      }
    }
    
    ```
    
    ---
    
    ## (권장) 6) 특정 비디오의 분석 결과 목록 조회 API
    
    **기본 정보**
    
    - Method: `GET`
    - Path: `/api/v1/videos/{video_id}/results`
    - 권한: (예) 로그인 사용자
    - 설명: 같은 영상(`video_id`)에 속한 `분석 결과`들을 반환 (클립 목록 화면에 바로 쓰기 좋음)
    
    **요청 형식**
    
    - URL Parameter
        - `video_id`: 원본영상 ID
    
    **응답 형식**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "분석 결과 목록을 조회했습니다.",
      "data": {
        "video_id": 101,
        "results": [
          {
            "result_id": 50001,
            "event_type_id": 1,
            "clip_path": "gs://bucket/clips/101/clip_0001.mp4",
            "occurred_time": "2026-01-29T10:13:40Z",
            "license_plate_text": "12가3456",
            "license_plate_img": "gs://bucket/plates/101/plate_0001.jpg"
          }
        ]
      }
    }
    
    ```
    
    ---
    
    ## 7) 클립(분석 결과) 정보 수정 API `[patch]`
    
    **기본 정보**
    
    - Method: `PATCH`
    - Path: `/api/v1/results/{result_id}`
    - 권한: (예) 로그인 사용자
    - 설명: 클립 상세보기에서 내용 수정 후 ‘수정완료’ 시 반영 (필요한 필드만 부분 수정)
    
    **요청 형식**
    
    - URL Parameter
        - `result_id`: 분석 결과 ID
    - Request Body
        - Content-Type: JSON
    
    ```json
    {
      "event_type_id": 3,
      "occurred_time": "2026-01-29T10:13:45Z",
      "license_plate_text": "34나7890"
    }
    
    ```
    
    **응답 형식**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "클립 정보가 수정되었습니다.",
      "data": {
        "result_id": 50001,
        "event_type_id": 3,
        "occurred_time": "2026-01-29T10:13:45Z",
        "license_plate_text": "34나7890"
      }
    }
    
    ```
    
    ---
    
    ## 8) 클립(분석 결과) 구간 삭제 API `[delete]`
    
    **기본 정보**
    
    - Method: `DELETE`
    - Path: `/api/v1/results/{result_id}`
    - 권한: (예) 로그인 사용자
    - 설명: 클립 목록에서 X 클릭 시 해당 결과 삭제
    
    **요청 형식**
    
    - URL Parameter
        - `result_id`: 분석 결과 ID
    
    **응답 형식**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "클립이 삭제되었습니다.",
      "data": {
        "result_id": 50001,
        "deleted": true
      }
    }
    
    ```
    
    ---
    
    ## (권장) 9) 분석 이벤트 타입 목록 조회 API
    
    **기본 정보**
    
    - Method: `GET`
    - Path: `/api/v1/event-types`
    - 권한: (예) 로그인 사용자
    - 설명: 분석 버튼에서 선택할 이벤트 타입 리스트 제공
    
    **요청 형식**
    
    - (없음)
    
    **응답 형식**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "이벤트 타입 목록을 조회했습니다.",
      "data": {
        "event_types": [
          { "event_type_id": 1, "event_name": "불법 유턴" },
          { "event_type_id": 3, "event_name": "불법 주정차" }
        ]
      }
    }
    
    ```
    
    ---
    
    # STEP 3 - 신고
    
    ## 10) 신고 전송 API `[post]`
    
    **기본 정보**
    
    - Method: `POST`
    - Path: `/api/v1/reports`
    - 권한: (예) 로그인 사용자
    - 설명: ‘신고 전송’ 버튼 클릭 시 `신고 정보` 저장 (분석 결과(result_id) 기반)
    
    **요청 형식**
    
    - Request Body
        - Content-Type: JSON
    
    ```json
    {
      "result_id": 50001,
      "title": "불법 유턴 신고",
      "description": "교차로에서 불법 유턴이 확인됩니다.",
      "occurred_time": "2026-01-29T10:13:40Z"
    }
    
    ```
    
    **응답 형식**
    
    ```json
    {
      "status": 201,
      "success": true,
      "message": "신고가 접수되었습니다.",
      "data": {
        "report_id": 70001,
        "result_id": 50001,
        "title": "불법 유턴 신고",
        "description": "교차로에서 불법 유턴이 확인됩니다.",
        "occurred_time": "2026-01-29T10:13:40Z",
        "report_created_at": "2026-01-29T10:20:10Z"
      }
    }
    
    ```
    
    ---
    
    ## (권장) 11) 신고 조회 API
    
    **기본 정보**
    
    - Method: `GET`
    - Path: `/api/v1/reports/{report_id}`
    - 권한: (예) 로그인 사용자
    - 설명: 신고 상세 조회 (신고 접수 결과 화면 등)
    
    **요청 형식**
    
    - URL Parameter
        - `report_id`: 신고 ID
    
    **응답 형식**
    
    ```json
    {
      "status": 200,
      "success": true,
      "message": "신고 정보를 조회했습니다.",
      "data": {
        "report_id": 70001,
        "result_id": 50001,
        "title": "불법 유턴 신고",
        "description": "교차로에서 불법 유턴이 확인됩니다.",
        "occurred_time": "2026-01-29T10:13:40Z",
        "report_created_at": "2026-01-29T10:20:10Z"
      }
    }
    
    ```
    
    ---
    
    # 한 눈에 보는 API 목록 (요약)
    
    - **POST** `/api/v1/videos` : 업로드(+task UPLOADING)
    - **GET** `/api/v1/videos/file?filename=...` : 비디오 파일 반환
    - **GET** `/api/v1/videos/{video_id}` : 비디오 메타 + 상태
    - **POST** `/api/v1/tasks/{task_id}/start` : 분석 시작(+PROCESSING)
    - **GET** `/api/v1/tasks/{task_id}` : 분석 상태 폴링(+완료 시 results 포함)
    - **GET** `/api/v1/videos/{video_id}/results` : 결과 목록(클립 리스트)
    - **PATCH** `/api/v1/results/{result_id}` : 클립 수정
    - **DELETE** `/api/v1/results/{result_id}` : 클립 삭제
    - **GET** `/api/v1/event-types` : 분석 이벤트 타입 목록
    - **POST** `/api/v1/reports` : 신고 전송
    - **GET** `/api/v1/reports/{report_id}` : 신고 조회(권장)
    
    ---
    
    원하면, 위 명세를 기반으로 **ERD 관점에서 FK/UNIQUE 제약(예: task.video_id unique), 인덱스 추천, 상태 전이 규칙(UPLOADING→PROCESSING→COMPLETED)**까지 같이 “규칙 문서” 형태로 붙여줄게.
