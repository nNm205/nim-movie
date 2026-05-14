from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, users, movies, watchlist

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(admin.router) 
api_router.include_router(users.router)
api_router.include_router(movies.router)
api_router.include_router(watchlist.router)