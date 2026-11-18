import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Strategy(Base):
    """A user-defined tag like 'Opening Range Breakout' used to group trades."""

    __tablename__ = "strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="strategies")
    trades: Mapped[list["Trade"]] = relationship(back_populates="strategy")


class TradeNote(Base):
    """
    Manual, subjective journaling attached to a trade AFTER it was
    automatically imported — notes, strategy reasoning, emotional state,
    self-identified mistakes. Never auto-generated.
    """

    __tablename__ = "trade_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotional_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mistake_tag: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trade: Mapped["Trade"] = relationship(back_populates="notes")


class Screenshot(Base):
    """A chart/screenshot the user attaches to a specific trade."""

    __tablename__ = "screenshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trade: Mapped["Trade"] = relationship(back_populates="screenshots")
