from fastapi import APIRouter, Depends 
from app.auth.dependencies import get_current_admin
from app.models.user import User 

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def admin_dashboard(
    current_admin: User = Depends(get_current_admin)
):
    return {
        "message": f"Welcome admin {current_admin.username}"
    }