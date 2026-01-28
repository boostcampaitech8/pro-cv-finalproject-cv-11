from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
import json
import requests

app = FastAPI()

# React(3000)에서 FastAPI(8000) 호출하려면 CORS 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 개발 중엔 이거만
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# allow_origins	허용할 프론트 주소
# allow_methods	GET, POST 등 어떤 요청 허용
# allow_headers	어떤 헤더 허용
# allow_credentials	쿠키/토큰 허용 여부

# 프론트: http://localhost:3000 (React)
# 백엔드: http://localhost:8000 (FastAPI)
# cors를 통해 3000에서 오는 요청은 허락하는 과정

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MODEL_SERVER_URL = "http://localhost:9000/infer"
RECEIVED_DIR = "receive"
os.makedirs(RECEIVED_DIR, exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok", "message": "FastAPI 연결 성공"}

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    events: str = Form(...)
):
    event_list = json.loads(events)

    for file in files:
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return {
        "filenames": [f.filename for f in files],
        "events": event_list,
        "message": "업로드 성공"
    }

@app.post("/test-model")
def test_model_server():
    response = requests.post(MODEL_SERVER_URL, stream=True)

    if response.status_code != 200:
        return {"error": "model server request failed"}

    save_path = os.path.join(RECEIVED_DIR, "from_model_server.mp4")

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return {
        "message": "모델 서버로부터 영상 수신 성공",
        "saved_path": save_path,
    }