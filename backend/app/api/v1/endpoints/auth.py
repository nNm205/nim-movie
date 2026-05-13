from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session
from app.database.session import get_db

from app.schemas.user import (
    TokenResponse,
    UserRegister,
    UserLogin,
    UserResponse 
)

from app.services.auth_service import (
    register_user,
    login_user
) 

from app.models.user import User 
from app.auth.dependencies import get_current_user

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

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> TokenResponse:
    return login_user(
        user_data=user_data,
        db=db 
    )  

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username
    ) 