# src/models/entities/__init__.py
from .genre_entity import GenreEntity
from .movie_entity import MovieEntity
from .user_entity import UserEntity
from .user_rate_movie_entity import UserRateMovieEntity
from .user_watch_movie_entity import UserWatchMovieEntity

__all__ = [
    "UserEntity",
    "MovieEntity",
    "GenreEntity",
    "UserWatchMovieEntity",
    "UserRateMovieEntity",
]
