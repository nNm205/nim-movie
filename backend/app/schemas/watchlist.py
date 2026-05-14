from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class WatchlistItemResponse(BaseModel):
    movie_id: int
    title: str
    poster_path: Optional[str] = None 
    backdrop_path: Optional[str] = None 
    added_at: datetime 
    progress: int 
    is_completed: bool 
class WatchlistListResponse(BaseModel):
    items: list[WatchlistItemResponse]
    total: int
    page: int 
    pageSize: int 