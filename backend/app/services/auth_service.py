from fastapi import HTTPException, status 
from sqlalchemy import select
from sqlalchemy.orm import Session  
from app.models.user import User 
from app.core.logger import logger 

from app.auth.security import (
    create_access_token, 
    hash_password,
    verify_password
)

from app.schemas.user import (
    TokenResponse, 
    UserRegister, 
    UserLogin,
    UserResponse
)

def register_user(
    user_data: UserRegister, 
    db: Session
) -> TokenResponse:
    logger.info(f"Register attempt for email: {user_data.email}")

    # Check existing email 
    result = db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = result.scalar_one_or_none()
    if existing_user: 
        logger.warning(f"Registration failed - email already exists: {user_data.email}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check existing username 
    result = db.execute(
        select(User).where(
            User.username == user_data.username
        )
    )

    existing_username = result.scalar_one_or_none()

    if existing_username:
        logger.warning(f"Registration failed - username already taken: {user_data.username}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    try: 
        hashed_password = hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.success(f"User registered successfully: {new_user.email}")

        access_token = create_access_token({
            "sub": new_user.email,
            "user_id": new_user.id,
        })

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                username=new_user.username,
                role=new_user.role 
            )
        )
    
    except Exception as e: 
        db.rollback()

        logger.error(f"Registration failed due to server error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 

def login_user(
    user_data: UserLogin,
    db: Session 
) -> TokenResponse:
    logger.info(f"Login attempt for email: {user_data.email}")

    # Find user by email 
    result = db.execute(
        select(User).where(
            User.email == user_data.email 
        )
    )

    user = result.scalar_one_or_none() 
    if not user: 
        logger.warning(f"Login failed - user not found: {user_data.email}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    is_valid_password = verify_password(user_data.password, user.hashed_password)

    if not is_valid_password:
        logger.warning(f"Login failed - invalid password for: {user_data.email}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.info(f"User logged in successfully: {user.email}")

    # Generate JWT token 
    access_token = create_access_token({
        "sub": user.email,
        "user_id": user.id 
    })

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role 
        )
    )