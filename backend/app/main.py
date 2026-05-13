from fastapi import FastAPI 
from sqlalchemy import text 
from app.database.session import engine

app = FastAPI()

@app.get("/")
async def root():
    return { 
        "message": "Backend running" 
    }

@app.get("/health/db")
async def check_db():
    async with engine.begin() as conn: 
        await conn.execute(text("SELECT 1"))
    
    return {
        "database": "connected successfully"
    }