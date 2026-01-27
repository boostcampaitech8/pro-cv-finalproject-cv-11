#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv26s 추론 테스트 스크립트
- pretrained YOLOv26s backbone 사용
- head는 vehicle 단일 클래스로 초기화
- 학습 없이 추론만 수행
"""

import os
import cv2
import random
from pathlib import Path
from ultralytics import YOLO
# from ultralytics.yolo.engine.model import DetectionHead


def load_model():
    """
    YOLOv26s pretrained 모델 로드 및 vehicle 단일 클래스로 초기화
    """
    print("=" * 60)
    print("YOLOv26s 모델 로드 중...")
    print("=" * 60)
    
    # YOLOv26s pretrained 모델 로드
    model = YOLO('yolo26s.pt') 


    # 실패
    # model.nc = 1
    # model.names = ['vehicle']

    # # head 새로 초기화 (pretrained backbone 유지)
    # model.model.head = DetectionHead(
    #     model.model.backbone,  # backbone 그대로 사용
    #     nc=model.nc,
    #     anchors=model.model.head.anchors,
    # )   


    # 모델 정보 출력
    print(f"모델 로드 완료: {model.model_name}")
    print(f"클래스 수: 1 (vehicle)")
    print()
    
    return model


def get_sample_images(image_dir, num_samples=3):
    """
    이미지 디렉토리에서 샘플 이미지 선택
    
    Args:
        image_dir: 이미지 디렉토리 경로
        num_samples: 샘플 수
        
    Returns:
        list: 샘플 이미지 경로 리스트
    """
    image_dir = Path(image_dir)
    
    if not image_dir.exists():
        print(f"[Error] 이미지 디렉토리가 존재하지 않습니다: {image_dir}")
        return []
    
    # jpg 파일 찾기
    image_files = list(image_dir.glob('*.jpg'))
    
    if not image_files:
        print(f"[Error] 이미지 파일을 찾을 수 없습니다: {image_dir}")
        return []
    
    # 랜덤 샘플링
    num_samples = min(num_samples, len(image_files))
    sample_images = random.sample(image_files, num_samples)
    
    print(f"총 {len(image_files)}개 이미지 중 {num_samples}개 샘플 선택:")
    for img_path in sample_images:
        print(f"  - {img_path.name}")
    print()
    
    return sample_images


def run_inference(model, image_path, save_dir):
    """
    단일 이미지에 대해 추론 수행
    
    Args:
        model: YOLO 모델
        image_path: 이미지 경로
        save_dir: 결과 저장 디렉토리
    """
    print(f"추론 중: {image_path.name}")
    print("-" * 60)
    
    # 추론 수행
    results = model.predict(
        source=str(image_path),
        save=True,  # 결과 이미지 저장
        save_txt=True,  # 결과 텍스트 저장
        conf=0.25,  # confidence threshold
        iou=0.45,  # NMS IoU threshold
        project=save_dir,
        name='inference',
        exist_ok=True,
    )
    
    # 결과 분석
    result = results[0]  # 첫 번째 (유일한) 결과
    
    # Detection 결과 출력
    boxes = result.boxes
    num_detections = len(boxes)
    
    print(f"감지된 객체 수: {num_detections}")
    
    if num_detections > 0:
        for i, box in enumerate(boxes):
            # Bounding box 좌표 (xyxy 형식)
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = xyxy
            
            # Confidence
            conf = box.conf[0].cpu().numpy()
            
            # Class
            cls = int(box.cls[0].cpu().numpy())
            class_name = result.names[cls] if cls < len(result.names) else 'vehicle'
            
            print(f"  [{i+1}] {class_name}")
            print(f"      bbox: ({x1:.1f}, {y1:.1f}) - ({x2:.1f}, {y2:.1f})")
            print(f"      confidence: {conf:.3f}")
    else:
        print("  감지된 객체가 없습니다.")
    
    print()
    
    return result


def visualize_result(result, image_path, save_dir):
    """
    추론 결과를 이미지에 시각화하여 파일로 저장
    
    Args:
        result: YOLO 추론 결과
        image_path: 원본 이미지 경로
        save_dir: 저장 디렉토리
    """
    # 결과 이미지 가져오기 (annotated image)
    img_with_boxes = result.plot()
    
    # 저장 경로 설정
    output_dir = Path(save_dir) / 'visualized'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{image_path.stem}_result.jpg"
    
    # 이미지 저장
    cv2.imwrite(str(output_path), img_with_boxes)
    
    print(f"✓ 시각화 결과 저장: {output_path}")
    print()


def main():
    """메인 실행 함수"""
    # 경로 설정
    train_image_dir = '/data/ephemeral/home/dataset/flatten_road_dataset_bb/train/images'
    val_image_dir = '/data/ephemeral/home/dataset/flatten_road_dataset_bb/val/images'
    save_dir = './inference_results'
    
    # 저장 디렉토리 생성
    os.makedirs(save_dir, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("YOLOv26s Vehicle Detection 추론 테스트")
    print("=" * 60)
    print()
    
    # 모델 로드
    model = load_model()
    
    # 샘플 이미지 선택 (train 폴더에서)
    sample_images = get_sample_images(train_image_dir, num_samples=3)
    
    if not sample_images:
        print("[Error] 샘플 이미지를 찾을 수 없습니다.")
        return
    
    print("=" * 60)
    print("추론 시작")
    print("=" * 60)
    print()
    
    # 각 샘플 이미지에 대해 추론 수행
    for i, image_path in enumerate(sample_images, 1):
        print(f"[{i}/{len(sample_images)}] 처리 중...")
        
        # 추론 수행
        result = run_inference(model, image_path, save_dir)
        
        # 결과 시각화 (파일로 저장)
        visualize_result(result, image_path, save_dir)
    
    print("=" * 60)
    print("추론 완료!")
    print(f"결과 저장 위치:")
    print(f"  - YOLO 결과 이미지: {save_dir}/inference/*.jpg")
    print(f"  - YOLO 결과 텍스트: {save_dir}/inference/labels/*.txt")
    print(f"  - 시각화 이미지: {save_dir}/visualized/*_result.jpg")
    print("=" * 60)


if __name__ == '__main__':
    main()

