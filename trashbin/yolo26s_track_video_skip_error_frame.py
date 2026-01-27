#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv26s Vehicle Tracking (Video) - Error Frame Skip Version
- Fine-tuned vehicle detection 모델로 비디오 파일에서 tracking 수행
- 연속된 프레임으로 더 정확한 tracking 가능
- 비디오 디코딩 에러 발생 시 해당 프레임을 스킵하고 계속 진행
"""

import os
from pathlib import Path
from ultralytics import YOLO


# ========== 설정 변수 ==========
# 모델 설정
MODEL_WEIGHT = "./runs/detect/cv-11-final/yolo26s_v5_e30_b64/weights/best.pt"

# 비디오 파일 경로
VIDEO_PATH = "/data/ephemeral/home/dataset/20260115-11h37m24s_N.avi"

# Tracking 설정
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
TRACKER_TYPE = "./models/yolo26s/bytetrack.yaml"  # "botsort.yaml" or "bytetrack.yaml"

# 저장 경로
VERSION = "v5-video-error-skip"
TRACK_PROJECT = f"track"
TRACK_NAME_PREFIX = f"yolo26s_{VERSION}"

# 에러 핸들링 설정
MAX_ERROR_DISPLAY = 10  # 최대 몇 개의 에러까지 출력할지
# ================================


def run_tracking_on_video(model, video_path):
    """
    비디오 파일로 tracking 수행 (에러 프레임 스킵)
    
    Args:
        model: YOLO 모델
        video_path: 비디오 파일 경로
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"[Error] 비디오 파일이 존재하지 않습니다: {video_path}")
        return
    
    # 비디오 파일명 (확장자 제외)
    video_name = video_path.stem
    
    print("\n" + "=" * 70)
    print(f"Tracking 시작: {video_name}")
    print("=" * 70)
    print(f"비디오 파일: {video_path}")
    print(f"Confidence threshold: {CONF_THRESHOLD}")
    print(f"IoU threshold: {IOU_THRESHOLD}")
    print(f"Tracker: {TRACKER_TYPE}")
    print(f"에러 프레임 처리: 스킵 후 계속 진행")
    print()
    
    # 저장 경로 구성: track/yolo26s_{VERSION}/{video_name}
    project_path = f"{TRACK_PROJECT}/{TRACK_NAME_PREFIX}"
    
    try:
        # Tracking 수행
        results = model.track(
            source=str(video_path),
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            persist=True,  # 프레임 간 track 유지
            tracker=TRACKER_TYPE,
            save=True,  # 결과 이미지 저장
            save_txt=True,  # 결과 텍스트 저장

            # 시각화 커스터마이징 파라미터
            show_labels=True,    # 클래스 이름 표시 (기본: True)
            show_conf=True,      # Confidence 값 표시 (기본: True)
            show_boxes=True,     # BBox 표시 (기본: True)
            line_width=1,        # BBox 선 두께 (기본: None=자동)

            project=project_path,
            name=video_name,
            exist_ok=True,
            stream=True,  # 메모리 효율적 처리
        )
        
        # 결과 처리 (stream=True이므로 iteration 필요)
        track_ids_seen = set()
        frame_count = 0
        error_count = 0
        
        print("처리 중...")
        for result in results:
            try:
                frame_count += 1
                
                # Track ID 수집
                if result.boxes and hasattr(result.boxes, 'id') and result.boxes.id is not None:
                    ids = result.boxes.id.int().cpu().tolist()
                    track_ids_seen.update(ids)
                
                # 진행 상황 출력 (100 프레임마다)
                if frame_count % 100 == 0:
                    print(f"  {frame_count} 프레임 처리 완료...")
                    
            except Exception as e:
                error_count += 1
                # 처음 몇 개의 에러만 상세히 출력
                if error_count <= MAX_ERROR_DISPLAY:
                    print(f"  ⚠️  프레임 {frame_count} 처리 중 에러: {e}")
                elif error_count == MAX_ERROR_DISPLAY + 1:
                    print(f"  ⚠️  너무 많은 에러 발생, 이후 에러는 카운트만 수행...")
                # 에러가 발생해도 계속 진행
                continue
        
        print()
        print("=" * 70)
        print("Tracking 완료!")
        print("=" * 70)
        print(f"총 처리 프레임: {frame_count}")
        
        if error_count > 0:
            print(f"⚠️  에러 프레임 수: {error_count} (스킵됨)")
            print(f"✓ 정상 처리 프레임: {frame_count - error_count}")
        
        print(f"고유 Track ID 수: {len(track_ids_seen)}")
        print()
        print(f"📁 결과 저장 위치:")
        print(f"   - 이미지: {TRACK_PROJECT}/{TRACK_NAME_PREFIX}/{video_name}/")
        print(f"   - 텍스트: {TRACK_PROJECT}/{TRACK_NAME_PREFIX}/{video_name}/labels/")
        print("=" * 70)
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Tracking 중 치명적 에러 발생!")
        print("=" * 70)
        print(f"에러 내용: {e}")
        if 'frame_count' in locals():
            print(f"처리된 프레임: {frame_count}")
            print(f"에러 프레임: {error_count}")
        print()
        print("비디오 파일이 심각하게 손상되었거나 호환되지 않는 형식일 수 있습니다.")
        print("ffmpeg로 재인코딩을 시도해보세요:")
        print(f"  ffmpeg -i {video_path} -c:v libx264 -crf 23 output.mp4")
        print("=" * 70)


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("YOLOv26s Vehicle Tracking (Video) - Error Skip")
    print("=" * 70)
    print()
    
    # Step 1: 모델 로드
    print("[Step 1] 모델 로드")
    print("-" * 70)
    print(f"모델: {MODEL_WEIGHT}")
    
    if not os.path.exists(MODEL_WEIGHT):
        print(f"[Error] 모델 파일을 찾을 수 없습니다: {MODEL_WEIGHT}")
        return
    
    model = YOLO(MODEL_WEIGHT)
    print("✓ 모델 로드 완료")
    print()
    
    # Step 2: Tracking 수행
    print("[Step 2] 비디오 Tracking (에러 프레임 스킵 모드)")
    print("-" * 70)
    
    run_tracking_on_video(model, VIDEO_PATH)
    
    print("\n✓ 모든 작업 완료!")


if __name__ == '__main__':
    main()

