# pylint: skip-file
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Mixin that adds timezone-aware timestamping and soft-delete capabilities."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp of when the record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp of when the record was last updated",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Timestamp of when the record was soft-deleted"
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",  # Enforces default directly in the SQL schema
        default=False,  # Enforces default in the Python ORM
        nullable=False,
        index=True,  # Crucial for query performance on soft-deleted tables
        comment="Flag indicating if the record is soft-deleted",
    )
