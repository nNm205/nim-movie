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
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    MovieReviewsResponse,
    UserReviewsResponse
)

from app.services.review_service import (
    create_review,
    get_movie_reviews,
    update_review,
    delete_review,
    get_user_reviews
)

router = APIRouter(tags=["Reviews"])

@router.post(
    "/movies/{movie_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def create_movie_review(
    movie_id: int,
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return create_review(
            movie_id=movie_id,
            data=data,
            current_user=current_user,
            db=db
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/movies/{movie_id}/reviews",
    response_model=MovieReviewsResponse
)
def movie_reviews(
    movie_id: int,
    db: Session = Depends(get_db)
):
    return get_movie_reviews(
        movie_id=movie_id,
        db=db
    )

@router.put(
    "/reviews/{review_id}",
    response_model=ReviewResponse
)
def edit_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return update_review(
            review_id=review_id,
            data=data,
            current_user=current_user,
            db=db
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.delete(
    "/reviews/{review_id}"
)
def remove_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        delete_review(
            review_id=review_id,
            current_user=current_user,
            db=db
        )

        return {
            "message": "Review deleted successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.get(
    "/users/reviews",
    response_model=UserReviewsResponse
)
def current_user_reviews(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_reviews(
        current_user=current_user,
        db=db,
        page=page,
        page_size=pageSize
    )