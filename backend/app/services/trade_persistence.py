
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.execution import Execution
from app.models.trade import Trade, TradeExecution
from app.models.broker_connection import BrokerConnection
from app.services.trade_matcher import group_position_cycles
from app.services.trade_matcher import (
    calculate_fifo,
    group_position_cycles,
)
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


def build_trade_summary(cycle):
    """Calculate the database fields for one position cycle."""

    fills = cycle["executions"]

    buys = [fill for fill in fills if fill.side.lower() == "buy"]
    sells = [fill for fill in fills if fill.side.lower() == "sell"]

    if not buys:
        raise ValueError("A long trade must have at least one buy.")

    total_bought = sum(
        (Decimal(str(fill.quantity)) for fill in buys),
        Decimal("0"),
    )

    total_sold = sum(
        (Decimal(str(fill.quantity)) for fill in sells),
        Decimal("0"),
    )

    remaining = total_bought - total_sold

    if remaining < 0:
        raise ValueError("Short positions are not supported yet.")

    entry_price = sum(
        (
            Decimal(str(fill.quantity)) * Decimal(str(fill.price))
            for fill in buys
        ),
        Decimal("0"),
    ) / total_bought

    exit_price = (
        sum(
            (
                Decimal(str(fill.quantity)) * Decimal(str(fill.price))
                for fill in sells
            ),
            Decimal("0"),
        ) / total_sold
        if total_sold > 0
        else None
    )

    _, gross_pnl, matches = calculate_fifo(
        fills, include_matches=True
    )
    fees = sum(
        (
            Decimal(str(getattr(fill, "fee", 0) or 0))
            for fill in fills
        ),
        Decimal("0"),
    )
    return {
        "symbol": cycle["symbol"],
        "status": cycle["status"],
        "quantity": total_bought,
        "remaining_quantity": remaining,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "entry_time": buys[0].executed_at,
        "exit_time": sells[-1].executed_at if remaining == 0 and sells else None,
        "gross_pnl": gross_pnl,
        "fees": fees,
        "net_pnl": gross_pnl - fees,
        "execution_ids": [fill.id for fill in fills],
    }

def save_closed_trades(db: Session, user_id):
    """Save completed long trades without creating duplicates."""

    connections = db.scalars(
        select(BrokerConnection).where(
            BrokerConnection.user_id == user_id
        )
    ).all()

    connection_ids = [connection.id for connection in connections]

    if not connection_ids:
        return 0

    executions = db.scalars(
        select(Execution)
        .where(Execution.broker_connection_id.in_(connection_ids))
        .order_by(Execution.executed_at, Execution.id)
    ).all()

    cycles = group_position_cycles(executions)
    saved = 0

    for cycle in cycles:
        if cycle["status"] != "closed":
            continue

        summary = build_trade_summary(cycle)
        first_fill = cycle["executions"][0]

        existing = db.scalar(
            select(Trade)
            .join(TradeExecution, TradeExecution.trade_id == Trade.id)
            .where(TradeExecution.execution_id == first_fill.id)
        )

        if existing is not None:
            if existing.user_id != user_id:
                raise ValueError("Trade belongs to another user.")
            trade = existing
        else:
            trade = Trade(user_id=user_id)
            db.add(trade)

        trade.symbol = summary["symbol"]
        trade.direction = "long"
        trade.quantity = summary["quantity"]
        trade.remaining_quantity = Decimal("0")
        trade.entry_price = summary["entry_price"]
        trade.exit_price = summary["exit_price"]
        trade.entry_time = summary["entry_time"]
        trade.exit_time = summary["exit_time"]
        trade.gross_pnl = summary["gross_pnl"]
        trade.fees = summary["fees"]
        trade.net_pnl = summary["net_pnl"]
        trade.status = "closed"

        db.flush()

        linked_ids = {
            link.execution_id for link in trade.execution_links
        }

        for fill in cycle["executions"]:
            if fill.id not in linked_ids:
                db.add(TradeExecution(
                    trade_id=trade.id,
                    execution_id=fill.id
                ))

        saved += 1

    db.commit()
    return saved