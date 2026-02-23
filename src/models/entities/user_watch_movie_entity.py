import uuid

from archipy.models.entities.sqlalchemy.base_entities import (
    UpdatableDeletableEntity,
)
from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import Synonym, relationship

from src.models.entities.mixins.timestamp import TimestampMixin


class UserWatchMovieEntity(UpdatableDeletableEntity, TimestampMixin):
    __tablename__ = "user_watch_movie"

    watch_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pk_uuid = Synonym("watch_uuid")

    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False, index=True)
    movie_uuid = Column(UUID(as_uuid=True), ForeignKey("movies.movie_uuid"), nullable=False, index=True)

    # Back-populating relationships
    user = relationship("UserEntity", back_populates="watched_movies")
    movie = relationship("MovieEntity", back_populates="watchers")
