from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.watchlist import WatchlistListResponse 
from app.services.watchlist_service import (
    add_to_watchlist,
    get_user_watchlist,
    remove_from_watchlist
)
from app.core.logger import logger 

router = APIRouter(prefix="/users", tags=["Watchlist"])

@router.get(
    "/watchlist",
    response_model=WatchlistListResponse
)
def user_watchlist(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WatchlistListResponse:
    logger.info(
        f"Fetching watchlist | user_id={current_user.id} | page={page}"
    )

    result = get_user_watchlist(
        user_id=current_user.id,
        db=db,
        page=page,
        page_size=pageSize
    )

    logger.info(
        f"Watchlist fetched successfully | user_id={current_user.id}"
    )

    return result 

@router.post(
    "/watchlist/{movie_id}",
    status_code=status.HTTP_201_CREATED
)
def add_movie(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(
        f"Adding movie to watchlist | user_id={current_user.id} | movie_id={movie_id}"
    )

    try:
        add_to_watchlist(
            current_user.id,
            movie_id,
            db
        )

        logger.info(
            f"Movie added to watchlist successfully | user_id={current_user.id} | movie_id={movie_id}"
        )

        return {
            "movieId": movie_id,
            "message": "Added to watchlist"
        }

    except ValueError as e:
        logger.warning(
            f"Failed to add movie to watchlist | user_id={current_user.id} | movie_id={movie_id} | error={str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e: 
        logger.exception(
            f"Unexpected error while adding to watchlist | user_id={current_user.id} | movie_id={movie_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete(
    "/watchlist/{movie_id}"
)
def remove_movie(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(
        f"Removing movie from watchlist | user_id={current_user.id} | movie_id={movie_id}"
    )

    try:
        remove_from_watchlist(
            current_user.id,
            movie_id,
            db 
        ) 

        logger.info(
            f"Movie removed from watchlist successfully | user_id={current_user.id} | movie_id={movie_id}"
        )

        return {
            "message": "Removed from watchlist"
        }
    except ValueError as e:
        logger.warning(
            f"Movie not found in watchlist | user_id={current_user.id} | movie_id={movie_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        logger.exception(
            f"Unexpected error while removing from watchlist | user_id={current_user.id} | movie_id={movie_id}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )