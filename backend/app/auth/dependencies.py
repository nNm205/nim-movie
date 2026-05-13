from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.security import decode_access_token
from app.database.session import get_db
from app.models.user import User 
from app.core.logger import logger

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User: 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    ) 

    payload = decode_access_token(token)

    if payload is None:
        logger.warning("Authentication failed - invalid token")
        raise credentials_exception
    
    user_id = payload.get("user_id")
    if user_id is None: 
        logger.warning("Authentication failed - missing user_id in token")
        raise credentials_exception
    
    result = db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalar_one_or_none()
    if user is None:
        logger.warning(f"Authentication failed - user not found: {user_id}")
        raise credentials_exception
    
    logger.info(f"Authenticated user: {user.email}")

    return user 

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    logger.info(f"Admin access check for user_id={current_user.id}, role={current_user.role}")

    if current_user.role != "admin":
        logger.warning(f"Forbidden admin access attempt - user_id={current_user.id}, role={current_user.role}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger.info(f"Admin access granted for user_id={current_user.id}")
    return current_user 