from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.services.movie_service import get_movie_detail

def create_review(
    movie_id: int,
    data: ReviewCreate,
    current_user: User,
    db: Session
):
    movie = get_movie_detail(movie_id)

    if not movie:
        raise ValueError("Movie not found")
    
    existing = db.execute(
        select(Review).where(
            Review.user_id == current_user.id,
            Review.movie_id == movie_id
        )
    ).scalar_one_or_none()

    if existing:
        raise ValueError(
            "You already reviewed this movie"
        )
    
    review = Review(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=data.rating,
        review_text=data.review_text
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review

def get_movie_reviews(
    movie_id: int,
    db: Session 
):
    result = db.execute(
        select(Review)
        .where(Review.movie_id == movie_id)
        .order_by(Review.created_at.desc())
    )

    reviews = result.scalars().all()

    average_rating = db.execute(
        select(func.avg(Review.rating))
        .where(Review.movie_id == movie_id)
    ).scalar()

    total_reviews = db.execute(
        select(func.count())
        .select_from(Review)
        .where(Review.movie_id == movie_id)
    ).scalar()

    return {
        "items": reviews,
        "average_rating": round(average_rating or 0, 1),
        "total_reviews": total_reviews
    }

def update_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User,
    db: Session 
):
    review = db.execute(
        select(Review).where(
            Review.id == review_id
        )
    ).scalar_one_or_none()

    if not review:
        raise ValueError("Review not found")
    
    if review.user_id != current_user.id:
        raise PermissionError(
            "Not allowed to edit this review"
        )
    
    if data.rating is not None: 
        review.rating = data.rating 
    
    if data.review_text is not None:
        review.review_text = data.review_text
    
    db.commit()
    db.refresh(review)

    return review 

def delete_review(
    review_id: int,
    current_user: User,
    db: Session
):
    review = db.execute(
        select(Review).where(
            Review.id == review_id
        )
    ).scalar_one_or_none()

    if not review:
        raise ValueError("Review not found")
    
    if review.user_id != current_user.id:
        raise PermissionError(
            "Not allowed to edit this review"
        )
    
    db.delete(review)
    db.commit()

def get_user_reviews(
    current_user: User,
    db: Session,
    page: int = 1,
    page_size: int = 20 
):
    offset = (page - 1) * page_size

    result = db.execute(
        select(Review)
        .where(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    reviews = result.scalars().all()

    total = db.execute(
        select(func.count())
        .select_from(Review)
        .where(Review.user_id == current_user.id)
    ).scalar()

    return {
        "items": reviews,
        "total": total,
        "page": page,
        "pageSize": page_size
    }
    