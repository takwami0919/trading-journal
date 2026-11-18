import uuid
from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DailyPerformance(Base):
    """
    Precomputed per-day P&L rollup, one row per (user, date).

    This exists so the trading calendar and dashboard charts don't have to
    aggregate the full trades table on every page load. Recomputed after
    each sync (see app/services/analytics.py once we build it).
    """

    __tablename__ = "daily_performance"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_daily_performance_per_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)

    total_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=0)
    trade_count: Mapped[int] = mapped_column(default=0)
    win_count: Mapped[int] = mapped_column(default=0)
    loss_count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="daily_performance")
