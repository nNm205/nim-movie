from fastapi import FastAPI 
from sqlalchemy import text 
from app.database.session import engine
from app.core.logger import logger

app = FastAPI()

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