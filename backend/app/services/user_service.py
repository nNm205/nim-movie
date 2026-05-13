from fastapi import HTTPException, status 
from sqlalchemy import select 
from sqlalchemy.orm import Session 
from app.models.user import User 
from app.schemas.user import UserResponse, UserUpdate
from app.core.logger import logger

def get_user_profile(user: User) -> UserResponse:
    logger.info(f"Fetching profile for user_id={user.id}")

    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role 
    )

def update_user_profile(
    user: User,
    data: UserUpdate,
    db: Session
) -> UserResponse:
    logger.info(f"Update profile for user_id={user.id}")

    # Check email conflict 
    if data.email and data.email != user.email:
        logger.info(f"Checking email conflict: user_id={user.id}, new_email={data.email}")

        result = db.execute(
            select(User).where(
                User.email == data.email 
            )
        )

        existing = result.scalar_one_or_none()
        if existing: 
            logger.warning(f"Email update conflict: email={data.email} already exists (user_id={user.id})")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        user.email = data.email 
        
        logger.info(f"Email updated successfully for user_id={user.id}")

    # Check username conflict
    if data.username and data.username != user.username:
        logger.info(f"Checking username conflict: user_id={user.id}, new_username={data.username}")

        result = db.execute(
            select(User).where(
                User.username == data.username
            )
        )

        existing = result.scalar_one_or_none()
        if existing:
            logger.warning(f"Username update conflict: username={data.username} already exists (user_id={user.id})")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        user.username = data.username

        logger.info(f"Username updated successfully for user_id={user.id}")

    
    db.commit()
    db.refresh(user)

    logger.info(f"User profile updated successfully user_id={user.id}")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role 
    )