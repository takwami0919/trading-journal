import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BrokerConnection(Base):
    """
    Represents one user's link to one brokerage account.

    API credentials are stored encrypted (see app/core/crypto.py) — never
    in plaintext, and never a brokerage login password (brokers don't give
    those to third-party apps; only API keys/tokens are ever stored here).
    """

    __tablename__ = "broker_connections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    broker_name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "alpaca"
    encrypted_api_key: Mapped[str] = mapped_column(String, nullable=False)
    encrypted_api_secret: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # success | failed

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="broker_connections")
    executions: Mapped[list["Execution"]] = relationship(
        back_populates="broker_connection", cascade="all, delete-orphan"
    )
