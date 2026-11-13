"""User model reserved for future opt-in authentication."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from verimed_api.models.base import Base, TimestampUUIDMixin


class User(TimestampUUIDMixin, Base):
    """Minimal user entity for future authentication support."""

    __tablename__ = "users"

    email_hash: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(32), default="public", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
