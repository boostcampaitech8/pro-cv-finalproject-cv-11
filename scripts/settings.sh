source /data/ephemeral/home/py310/bin/activate
source /data/ephemeral/home/py310-jsw/bin/activate

pip install --upgrade pip
pip install jupyter ipykernel

# py310 가상환경도 여기까진 했음

# 여기서부턴 py310-jsw 가상환경만 함

deactivate

watch -n 1 nvidia-smi
watch -n 1 "df -h | grep -E '/data/ephemeral|Avail'"

pip install numpy==1.26.0
pip uninstall opencv-python
pip install opencv-python-headless
pip install ultralytics==8.4.7
pip install gdown
pip install python-dotenv
pip install wandb
yolo settings wandb=True
apt install tmux

# import cv2 에러 발생
apt update
apt install libxcb1
apt install libgl1-mesa-glx
apt install libglib2.0-0

pip install -U numpy==1.26.0