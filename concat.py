#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Concatenation Tool
- Tracking/Inference 결과 이미지들을 2x3 그리드로 concat
- 시퀀스별로 정리하여 선택 가능
"""

import os
import re
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict


# ========== 설정 변수 ==========
# 입력 경로 (None이면 대화형으로 입력)
INPUT_PATH = None  # 예: "runs/detect/track/yolo26s_v5/20201019_161210"

# Concat 설정
GRID_SIZE = (2, 3)  # (rows, cols) = 세로 2, 가로 3
# ================================


def find_sequences_in_path(input_path):
    """
    경로에서 이미지 시퀀스 찾기
    
    Args:
        input_path: 입력 경로
        
    Returns:
        dict: {timestamp: [image_paths]}
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"[Error] 경로가 존재하지 않습니다: {input_path}")
        return {}
    
    # jpg 파일 찾기
    images = sorted(input_path.glob("**/*.jpg"))
    
    if not images:
        print(f"[Error] 이미지 파일을 찾을 수 없습니다: {input_path}")
        return {}
    
    # 시퀀스별로 그룹화
    sequences = defaultdict(list)
    pattern = re.compile(r'.*_(\d{8}_\d{6})_(\d+)\.jpg')
    
    for img in images:
        match = pattern.match(img.name)
        if match:
            timestamp = match.group(1)
            frame_num = match.group(2)
            sequences[timestamp].append((frame_num, str(img)))
    
    # 프레임 번호 순으로 정렬
    for timestamp in sequences:
        sequences[timestamp] = [path for _, path in sorted(sequences[timestamp])]
    
    return dict(sequences)


