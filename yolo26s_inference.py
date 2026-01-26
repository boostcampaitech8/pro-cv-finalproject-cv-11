#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv26s Vehicle Detection - Inference
- Fine-tuned vehicle detection 모델로 추론 수행
- 이미지 시퀀스를 시간별로 그룹화하여 선택 후 추론
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from ultralytics import YOLO


# ========== 설정 변수 ==========
# 모델 설정
MODEL_WEIGHT = "runs/detect/cv-11-final/yolo26s_v4-2_e1_b64/weights/best.pt"  # 학습된 모델 경로

# 데이터 경로
IMAGE_DIR = "/data/ephemeral/home/dataset/flatten_road_dataset_bb/val/images"

# 추론 설정
CONF_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45

# 저장 경로
VERSION = "v4-2"
INFERENCE_PROJECT = "inference"
INFERENCE_NAME_PREFIX = f"yolo26s_{VERSION}"

# 시퀀스 선택 (None이면 대화형으로 선택)
SELECTED_SEQUENCE = None  # 예: "20201019_161210" 또는 None
# ================================


def find_sequences(image_dir):
    """
    이미지 디렉토리에서 시퀀스별로 그룹화
    
    Args:
        image_dir: 이미지 디렉토리 경로
        
    Returns:
        dict: {timestamp: [image_paths]}
    """
    image_dir = Path(image_dir)
    
    if not image_dir.exists():
        print(f"[Error] 이미지 디렉토리가 존재하지 않습니다: {image_dir}")
        return {}
    
    # 모든 jpg 파일 찾기
    images = sorted(image_dir.glob("*.jpg"))
    
    if not images:
        print(f"[Error] 이미지 파일을 찾을 수 없습니다: {image_dir}")
        return {}
    
    # 시퀀스별로 그룹화
    sequences = defaultdict(list)
    pattern = re.compile(r'.*_(\d{8}_\d{6})_\d+\.jpg')
    
    for img in images:
        match = pattern.match(img.name)
        if match:
            timestamp = match.group(1)
            sequences[timestamp].append(str(img))
    
    return dict(sequences)


def display_sequences(sequences):
    """
    사용 가능한 시퀀스 목록 출력
    
    Args:
        sequences: 시퀀스 딕셔너리
    """
    print("\n" + "=" * 70)
    print("사용 가능한 비디오 시퀀스")
    print("=" * 70)
    
    sorted_keys = sorted(sequences.keys())
    
    for i, timestamp in enumerate(sorted_keys, 1):
        date = timestamp[:8]  # YYYYMMDD
        time = timestamp[9:]   # HHMMSS
        frame_count = len(sequences[timestamp])
        
        # 날짜와 시간 포맷팅
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        formatted_time = f"{time[:2]}:{time[2:4]}:{time[4:6]}"
        
        print(f"  [{i:2d}] {timestamp}")
        print(f"       날짜: {formatted_date}, 시간: {formatted_time}")
        print(f"       프레임 수: {frame_count}개")
        print()
    
    print("=" * 70)
    return sorted_keys


def select_sequence(sequences):
    """
    사용자에게 시퀀스 선택 요청
    
    Args:
        sequences: 시퀀스 딕셔너리
        
    Returns:
        tuple: (timestamp, image_paths)
    """
    sorted_keys = display_sequences(sequences)
    
    while True:
        try:
            choice = input(f"\n추론할 시퀀스 번호를 입력하세요 (1-{len(sorted_keys)}): ")
            idx = int(choice) - 1
            
            if 0 <= idx < len(sorted_keys):
                selected_timestamp = sorted_keys[idx]
                print(f"\n✓ 선택된 시퀀스: {selected_timestamp}")
                return selected_timestamp, sequences[selected_timestamp]
            else:
                print(f"[Error] 1에서 {len(sorted_keys)} 사이의 숫자를 입력하세요.")
        except ValueError:
            print("[Error] 올바른 숫자를 입력하세요.")
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            exit(0)


