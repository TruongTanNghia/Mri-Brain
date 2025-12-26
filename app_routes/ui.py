from fastapi import APIRouter

router = APIRouter()

@router.get("/ui")
def ui_page():
    return {"message": "UI route is working!"}
