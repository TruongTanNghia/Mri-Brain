import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app_routes import ui, analyze  # đổi routes → app_routes

app = FastAPI(title="Fabric Classifier + Tips")

Path("static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(ui.router)
app.include_router(analyze.router)
@app.get("/")
def home():
    return {
        "message": "🚀 Fabric Classifier API is running!",
        "routes": ["/ui", "/analyze"]
    }