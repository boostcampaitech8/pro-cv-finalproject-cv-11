from ultralytics import YOLO

# pretrained YOLO26s 모델 로드
model = YOLO("yolo26s.pt")

# vehicle dataset으로 fine-tuning
results = model.train(
    data="models/yolo26s/vehicle_dataset.yaml",
    epochs=1,
    imgsz=(1920, 1080)
)


results = model.predict(
    source=(샘플 3개),
    conf=0.25,
    save=True,
    save_txt=True
)