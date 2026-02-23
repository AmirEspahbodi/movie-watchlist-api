import uuid

from archipy.models.entities.sqlalchemy.base_entities import (
    UpdatableDeletableEntity,
)
from sqlalchemy import UUID, CheckConstraint, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, Synonym, mapped_column, relationship

from src.models.entities.mixins.timestamp import TimestampMixin


class UserRateMovieEntity(UpdatableDeletableEntity, TimestampMixin):
    __tablename__ = "user_rate_movie"

    rate_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pk_uuid = Synonym("rate_uuid")

    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.user_uuid"), nullable=False, index=True)
    movie_uuid = Column(UUID(as_uuid=True), ForeignKey("movies.movie_uuid"), nullable=False, index=True)

    # e.g. rating out of 10 or 5. Adding a CheckConstraint ensures valid DB state
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    # Back-populating relationships
    user = relationship("UserEntity", back_populates="movie_ratings")
    movie = relationship("MovieEntity", back_populates="ratings")

    __table_args__ = (CheckConstraint("score >= 1 AND score <= 10", name="check_rating_range"),)
