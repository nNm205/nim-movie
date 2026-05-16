from typing import Literal
from fastapi import APIRouter, Query 
from app.services.movie_service import (
    get_trending_movies,
    get_movie_detail,
    search_movies,
    get_genres,
    get_discover_movies,
    get_popular_movies,
    get_top_rated_movies
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
    "/popular", 
    response_model=MovieListResponse
)
def popular_movies(page: int = Query(1, ge=1)):
    return get_popular_movies(page=page)

@router.get(
    "/top-rated", 
    response_model=MovieListResponse
)
def top_rated_movies(page: int = Query(1, ge=1)):
    return get_top_rated_movies(page=page)

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
    "/discover",
    response_model=MovieListResponse
)
def discover_movies(
    page: int = Query(1, ge=1),
    sort_by: str = Query("popularity.desc")
):
    return get_discover_movies(
        page=page,
        sort_by=sort_by
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