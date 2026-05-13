from typing import Literal
from fastapi import APIRouter, Query 
from app.services.movie_service import (
    get_trending_movies,
    get_movie_detail,
    search_movies,
    get_genres
)
from app.schemas.movie import (
    MovieListResponse,
    MovieDetailResponse,
    GenreResponse 
)

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get(
    "/trending",
    response_model=MovieListResponse
)
def trending_movies(
    page: int = Query(1),
    timeWindow: Literal["day", "week"] = Query("week")
):
    return get_trending_movies(
        page=page,
        time_window=timeWindow
    )

@router.get(
    "/search",
    response_model=MovieListResponse
)
def search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1)
):
    return search_movies(
        query=q, 
        page=page
    )

@router.get(
    "/genres",
    response_model=list[GenreResponse] 
)
def genres():
    return get_genres()

@router.get(
    "/{movie_id}",
    response_model=MovieDetailResponse
)
def movie_detail(movie_id: int):
    return get_movie_detail(movie_id)