from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.watchlist import Watchlist
from app.services.movie_service import get_movie_detail
from app.core.logger import logger

def add_to_watchlist(
    user_id: int,
    movie_id: int,
    db: Session
):
    logger.info(
        f"Adding movie to watchlist | user_id={user_id} | movie_id={movie_id}"
    )
    try: 
        movie = get_movie_detail(movie_id)

        if not movie:
            logger.warning(
                f"Movie not found from TMDB | movie_id={movie_id}"
            )
            
            raise ValueError("Movie not found")
        
        result = db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.movie_id == movie_id
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(
                f"Movie already exists in watchlist | user_id={user_id} | movie_id={movie_id}"
            )

            raise ValueError(
                "Movie already in watchlist"
            )
        
        item = Watchlist(
            user_id=user_id,
            movie_id=movie_id
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        logger.info(
            f"Movie added successfully | user_id={user_id} | movie_id={movie_id}"
        )
        
        return item 
    
    except Exception as e:
        db.rollback()
        
        logger.exception(
            f"Failed to add movie to watchlist | user_id={user_id} | movie_id={movie_id}"
        )

        raise e

def get_user_watchlist(
    user_id: int,
    db: Session,
    page: int = 1,
    page_size: int = 20
):
    logger.info(
        f"Fetching user watchlist | user_id={user_id} | page={page}"
    )

    offset = (page - 1) * page_size

    result = db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == user_id)
        .order_by(Watchlist.added_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    items = result.scalars().all()

    logger.info(
        f"Retrieved watchlist items from database | user_id={user_id} | count={len(items)}"
    )

    enriched_items = []

    for item in items:
        try: 
            movie = get_movie_detail(item.movie_id)

            if not movie:
                logger.warning(
                    f"Movie data not found from TMDB | movie_id={item.movie_id}"
                )

                continue 

            enriched_items.append({
                "movie_id": item.movie_id,
                "title": movie.get("title"),
                "poster_path": movie.get("poster_path"),
                "backdrop_path": movie.get("backdrop_path"),
                "added_at": item.added_at,
                "progress": item.progress,
                "is_completed": item.is_completed
            })

        except Exception:
            logger.exception(
                f"Failed to fetch movie detail from TMDB | movie_id={item.movie_id}"
            )
            
            continue
    
    total_result = db.execute(
        select(func.count())
        .select_from(Watchlist)
        .where(Watchlist.user_id == user_id)
    )

    total = total_result.scalar()

    logger.info(
        f"Watchlist fetched successfully | user_id={user_id} | total={total}"
    )

    return {
        "items": enriched_items,
        "total": total,
        "page": page,
        "pageSize": page_size
    }

def remove_from_watchlist(
    user_id: int,
    movie_id: int,
    db: Session
):
    logger.info(
        f"Removing movie from watchlist | user_id={user_id} | movie_id={movie_id}"
    )

    try: 
        result = db.execute(
            select(Watchlist).where(
                Watchlist.user_id == user_id,
                Watchlist.movie_id == movie_id 
            )
        )

        item = result.scalar_one_or_none()

        if not item:
            logger.warning(
                f"Movie not found in watchlist | user_id={user_id} | movie_id={movie_id}"
            )

            raise ValueError(
                "Movie not found in watchlist"
            )
        
        db.delete(item)
        db.commit()

        logger.info(
            f"Movie removed successfully | user_id={user_id} | movie_id={movie_id}"
        )
    
    except Exception as e: 
        db.rollback()

        logger.exception(
            f"Failed to remove movie from watchlist | user_id={user_id} | movie_id={movie_id}"
        )

        raise e