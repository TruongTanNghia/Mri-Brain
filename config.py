import os
from pathlib import Path
from dotenv import load_dotenv

# load .env (nếu bạn dùng file .env)
load_dotenv()

# ========= CONFIG =========
# Thay đổi nếu cần hoặc set environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")    # để trống nếu không dùng GPT
MODEL_PATH     = os.getenv("MODEL_PATH", "best.pt") # đường dẫn tới file .pt của bạn
TMP_UPLOAD_DIR = Path(os.getenv("TMP_UPLOAD_DIR", "tmp"))
TMP_UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# Server config (tuỳ chọn)
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