def run_inference(model, images, sequence_name):
    """
    선택한 시퀀스로 추론 수행
    
    Args:
        model: YOLO 모델
        images: 이미지 경로 리스트
        sequence_name: 시퀀스 이름 (timestamp)
    """
    print("\n" + "=" * 70)
    print(f"추론 시작: {sequence_name}")
    print("=" * 70)
    print(f"프레임 수: {len(images)}")
    print(f"Confidence threshold: {CONF_THRESHOLD}")
    print(f"IoU threshold: {IOU_THRESHOLD}")
    print()
    
    # 저장 경로 구성: inference/yolo26s_{VERSION}/{seq_name}
    project_path = f"{INFERENCE_PROJECT}/{INFERENCE_NAME_PREFIX}"
    
    # 추론 수행
    results = model.predict(
        source=images,
        conf=CONF_THRESHOLD,
        iou=IOU_THRESHOLD,
        save=True,  # 결과 이미지 저장
        save_txt=True,  # 결과 텍스트 저장
        project=project_path,
        name=sequence_name,
        exist_ok=True,
        stream=True,  # 메모리 효율적 처리
    )
    
    # 결과 처리 및 통계
    frame_count = 0
    total_detections = 0
    detections_per_frame = []
    
    for result in results:
        frame_count += 1
        num_boxes = len(result.boxes)
        total_detections += num_boxes
        detections_per_frame.append(num_boxes)
        
        # 진행 상황 출력 (100 프레임마다)
        if frame_count % 100 == 0:
            print(f"  처리 중... {frame_count}/{len(images)} 프레임")
    
    # 통계 계산
    avg_detections = total_detections / frame_count if frame_count > 0 else 0
    max_detections = max(detections_per_frame) if detections_per_frame else 0
    min_detections = min(detections_per_frame) if detections_per_frame else 0
    
    print()
    print("=" * 70)
    print("추론 완료!")
    print("=" * 70)
    print(f"총 처리 프레임: {frame_count}")
    print(f"총 검출된 vehicle 수: {total_detections}")
    print(f"프레임당 평균 검출 수: {avg_detections:.2f}")
    print(f"최대 검출 수 (1 프레임): {max_detections}")
    print(f"최소 검출 수 (1 프레임): {min_detections}")
    print()
    print(f"📁 결과 저장 위치:")
    print(f"   - 이미지: {INFERENCE_PROJECT}/{INFERENCE_NAME_PREFIX}/{sequence_name}/")
    print(f"   - 텍스트: {INFERENCE_PROJECT}/{INFERENCE_NAME_PREFIX}/{sequence_name}/labels/")
    print("=" * 70)


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("YOLOv26s Vehicle Detection - Inference")
    print("=" * 70)
    print()
    
    # Step 1: 모델 로드
    print("[Step 1] Fine-tuned 모델 로드")
    print("-" * 70)
    print(f"모델: {MODEL_WEIGHT}")
    
    if not os.path.exists(MODEL_WEIGHT):
        print(f"[Error] 모델 파일을 찾을 수 없습니다: {MODEL_WEIGHT}")
        print("먼저 yolo26s_train.py로 모델을 학습하세요.")
        return
    
    model = YOLO(MODEL_WEIGHT)
    print("✓ 모델 로드 완료")
    print()
    
    # Step 2: 시퀀스 찾기
    print("[Step 2] 이미지 시퀀스 탐색")
    print("-" * 70)
    
    sequences = find_sequences(IMAGE_DIR)
    
    if not sequences:
        print("[Error] 시퀀스를 찾을 수 없습니다.")
        return
    
    print(f"✓ {len(sequences)}개의 시퀀스를 찾았습니다.")
    
    # Step 3: 시퀀스 선택
    print("\n[Step 3] 시퀀스 선택")
    print("-" * 70)
    
    if SELECTED_SEQUENCE:
        # 설정 변수로 지정된 시퀀스 사용
        if SELECTED_SEQUENCE in sequences:
            timestamp = SELECTED_SEQUENCE
            images = sequences[timestamp]
            print(f"✓ 사전 선택된 시퀀스: {timestamp} ({len(images)} 프레임)")
        else:
            print(f"[Error] 지정된 시퀀스를 찾을 수 없습니다: {SELECTED_SEQUENCE}")
            print(f"사용 가능한 시퀀스: {list(sequences.keys())[:5]}...")
            return
    else:
        # 대화형으로 선택
        timestamp, images = select_sequence(sequences)
    
    # Step 4: 추론 수행
    run_inference(model, images, timestamp)
    
    print("\n✓ 모든 작업 완료!")


if __name__ == '__main__':
    main()

