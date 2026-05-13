import httpx
from app.config import settings
from fastapi import HTTPException 
from app.core.logger import logger 

class TMDbClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY

    def get(self, endpoint: str, params: dict | None = None):
        params = params or {}
        params["api_key"] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"

        logger.info(f"Calling TMDb API: {url}")

        try: 
            with httpx.Client() as client:
                response = client.get(
                    url,
                    params=params 
                )

                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e: 
            logger.error(f"TMDb HTTP error | status={e.response.status_code}")

            raise HTTPException(
                status_code=e.response.status_code,
                detail="TMDb API error"
            )
        
        except httpx.RequestError as e:
            logger.error(f"TMDb connection error: {str(e)}")

            raise HTTPException(
                status_code=503,
                detail="TMDb service unavailable"
            )