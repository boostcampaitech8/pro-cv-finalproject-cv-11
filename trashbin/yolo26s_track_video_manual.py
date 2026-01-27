#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv26s Vehicle Tracking (Video) - Manual Frame Processing
- OpenCV로 직접 비디오 프레임을 읽어서 손상된 프레임 스킵
- 각 프레임마다 YOLO tracking 수행
"""

import os
import cv2
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
VERSION = "v5-video-manual"
TRACK_PROJECT = f"track"
TRACK_NAME_PREFIX = f"yolo26s_{VERSION}"

# 에러 핸들링 설정
MAX_ERROR_DISPLAY = 10  # 최대 몇 개의 에러까지 출력할지
MAX_CONSECUTIVE_ERRORS = 50  # 연속 에러가 이 횟수를 넘으면 종료
# ================================


def run_tracking_manual(model, video_path):
    """
    OpenCV로 직접 프레임을 읽어서 tracking 수행
    
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
    
    # 출력 디렉토리 설정
    output_dir = Path(f"{TRACK_PROJECT}/{TRACK_NAME_PREFIX}/{video_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    labels_dir = output_dir / "labels"
    labels_dir.mkdir(exist_ok=True)
    
    print("\n" + "=" * 70)
    print(f"Manual Tracking 시작: {video_name}")
    print("=" * 70)
    print(f"비디오 파일: {video_path}")
    print(f"출력 디렉토리: {output_dir}")
    print()
    
    # OpenCV로 비디오 열기
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[Error] 비디오를 열 수 없습니다: {video_path}")
        return
    
    # 비디오 정보
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"비디오 정보:")
    print(f"  - 총 프레임: {total_frames}")
    print(f"  - FPS: {fps:.2f}")
    print(f"  - 해상도: {width}x{height}")
    print(f"Confidence threshold: {CONF_THRESHOLD}")
    print(f"IoU threshold: {IOU_THRESHOLD}")
    print(f"Tracker: {TRACKER_TYPE}")
    print()
    
    # 비디오 writer 설정 (결과 비디오 저장)
    output_video_path = output_dir / f"{video_name}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out_video = cv2.VideoWriter(
        str(output_video_path),
        fourcc,
        fps,
        (width, height)
    )
    
    frame_count = 0
    processed_count = 0
    read_error_count = 0
    process_error_count = 0
    consecutive_errors = 0
    track_ids_seen = set()
    
    print("처리 중...")
    
    while True:
        # 프레임 읽기
        ret, frame = cap.read()
        
        if not ret:
            # 프레임 읽기 실패
            read_error_count += 1
            consecutive_errors += 1
            
            if consecutive_errors <= MAX_ERROR_DISPLAY:
                print(f"  ⚠️  프레임 {frame_count} 읽기 실패 (스킵)")
            elif consecutive_errors == MAX_ERROR_DISPLAY + 1:
                print(f"  ⚠️  너무 많은 에러 발생, 이후 에러는 카운트만 수행...")
            
            # 연속 에러가 너무 많으면 비디오가 끝난 것으로 간주
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(f"\n⚠️  연속 {MAX_CONSECUTIVE_ERRORS}개 프레임 읽기 실패")
                print(f"비디오 끝 또는 심각한 손상으로 판단하여 종료합니다.")
                break
            
            # 다음 프레임 시도
            frame_count += 1
            continue
        
        # 프레임 읽기 성공
        frame_count += 1
        consecutive_errors = 0  # 연속 에러 카운터 리셋
        
        try:
            # YOLO tracking 수행
            results = model.track(
                frame,
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD,
                persist=True,
                tracker=TRACKER_TYPE,
                verbose=False,  # 프레임별 로그 끄기
            )
            
            if results and len(results) > 0:
                result = results[0]
                
                # Track ID 수집
                if result.boxes and hasattr(result.boxes, 'id') and result.boxes.id is not None:
                    ids = result.boxes.id.int().cpu().tolist()
                    track_ids_seen.update(ids)
                    
                    # 라벨 파일 저장 (YOLO format with track ID)
                    label_file = labels_dir / f"{video_name}_{frame_count}.txt"
                    with open(label_file, 'w') as f:
                        boxes = result.boxes
                        for i in range(len(boxes)):
                            # class_id, x_center, y_center, width, height, track_id, confidence
                            cls = int(boxes.cls[i])
                            xywhn = boxes.xywhn[i]  # normalized
                            track_id = int(boxes.id[i]) if boxes.id is not None else -1
                            conf = float(boxes.conf[i])
                            
                            f.write(f"{cls} {xywhn[0]:.6f} {xywhn[1]:.6f} "
                                   f"{xywhn[2]:.6f} {xywhn[3]:.6f} {track_id} {conf:.6f}\n")
                
                # 시각화된 프레임
                annotated = result.plot(
                    line_width=1,
                    conf=True,
                    labels=True,
                )
                
                # 이미지 저장
                img_path = output_dir / f"{video_name}_{frame_count}.jpg"
                cv2.imwrite(str(img_path), annotated)
                
                # 비디오에 저장
                out_video.write(annotated)
                
                processed_count += 1
                
        except Exception as e:
            process_error_count += 1
            if process_error_count <= MAX_ERROR_DISPLAY:
                print(f"  ⚠️  프레임 {frame_count} 처리 중 에러: {e}")
            elif process_error_count == MAX_ERROR_DISPLAY + 1:
                print(f"  ⚠️  너무 많은 처리 에러 발생, 이후 에러는 카운트만 수행...")
            continue
        
        # 진행 상황 출력 (100 프레임마다)
        if frame_count % 100 == 0:
            print(f"  {frame_count} 프레임 처리 완료... (성공: {processed_count})")
    
    # 정리
    cap.release()
    out_video.release()
    
    print()
    print("=" * 70)
    print("Tracking 완료!")
    print("=" * 70)
    print(f"총 시도 프레임: {frame_count}")
    print(f"✓ 정상 처리: {processed_count}")
    
    if read_error_count > 0 or process_error_count > 0:
        print(f"⚠️  읽기 실패: {read_error_count}")
        print(f"⚠️  처리 실패: {process_error_count}")
    
    print(f"고유 Track ID 수: {len(track_ids_seen)}")
    print()
    print(f"📁 결과 저장 위치:")
    print(f"   - 이미지: {output_dir}/")
    print(f"   - 비디오: {output_video_path}")
    print(f"   - 라벨: {labels_dir}/")
    print("=" * 70)


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("YOLOv26s Vehicle Tracking (Manual Frame Processing)")
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
    
    # Step 2: Manual Tracking 수행
    print("[Step 2] Manual Frame Processing Tracking")
    print("-" * 70)
    
    run_tracking_manual(model, VIDEO_PATH)
    
    print("\n✓ 모든 작업 완료!")


if __name__ == '__main__':
    main()

