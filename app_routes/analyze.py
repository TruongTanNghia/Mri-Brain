from fastapi import APIRouter

router = APIRouter()

@router.get("/analyze")
def analyze_page():
    return {"message": "Analyze route is active!"}
