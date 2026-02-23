import uuid

from archipy.models.entities.sqlalchemy.base_entities import (
    UpdatableDeletableEntity,
)
from sqlalchemy import TEXT, UUID, VARCHAR, Column
from sqlalchemy.orm import Mapped, Synonym, mapped_column, relationship

from src.models.entities.mixins.timestamp import TimestampMixin


class GenreEntity(UpdatableDeletableEntity, TimestampMixin):
    __tablename__ = "genres"

    genre_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pk_uuid = Synonym("genre_uuid")

    name: Mapped[str] = mapped_column(type_=VARCHAR(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(type_=TEXT, nullable=True)

    movies = relationship("MovieEntity", back_populates="genre")
