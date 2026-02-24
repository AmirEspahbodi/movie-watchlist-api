# src/models/entities/user_watch_movie_entity.py
import uuid

from archipy.models.entities.sqlalchemy.base_entities import UpdatableDeletableEntity
from sqlalchemy import UUID, VARCHAR, Column, ForeignKey
from sqlalchemy.orm import Mapped, Synonym, mapped_column, relationship

from src.models.entities.mixins.timestamp import TimestampMixin
from src.models.types.watch_status_type import WatchStatusType


class UserWatchMovieEntity(UpdatableDeletableEntity, TimestampMixin):
    __tablename__ = "user_watch_movie"

    watch_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pk_uuid = Synonym("watch_uuid")

    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False, index=True)
    movie_uuid = Column(UUID(as_uuid=True), ForeignKey("movies.movie_uuid"), nullable=False, index=True)

    # Watch status stored as plain VARCHAR to avoid PostgreSQL ENUM migrations
    status: Mapped[str] = mapped_column(
        type_=VARCHAR(20),
        nullable=False,
        server_default=WatchStatusType.WANT_TO_WATCH.value,
        default=WatchStatusType.WANT_TO_WATCH,
        index=True,
    )

    # Back-populating relationships
    user = relationship("UserEntity", back_populates="watched_movies")
    movie = relationship("MovieEntity", back_populates="watchers")
