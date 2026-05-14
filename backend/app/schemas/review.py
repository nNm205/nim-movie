from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=10)
    review_text: Optional[str] = Field(None, max_length=2000)

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=10)
    review_text: Optional[str] = Field(None, max_length=2000)

class ReviewUserResponse(BaseModel):
    id: int
    username: str

class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    rating: int
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime
    user: ReviewUserResponse

    class Config:
        from_attributes = True

class MovieReviewsResponse(BaseModel):
    items: list[ReviewResponse]
    average_rating: float
    total_reviews: int

class UserReviewsResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    pageSize: int