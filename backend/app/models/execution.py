
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Execution(Base):
    """
    One raw fill reported by the broker.

    Broker execution IDs are unique per connection, preventing
    duplicate fills when synchronizing multiple times.
    """

    __tablename__ = "executions"

    __table_args__ = (
        UniqueConstraint(
            "broker_connection_id",
            "broker_execution_id",
            name="uq_execution_per_broker"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    broker_connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("broker_connections.id", ondelete="CASCADE"),
        nullable=False
    )

    broker_execution_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    side: Mapped[str] = mapped_column(
        String(4),
        nullable=False
    )

    # Increased precision for cryptocurrency quantities
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(28, 12),
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False
    )

    fee: Mapped[Decimal] = mapped_column(
        Numeric(28, 12),
        default=0
    )

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    raw_payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    broker_connection: Mapped["BrokerConnection"] = relationship(
        back_populates="executions"
    )

    trade_links: Mapped[list["TradeExecution"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan"
    )