def display_sequences(sequences):
    """
    사용 가능한 시퀀스 목록 출력
    
    Args:
        sequences: 시퀀스 딕셔너리
        
    Returns:
        list: 정렬된 timestamp 리스트
    """
    print("\n" + "=" * 70)
    print("사용 가능한 이미지 시퀀스")
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
    시퀀스 선택
    
    Args:
        sequences: 시퀀스 딕셔너리
        
    Returns:
        tuple: (timestamp, image_paths)
    """
    sorted_keys = display_sequences(sequences)
    
    while True:
        try:
            choice = input(f"\nConcat할 시퀀스 번호를 입력하세요 (1-{len(sorted_keys)}): ")
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


def select_frames(images, grid_size):
    """
    Concat할 프레임 선택
    
    Args:
        images: 이미지 경로 리스트
        grid_size: (rows, cols)
        
    Returns:
        list: 선택된 이미지 경로 리스트
    """
    rows, cols = grid_size
    total_needed = rows * cols
    
    print("\n" + "=" * 70)
    print(f"프레임 선택 (2x3 = 6개 이미지)")
    print("=" * 70)
    print(f"총 {len(images)}개 프레임 사용 가능")
    print(f"선택할 프레임 수: {total_needed}개")
    print()
    
    # 사용 가능한 프레임 범위 표시
    sample_count = min(10, len(images))
    print("프레임 예시 (처음 10개):")
    for i in range(sample_count):
        img_name = Path(images[i]).name
        print(f"  [{i:3d}] {img_name}")
    if len(images) > sample_count:
        print(f"  ... (총 {len(images)}개)")
    print()
    
    while True:
        try:
            start_idx = int(input(f"시작 프레임 번호를 입력하세요 (0-{len(images) - total_needed}): "))
            
            if 0 <= start_idx <= len(images) - total_needed:
                selected_images = images[start_idx:start_idx + total_needed]
                
                print(f"\n✓ 선택된 프레임:")
                for i, img_path in enumerate(selected_images):
                    print(f"  [{i+1}] {Path(img_path).name}")
                
                confirm = input(f"\n이 프레임들을 concat하시겠습니까? (y/n): ")
                if confirm.lower() == 'y':
                    return selected_images
            else:
                print(f"[Error] 0에서 {len(images) - total_needed} 사이의 숫자를 입력하세요.")
        except ValueError:
            print("[Error] 올바른 숫자를 입력하세요.")
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            exit(0)


def concat_images(image_paths, grid_size):
    """
    이미지들을 그리드로 concat
    
    Args:
        image_paths: 이미지 경로 리스트
        grid_size: (rows, cols)
        
    Returns:
        numpy.ndarray: concat된 이미지
    """
    rows, cols = grid_size
    
    # 이미지 로드
    images = []
    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"[Warning] 이미지 로드 실패: {img_path}")
            continue
        images.append(img)
    
    if len(images) != rows * cols:
        print(f"[Error] 로드된 이미지 수({len(images)})가 필요한 수({rows * cols})와 다릅니다.")
        return None
    
    # 이미지 크기 확인 (첫 번째 이미지 기준)
    h, w = images[0].shape[:2]
    
    # 모든 이미지를 동일한 크기로 resize
    resized_images = []
    for img in images:
        if img.shape[:2] != (h, w):
            img = cv2.resize(img, (w, h))
        resized_images.append(img)
    
    # 그리드로 배치
    grid_rows = []
    for i in range(rows):
        row_images = resized_images[i * cols:(i + 1) * cols]
        row = np.hstack(row_images)
        grid_rows.append(row)
    
    # 최종 concat
    result = np.vstack(grid_rows)
    
    return result


def generate_output_filename(image_paths, timestamp):
    """
    출력 파일명 생성
    
    Args:
        image_paths: 이미지 경로 리스트
        timestamp: 시퀀스 timestamp
        
    Returns:
        str: 출력 파일명
    """
    # 시작 프레임과 끝 프레임 번호 추출
    pattern = re.compile(r'.*_\d{8}_\d{6}_(\d+)\.jpg')
    
    first_match = pattern.match(Path(image_paths[0]).name)
    last_match = pattern.match(Path(image_paths[-1]).name)
    
    if first_match and last_match:
        first_frame = first_match.group(1)
        last_frame = last_match.group(1)
        
        # 파일명 prefix 추출 (예: 3_)
        prefix = Path(image_paths[0]).name.split('_')[0]
        
        return f"{prefix}_{timestamp}_{first_frame}-{last_frame}.jpg"
    
    return f"concat_{timestamp}.jpg"


def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("Image Concatenation Tool")
    print("=" * 70)
    print()
    
    # Step 1: 입력 경로 설정
    print("[Step 1] 입력 경로 설정")
    print("-" * 70)
    
    if INPUT_PATH:
        input_path = INPUT_PATH
        print(f"사전 지정된 경로: {input_path}")
    else:
        input_path = input("이미지가 있는 경로를 입력하세요: ").strip()
    
    # 원본 이미지 경로 저장
    original_path = Path(input_path)
    
    print(f"✓ 경로: {input_path}")
    print()
    
    # Step 2: 시퀀스 찾기
    print("[Step 2] 이미지 시퀀스 탐색")
    print("-" * 70)
    
    sequences = find_sequences_in_path(input_path)
    
    if not sequences:
        print("[Error] 시퀀스를 찾을 수 없습니다.")
        return
    
    print(f"✓ {len(sequences)}개의 시퀀스를 찾았습니다.")
    
    # Step 3: 시퀀스 선택
    print("\n[Step 3] 시퀀스 선택")
    print("-" * 70)
    
    timestamp, images = select_sequence(sequences)
    
    # Step 4: 프레임 선택
    print("\n[Step 4] 프레임 선택")
    print("-" * 70)
    
    selected_images = select_frames(images, GRID_SIZE)
    
    # Step 5: Concat 수행
    print("\n[Step 5] Concat 수행")
    print("-" * 70)
    print(f"그리드 크기: {GRID_SIZE[0]}x{GRID_SIZE[1]} (세로x가로)")
    print("처리 중...")
    
    result = concat_images(selected_images, GRID_SIZE)
    
    if result is None:
        print("[Error] Concat 실패")
        return
    
    print(f"✓ Concat 완료! 크기: {result.shape[1]}x{result.shape[0]}")
    
    # Step 6: 저장
    print("\n[Step 6] 결과 저장")
    print("-" * 70)
    
    # 저장 디렉토리는 원본 이미지 경로와 동일
    output_dir = original_path
    
    # 파일명 생성
    output_filename = generate_output_filename(selected_images, timestamp)
    output_path = output_dir / output_filename
    
    # 저장
    cv2.imwrite(str(output_path), result)
    
    print(f"✓ 저장 완료!")
    print(f"   파일: {output_path}")
    print(f"   크기: {result.shape[1]}x{result.shape[0]}")
    print()
    print("=" * 70)
    print("모든 작업 완료!")
    print("=" * 70)


if __name__ == '__main__':
    main()

