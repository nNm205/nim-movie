from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy import text 
from app.database.session import engine
from app.core.logger import logger

from app.api.v1.router import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    logger.info("FastAPI application started")

@app.get("/")
def root():
    logger.info("Root endpoint called")

    return { 
        "message": "Backend running" 
    }

@app.get("/health/db")
def check_db():
    logger.info("Checking database connection")

    try: 
        with engine.begin() as conn: 
            conn.execute(text("SELECT 1"))

        logger.success("Database connected successfully")
        
        return {
            "database": "connected successfully"
        }
    
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

        return {
            "database": "failed"
        } 