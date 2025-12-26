from pathlib import Path
from typing import Dict, Optional
from model import MODEL

def predict_image(image_path: str) -> Dict[str, Optional[object]]:
    """
    Chạy model lên image_path, trả về dict:
    { "label": str, "confidence": float }
    """
    if MODEL is None:
        raise RuntimeError("Model chưa được load. Kiểm tra model.py và đường dẫn .pt")

    results = MODEL(str(image_path))
    if len(results) == 0:
        return {"label": "Unknown", "confidence": None}

    r = results[0]

    try:
        class_id = int(r.probs.top1)
        confidence = float(r.probs.top1conf.item())
    except Exception:
        # fallback nếu cấu trúc khác
        class_id = None
        confidence = None

    label = MODEL.names.get(class_id, "Unknown") if class_id is not None else "Unknown"

    return {"label": label, "confidence": confidence}
