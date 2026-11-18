
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Trade(Base):
    """
    A completed or currently open trade, produced by grouping
    executions using the FIFO matching engine.
    """

    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    strategy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategies.id", ondelete="SET NULL"),
        nullable=True
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    direction: Mapped[str] = mapped_column(
        String(5),
        nullable=False
    )

    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False
    )

    exit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True
    )

    # Increased precision for cryptocurrency trades
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(28, 12),
        nullable=False
    )

    remaining_quantity: Mapped[Decimal] = mapped_column(
        Numeric(28, 12),
        nullable=False,
        default=0
    )

    entry_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    exit_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    gross_pnl: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True
    )

    fees: Mapped[Decimal] = mapped_column(
        Numeric(28, 12),
        default=0
    )

    net_pnl: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(10),
        default="open"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="trades"
    )

    strategy: Mapped["Strategy | None"] = relationship(
        back_populates="trades"
    )

    execution_links: Mapped[list["TradeExecution"]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan"
    )

    notes: Mapped[list["TradeNote"]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan"
    )

    screenshots: Mapped[list["Screenshot"]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan"
    )


class TradeExecution(Base):
    """
    Join table linking trades to their executions.
    """

    __tablename__ = "trade_executions"

    trade_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trades.id", ondelete="CASCADE"),
        primary_key=True
    )

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("executions.id", ondelete="CASCADE"),
        primary_key=True
    )

    trade: Mapped["Trade"] = relationship(
        back_populates="execution_links"
    )

    execution: Mapped["Execution"] = relationship(
        back_populates="trade_links"
    )
