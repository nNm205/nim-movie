from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session
from app.database.session import get_db

from app.schemas.user import (
    TokenResponse,
    UserRegister
)

from app.services.auth_service import register_user 

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register", 
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
) -> TokenResponse:
    return register_user(
        user_data=user_data, 
        db=db 
)