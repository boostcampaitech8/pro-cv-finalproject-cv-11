from ultralytics import YOLO

# 1. YOLO 모델 불러오기 (pretrained backbone만)
# coco pretrained weight를 로드하지만 head는 nc=1로 새로 생성됨
model = YOLO('yolo26s.pt')  # small model 예시
model.model.nc = 1           # 클래스 수 1개
model.model.names = ['vehicle']  # 클래스 이름

# 2. Detection head 재초기화 (random init)
from ultralytics.yolo.utils.torch_utils import initialize_weights
initialize_weights(model.model.model[-1])  # 마지막 detection head 초기화

# 3. 테스트할 이미지
img_path = 'path/to/your/test_image.jpg'

# 4. 추론
results = model.predict(img_path, conf=0.3, imgsz=640)  # conf는 낮게 잡아서 테스트 가능
results.show()  # 화면에 결과 표시
