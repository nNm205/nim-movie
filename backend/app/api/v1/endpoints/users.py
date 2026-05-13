from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User

from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import (
    get_user_profile,
    update_user_profile
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/profile", 
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return get_user_profile(current_user)

@router.put(
    "/profile", 
    response_model=UserResponse
)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    return update_user_profile(
        user=current_user, 
        data=data, 
        db=db
    )
