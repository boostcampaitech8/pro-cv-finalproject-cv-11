"""
FastAPI 서버 메인 파일
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json
import uuid
import os
from pathlib import Path
from services import (
    detect_events,
    extract_video_metadata,
    extract_location_info,
    generate_llm_content,
    format_report_data
)

app = FastAPI(
    title="교통 위반 신고 자동화 API",
    description="블랙박스 영상에서 교통 위반 이벤트를 검출하고 신고 양식을 생성하는 API",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 작업 저장소 (메모리 기반, 간단하게)
tasks: Dict[str, Dict] = {}


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/v1/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_info: str = Form(...)
) -> Dict:
    """
    영상 파일 업로드 및 분석 작업 시작
    """
    try:
        # 사용자 정보 파싱
        user_info_dict = json.loads(user_info)
        
        # 작업 ID 생성
        task_id = str(uuid.uuid4())
        
        # 파일 저장
        upload_dir = Path("storage/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        file_content = await file.read()
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 작업 초기화
        tasks[task_id] = {
            "task_id": task_id,
            "status": "processing",
            "progress": 0,
            "current_step": "대기 중...",
            "results": None,
            "error": None
        }
        
        # 백그라운드 작업으로 분석 시작
        background_tasks.add_task(
            process_video_task,
            task_id,
            str(file_path),
            user_info_dict
        )
        
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "영상 분석이 시작되었습니다."
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"사용자 정보 JSON 파싱 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {str(e)}")


@app.get("/api/v1/tasks/{task_id}/status")
async def get_task_status(task_id: str) -> Dict:
    """작업 상태 조회"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "current_step": task.get("current_step"),
        "error": task.get("error")
    }


@app.get("/api/v1/tasks/{task_id}/results")
async def get_task_results(task_id: str) -> Dict:
    """분석 결과 조회"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="작업이 아직 완료되지 않았습니다.")
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "events": task["results"].get("events", []),
        "metadata": task["results"].get("metadata")
    }


@app.post("/api/v1/generate-content")
async def generate_content(
    event_type: str = Form(...),
    violation_type: str = Form(...),
    event_details: str = Form(None),
    api_key: str = Form(None)
) -> Dict[str, str]:
    """LLM을 사용하여 제목과 신고 내용 생성"""
    event_details_dict = None
    if event_details:
        try:
            event_details_dict = json.loads(event_details)
        except:
            pass
    
    return generate_llm_content(
        event_type=event_type,
        violation_type=violation_type,
        event_details=event_details_dict,
        api_key=api_key
    )


@app.post("/api/v1/generate-report")
async def generate_report(
    event: str = Form(...),
    user_info: str = Form(...)
) -> Dict:
    """안전신문고 신고 양식 생성"""
    try:
        event_dict = json.loads(event)
        user_info_dict = json.loads(user_info)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    
    report_data = format_report_data(event_dict, user_info_dict)
    return {"report": report_data}


async def process_video_task(task_id: str, file_path: str, user_info: Dict):
    """영상 분석 백그라운드 작업 (더미 데이터 반환)"""
    import asyncio
    
    try:
        # 작업 시작
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        tasks[task_id]["current_step"] = "영상 파일 로딩 중..."
        await asyncio.sleep(0.5)  # 시뮬레이션
        
        # 메타데이터 추출
        tasks[task_id]["progress"] = 20
        tasks[task_id]["current_step"] = "메타데이터 추출 중..."
        metadata = extract_video_metadata(file_path)
        await asyncio.sleep(0.5)
        
        # 위치 정보 추출
        tasks[task_id]["progress"] = 30
        tasks[task_id]["current_step"] = "위치 정보 추출 중..."
        location = extract_location_info(file_path)
        await asyncio.sleep(0.5)
        
        # 이벤트 검출 (더미 데이터 반환)
        tasks[task_id]["progress"] = 50
        tasks[task_id]["current_step"] = "이벤트 검출 중..."
        await asyncio.sleep(1.0)  # 분석 시뮬레이션
        events = detect_events(file_path, user_info)
        
        # 위치 정보를 이벤트에 추가
        if location:
            for event in events:
                if not event.get("location"):
                    event["location"] = location
        
        # 결과 저장
        tasks[task_id]["progress"] = 90
        tasks[task_id]["current_step"] = "결과 저장 중..."
        await asyncio.sleep(0.3)
        tasks[task_id]["results"] = {
            "events": events,
            "metadata": metadata
        }
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["current_step"] = "완료"
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = f"분석 실패: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

