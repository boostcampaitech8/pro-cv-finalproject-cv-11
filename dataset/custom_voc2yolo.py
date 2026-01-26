#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOC XML annotation을 YOLO 형식으로 변환하는 스크립트
- Vehicle_* 클래스만 추출하여 vehicle (class_id=0)로 통일
- 다른 클래스는 모두 무시

사용법:
    python custom_voc2yolo.py

디렉토리 구조:
    /data/ephemeral/home/dataset/flatten_road_dataset_bb/
    ├── train/
    │   ├── voc_annotations/  (입력 XML 파일들)
    │   └── labels/           (출력 YOLO txt 파일들)
    └── val/
        ├── voc_annotations/
        └── labels/
"""

import os
import xml.etree.ElementTree as ET


def convert_voc_to_yolo(xml_path, output_txt_path):
    """
    하나의 VOC XML 파일을 YOLO 형식 txt 파일로 변환
    
    Args:
        xml_path: 입력 XML 파일 경로
        output_txt_path: 출력 txt 파일 경로
    """
    # XML 파싱
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # 이미지 크기 정보 추출
    size = root.find('size')
    if size is None:
        print(f"[Warning] {xml_path}에서 size 정보를 찾을 수 없습니다.")
        return
    
    img_width = int(size.find('width').text)
    img_height = int(size.find('height').text)
    
    # 출력할 라벨 정보 저장
    yolo_labels = []
    
    # 모든 object 순회
    for obj in root.iter('object'):
        # 클래스명 추출
        class_name = obj.find('name').text
        
        # Vehicle_* 클래스만 처리 (Vehicle_로 시작하는 경우, 대소문자 구분 없이)
        if not class_name.lower().startswith('vehicle_'):
            continue
        
        # bounding box 좌표 추출
        bbox = obj.find('bndbox')
        if bbox is None:
            continue
        
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)
        
        # 좌표 유효성 검증 (이미지 범위 내에 있는지 확인)
        if (xmin < 0 or xmax > img_width or 
            ymin < 0 or ymax > img_height or 
            xmin >= xmax or ymin >= ymax):
            print(f"[Warning] {xml_path}에서 잘못된 bbox 발견: ({xmin}, {ymin}, {xmax}, {ymax})")
            continue
        
        # YOLO 형식으로 변환: 중심점(x, y) + 너비, 높이 (정규화)
        x_center = ((xmin + xmax) / 2) / img_width
        y_center = ((ymin + ymax) / 2) / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height
        
        # vehicle 클래스 ID는 0
        class_id = 0
        
        # YOLO 형식: <class_id> <x_center> <y_center> <width> <height>
        yolo_labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    # 라벨 파일 저장 (vehicle 객체가 하나라도 있을 때만)
    if yolo_labels:
        with open(output_txt_path, 'w') as f:
            f.write('\n'.join(yolo_labels) + '\n')
        print(f"✓ {os.path.basename(output_txt_path)}: {len(yolo_labels)}개 vehicle 객체")
    else:
        # vehicle 객체가 없으면 빈 파일 생성
        with open(output_txt_path, 'w') as f:
            pass
        print(f"✓ {os.path.basename(output_txt_path)}: vehicle 객체 없음 (빈 파일 생성)")


def process_dataset_split(split_name, base_dir):
    """
    특정 데이터셋 분할(train/val)을 처리
    
    Args:
        split_name: 'train' 또는 'val'
        base_dir: 데이터셋 기본 경로
    """
    # 디렉토리 경로 설정
    voc_annotation_dir = os.path.join(base_dir, split_name, 'voc_annotations')
    output_label_dir = os.path.join(base_dir, split_name, 'labels')
    
    # voc_annotations 폴더 존재 확인
    if not os.path.exists(voc_annotation_dir):
        print(f"[Warning] '{voc_annotation_dir}' 폴더가 존재하지 않습니다. 건너뜁니다.")
        return 0
    
    # labels 폴더 생성 (없으면)
    if not os.path.exists(output_label_dir):
        os.makedirs(output_label_dir)
        print(f"'{output_label_dir}' 폴더를 생성했습니다.")
    
    # voc_annotations 폴더 내 모든 XML 파일 찾기
    xml_files = [f for f in os.listdir(voc_annotation_dir) if f.endswith('.xml')]
    
    if not xml_files:
        print(f"[Warning] '{voc_annotation_dir}' 폴더에 XML 파일이 없습니다.")
        return 0
    
    print(f"\n[{split_name.upper()}] 총 {len(xml_files)}개의 XML 파일을 변환합니다.\n")
    
    # 각 XML 파일 처리
    success_count = 0
    for xml_file in sorted(xml_files):
        xml_path = os.path.join(voc_annotation_dir, xml_file)
        
        try:
            # XML에서 이미지 파일명 추출
            tree = ET.parse(xml_path)
            root = tree.getroot()
            filename_elem = root.find('filename')
            
            if filename_elem is not None and filename_elem.text:
                # 이미지 파일명에서 확장자를 .txt로 변경
                image_filename = filename_elem.text
                txt_filename = os.path.splitext(image_filename)[0] + '.txt'
            else:
                # filename 태그가 없으면 XML 파일명을 사용
                txt_filename = os.path.splitext(xml_file)[0] + '.txt'
            
            output_txt_path = os.path.join(output_label_dir, txt_filename)
            
            # 변환 수행
            convert_voc_to_yolo(xml_path, output_txt_path)
            success_count += 1
            
        except Exception as e:
            print(f"[Error] {xml_file} 변환 중 오류 발생: {str(e)}")
    
    print(f"\n[{split_name.upper()}] 변환 완료! {success_count}/{len(xml_files)}개 파일 처리됨.")
    return success_count


def main():
    """메인 실행 함수"""
    # 데이터셋 기본 경로 설정 (절대 경로)
    base_dir = '/data/ephemeral/home/dataset/flatten_road_dataset_bb'
    
    if not os.path.exists(base_dir):
        print(f"[Error] '{base_dir}' 폴더가 존재하지 않습니다.")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        return
    
    print("=" * 60)
    print("VOC → YOLO 변환 스크립트")
    print("Vehicle_* 클래스만 추출 (class_id=0)")
    print("=" * 60)
    print(f"데이터셋 경로: {base_dir}")
    
    # train과 val 데이터셋 처리
    total_success = 0
    for split in ['train', 'val']:
        total_success += process_dataset_split(split, base_dir)
    
    print("\n" + "=" * 60)
    print(f"전체 변환 완료! 총 {total_success}개 파일 처리됨.")
    print("=" * 60)


if __name__ == '__main__':
    main()

