from pydantic import BaseModel, Field 
from typing import Optional
from datetime import date

class MovieResponse(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[date] = None
    vote_average: float = 0.0
    vote_count: int = 0
    genre_ids: list[int] = Field(default_factory=list)

class CastResponse(BaseModel):
    id: int
    name: str
    character: Optional[str] = None

class CrewResponse(BaseModel):
    id: int
    name: str
    job: Optional[str] = None

class MovieDetailResponse(MovieResponse):
    runtime: Optional[int] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    genres: list[dict] = Field(default_factory=list)
    homepage: Optional[str] = None
    cast: list[CastResponse] = Field(default_factory=list)
    crew: list[CrewResponse] = Field(default_factory=list)

class MovieListResponse(BaseModel):
    items: list[MovieResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int

class GenreResponse(BaseModel):
    id: int
    name: str