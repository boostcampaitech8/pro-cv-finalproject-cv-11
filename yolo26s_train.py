#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv26s Vehicle Detection - Training
- pretrained YOLOv26s를 vehicle 데이터셋으로 파인튜닝
"""

import os
from ultralytics import YOLO
import wandb
from dotenv import load_dotenv

# ========== 설정 변수 ==========
# 모델 및 데이터셋 설정
# MODEL_WEIGHT = "./models/yolo26s/yolo26s.pt"
MODEL_WEIGHT = "./yolo26l.pt"
DATASET_CONFIG = "models/yolo26s/vehicle_dataset.yaml"
TRAIN_IMAGE_DIR = "/data/ephemeral/home/dataset/flatten_road_dataset_bb/train/images"
VAL_IMAGE_DIR = "/data/ephemeral/home/dataset/flatten_road_dataset_bb/val/images"

# 학습 설정
EPOCHS = 40
IMAGE_SIZE = (640, 640)
BATCH_SIZE = 40
USE_AMP = True
SEED = 42

# 저장 경로 설정
TRAIN_PROJECT = "cv-11-final"
VERSION="v1"
# TRAIN_NAME = f"train_yolo26s_{VERSION}"
TRAIN_NAME = f"yolo26l_{VERSION}_e{EPOCHS}_b{BATCH_SIZE}"

# Wandb 설정
load_dotenv()
WANDB_API_KEY = os.getenv('WANDB_API_KEY')
os.environ["WANDB_ENTITY"] = "cv_11"
os.environ["WANDB_API_KEY"] = WANDB_API_KEY
wandb.login()

# WANDB_PROJECT = "cv-11-final"
# WANDB_ENTITY = "cv_11"  # 팀 이름 (본인 팀에 맞게 수정)
# WANDB_RUN_NAME = f"yolo26s_{VERSION}_e{EPOCHS}_b{BATCH_SIZE}"  # 간단한 run name

# ================================


def main():
    """메인 실행 함수"""
    
    print("=" * 70)
    print("YOLOv26s Vehicle Detection - Training")
    print("=" * 70)
    print()
    
    # # ========== Wandb 초기화 ==========
    # print("[Wandb] 초기화 중...")
    # wandb_run = wandb.init(
    #     project=WANDB_PROJECT,
    #     entity=WANDB_ENTITY,
    #     name=WANDB_RUN_NAME,
    #     config={
    #         "model": "YOLOv26s",
    #         "dataset": "flatten_road_dataset_bb",
    #         "epochs": EPOCHS,
    #         "batch_size": BATCH_SIZE,
    #         "image_size": IMAGE_SIZE,
    #         "lr0": 0.01,  # YOLO 기본값
    #         "amp": USE_AMP,
    #         "seed": SEED,
    #     }
    # )
    # print(f"✓ Wandb 초기화 완료: {WANDB_PROJECT}/{WANDB_RUN_NAME}")
    # print()
    
    # ========== Step 1: 모델 로드 ==========
    print("[Step 1] Pretrained YOLOv26s 모델 로드")
    print("-" * 70)
    
    model = YOLO(MODEL_WEIGHT)
    print(f"✓ 모델 로드 완료: {model.model_name}")
    print()
    
    # ========== Step 2: Training ==========
    print(f"[Step 2] Vehicle 데이터셋으로 Fine-tuning ({EPOCHS} epoch)")
    print("-" * 70)
    print(f"데이터셋: {DATASET_CONFIG}")
    print(f"Epochs: {EPOCHS}")
    print(f"Image size: {IMAGE_SIZE}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Train 데이터: {TRAIN_IMAGE_DIR}")
    print(f"Validation 데이터: {VAL_IMAGE_DIR}")
    print("※ Validation은 학습 중 자동으로 수행됩니다.")
    print()
    
    # vehicle dataset으로 파인튜닝
    train_results = model.train(
        data=DATASET_CONFIG,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        project=TRAIN_PROJECT,
        name=TRAIN_NAME,
        exist_ok=True,
        pretrained=True,  # pretrained weight 유지
        verbose=True,
        amp=USE_AMP,
        seed=SEED,
    )
    
    print()
    print("=" * 70)
    print("학습 완료!")
    print("=" * 70)
    print()
    print("📁 저장된 파일:")
    print(f"  - 모델 가중치: {TRAIN_PROJECT}/{TRAIN_NAME}/weights/best.pt")
    print(f"  - 학습 로그: {TRAIN_PROJECT}/{TRAIN_NAME}/")
    print(f"  - Validation 결과: {TRAIN_PROJECT}/{TRAIN_NAME}/val_*.jpg")
    print()
    print("💡 추론을 수행하려면 다음 명령을 실행하세요:")
    print(f"   python yolo26s_inference.py")
    print()
    print("=" * 70)
    
    # # Wandb 종료
    # wandb.finish()
    # print("\n✓ Wandb 로깅 완료")


if __name__ == '__main__':
    main()

