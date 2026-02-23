import uuid

from archipy.models.entities.sqlalchemy.base_entities import (
    UpdatableDeletableEntity,
)
from sqlalchemy import TEXT, UUID, VARCHAR, Column, ForeignKey
from sqlalchemy.orm import Mapped, Synonym, mapped_column, relationship

from src.models.entities.mixins.timestamp import TimestampMixin


class MovieEntity(UpdatableDeletableEntity, TimestampMixin):
    __tablename__ = "movies"

    movie_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pk_uuid = Synonym("movie_uuid")

    title: Mapped[str] = mapped_column(type_=VARCHAR(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(type_=TEXT, nullable=True)

    # Foreign Key to Genre (Each movie has one genre)
    genre_uuid = Column(UUID(as_uuid=True), ForeignKey("genres.genre_uuid"), nullable=False)

    # Relationships
    genre = relationship("GenreEntity", back_populates="movies")

    # Many-to-Many relationships via association tables
    watchers = relationship("UserWatchMovieEntity", back_populates="movie")
    ratings = relationship("UserRateMovieEntity", back_populates="movie")
