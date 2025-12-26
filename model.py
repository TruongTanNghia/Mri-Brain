from ultralytics import YOLO
from config import MODEL_PATH

# Load YOLO model 1 lần khi import module
# (Ultralytics sẽ tải model vào bộ nhớ, tránh load lặp khi có nhiều request)
try:
    MODEL = YOLO(MODEL_PATH)
    print(f"[model] Loaded YOLO model from: {MODEL_PATH}")
except Exception as e:
    MODEL = None
    print(f"[model] ERROR loading model: {e}\nMake sure MODEL_PATH points to a valid .pt file.")
