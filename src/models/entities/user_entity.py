import uuid
from datetime import datetime

from archipy.models.entities.sqlalchemy.base_entities import (
    UpdatableDeletableEntity,
)
from sqlalchemy import UUID, VARCHAR, Boolean, Column, Date, DateTime
from sqlalchemy.orm import Mapped, Synonym, mapped_column

from src.utils.utils import Utils


class UserEntity(UpdatableDeletableEntity):
    __tablename__ = "users"
    user_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pk_uuid = Synonym("user_uuid")

    first_name: Mapped[str] = mapped_column(type_=VARCHAR(255), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, index=True)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=True, index=True)

    email: Mapped[str] = mapped_column(type_=VARCHAR(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(type_=VARCHAR(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(type_=VARCHAR(320), nullable=False)
    is_active: Mapped[bool] = mapped_column(type_=Boolean, default=True, nullable=False, index=True)
    is_super_user: Mapped[bool] = mapped_column(type_=Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=Utils.get_datetime_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=Utils.get_datetime_utc_now,
        onupdate=Utils.get_datetime_utc_now,
        nullable=False,
    )
