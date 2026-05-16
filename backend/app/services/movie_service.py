from app.integrations.tmdb_client import TMDbClient
from app.core.logger import logger 

tmdb_client = TMDbClient()

def get_discover_movies(
    page: int = 1,
    sort_by: str = "popularity.desc"
): 
    logger.info(f"Discover movies | page={page} | sort_by={sort_by}")

    data = tmdb_client.get(
        "/discover/movie", 
        params={
            "page": page,
            "sort_by": sort_by 
        }
    )

    return {
        "items": data["results"],
        "total": data["total_results"],
        "page": data["page"],
        "pageSize": len(data["results"]),
        "totalPages": data["total_pages"]
    }

def get_popular_movies(page: int = 1):
    logger.info(f"Fetching popular movies | page={page}")

    data = tmdb_client.get(
        "/movie/popular",
        params={
            "page": page
        }
    )

    return {
        "items": data["results"],
        "total": data["total_results"],
        "page": data["page"],
        "pageSize": len(data["results"]),
        "totalPages": data["total_pages"]
    }

def get_top_rated_movies(page: int = 1):
    logger.info(f"Fetching top rated movies | page={page}")

    data = tmdb_client.get(
        "/movie/top_rated",
        params={"page": page}
    )

    return {
        "items": data["results"],
        "total": data["total_results"],
        "page": data["page"],
        "pageSize": len(data["results"]),
        "totalPages": data["total_pages"]
    }

def get_trending_movies(
    page: int = 1,
    time_window: str = "week"
):
    logger.info(f"Fetching trending movies | page={page}")

    data = tmdb_client.get(
        f"/trending/movie/{time_window}",
        params={"page": page}
    )

    return {
        "items": data["results"],
        "total": data["total_results"],
        "page": data["page"],
        "pageSize": len(data["results"]),
        "totalPages": data["total_pages"]
    }

def get_movie_detail(movie_id: int):
    logger.info(
        f"Fetching movie detail | id={movie_id}"
    )

    movie = tmdb_client.get(
        f"/movie/{movie_id}",
        params={"append_to_response": "credits"}
    )

    return {
        **movie,
        "cast": movie.get("credits", {}).get("cast", []),
        "crew": movie.get("credits", {}).get("crew", [])
    }

def search_movies(
    query: str,
    page: int = 1
):
    logger.info(f"Searching movies | query={query}")

    data = tmdb_client.get(
        "/search/movie",
        params={
            "query": query,
            "page": page
        }
    )

    return {
        "items": data["results"],
        "total": data["total_results"],
        "page": data["page"],
        "pageSize": len(data["results"]),
        "totalPages": data["total_pages"]
    }

def get_genres():
    logger.info("Fetching movie genres")
    
    data = tmdb_client.get("/genre/movie/list")
    return data["genres"]