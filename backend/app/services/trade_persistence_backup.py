
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.execution import Execution
from app.models.trade import Trade, TradeExecution
from app.models.broker_connection import BrokerConnection


def save_open_trades(db: Session, user_id):
    """
    Save open long positions to PostgreSQL.
    Re-running updates existing open trades instead of duplicating them.

    This first version supports buy-only positions.
    """

    connections = db.scalars(
        select(BrokerConnection).where(
            BrokerConnection.user_id == user_id
        )
    ).all()

    connection_ids = [c.id for c in connections]

    if not connection_ids:
        return 0

    executions = db.scalars(
        select(Execution)
        .where(Execution.broker_connection_id.in_(connection_ids))
        .order_by(Execution.executed_at, Execution.id)
    ).all()

    # Group executions by broker connection and symbol.
    groups = {}

    for execution in executions:
        key = (execution.broker_connection_id, execution.symbol)
        groups.setdefault(key, []).append(execution)

    saved = 0

    for (connection_id, symbol), fills in groups.items():
        # Do not persist incomplete or closed positions yet.
        if any(fill.side.lower() != "buy" for fill in fills):
            print(f"Skipping {symbol}: sells are not supported yet.")
            continue

        quantity = sum(
            (Decimal(str(fill.quantity)) for fill in fills),
            Decimal("0")
        )

        if quantity <= 0:
            continue

        entry_price = sum(
            (
                Decimal(str(fill.quantity)) * Decimal(str(fill.price))
                for fill in fills
            ),
            Decimal("0")
        ) / quantity

        first_fill = fills[0]

        # Find a trade already linked to this position's first fill.
        existing = db.scalar(
            select(Trade)
            .join(TradeExecution, TradeExecution.trade_id == Trade.id)
            .where(TradeExecution.execution_id == first_fill.id)
        )

        if existing is None:
            trade = Trade(
                user_id=user_id,
                symbol=symbol,
                direction="long",
                entry_price=entry_price,
                quantity=quantity,
                remaining_quantity=quantity,
                entry_time=first_fill.executed_at,
                fees=sum(
                    (Decimal(str(fill.fee or 0)) for fill in fills),
                    Decimal("0")
                ),
                status="open",
            )
            db.add(trade)
            db.flush()
        else:
            trade = existing
            if trade.user_id != user_id or trade.status != "open":
                raise ValueError(
                    f"Existing trade for {symbol} cannot be updated safely."
                )

            trade.entry_price = entry_price
            trade.quantity = quantity
            trade.remaining_quantity = quantity
            trade.fees = sum(
                (Decimal(str(fill.fee or 0)) for fill in fills),
                Decimal("0")
            )

        linked_ids = {
            link.execution_id for link in trade.execution_links
        }

        for fill in fills:
            if fill.id not in linked_ids:
                db.add(TradeExecution(
                    trade_id=trade.id,
                    execution_id=fill.id
                ))

        saved += 1

    db.commit()
    return saved
