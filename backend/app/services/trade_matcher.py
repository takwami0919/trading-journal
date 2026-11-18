
from collections import deque
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.execution import Execution


def calculate_fifo(executions, include_matches=False):
    """
    Calculate FIFO matches for long positions.

    Returns:
        open_lots: remaining unmatched buy quantities
        realized_pnl: total realized gross P&L
        matches: individual buy/sell matches (optional)

    Does not modify the database.
    """

    open_lots = {}
    realized_pnl = Decimal("0")
    matches = []

    ordered = sorted(
        executions,
        key=lambda e: (e.executed_at, str(e.id))
    )

    for execution in ordered:
        symbol = execution.symbol
        side = execution.side.lower()
        quantity = Decimal(str(execution.quantity))
        price = Decimal(str(execution.price))
        fee = Decimal(str(getattr(execution, "fee", 0) or 0))

        if quantity <= 0:
            raise ValueError("Execution quantity must be positive.")

        if symbol not in open_lots:
            open_lots[symbol] = deque()

        if side == "buy":
            open_lots[symbol].append({
                "quantity": quantity,
                "original_quantity": quantity,
                "price": price,
                "execution_id": execution.id,
                "executed_at": execution.executed_at,
                "fee": fee,
            })

        elif side == "sell":
            remaining = quantity

            while remaining > 0 and open_lots[symbol]:
                oldest = open_lots[symbol][0]
                matched = min(remaining, oldest["quantity"])

                gross_pnl = matched * (price - oldest["price"])

                # Allocate fees proportionally to matched quantity.
                buy_fee = (
                    oldest["fee"]
                    * matched
                    / oldest["original_quantity"]
                )
                sell_fee = fee * matched / quantity

                matches.append({
                    "symbol": symbol,
                    "buy_execution_id": oldest["execution_id"],
                    "sell_execution_id": execution.id,
                    "quantity": matched,
                    "entry_price": oldest["price"],
                    "exit_price": price,
                    "entry_time": oldest["executed_at"],
                    "exit_time": execution.executed_at,
                    "gross_pnl": gross_pnl,
                    "fees": buy_fee + sell_fee,
                    "net_pnl": gross_pnl - buy_fee - sell_fee,
                })

                realized_pnl += gross_pnl

                print(
                    f"{symbol}: matched {matched} units, "
                    f"realized P&L = ${gross_pnl:.2f}"
                )

                oldest["quantity"] -= matched
                remaining -= matched

                if oldest["quantity"] == 0:
                    open_lots[symbol].popleft()

            if remaining > 0:
                raise ValueError(
                    f"Unmatched sell of {remaining} {symbol}. "
                    "Short positions are not supported yet."
                )

        else:
            raise ValueError(f"Unknown execution side: {side}")

    if include_matches:
        return open_lots, realized_pnl, matches

    return open_lots, realized_pnl


def match_trades(db: Session, user_id, include_matches=False):
    """Load executions from PostgreSQL and calculate FIFO."""

    executions = db.scalars(
        select(Execution)
        .where(Execution.broker_connection.has(user_id=user_id))
        .order_by(Execution.executed_at, Execution.id)
    ).all()

    return calculate_fifo(
        executions,
        include_matches=include_matches
    )

def group_position_cycles(executions):
    """
    Group long-position executions into trading cycles.

    A cycle starts when position quantity goes above zero
    and ends when it returns to zero.
    """

    groups = {}
    cycles = []

    for execution in sorted(
        executions,
        key=lambda e: (e.executed_at, str(e.id))
    ):
        key = (execution.broker_connection_id, execution.symbol)

        if key not in groups:
            groups[key] = {
                "quantity": Decimal("0"),
                "executions": [],
            }

        group = groups[key]
        quantity = Decimal(str(execution.quantity))
        side = execution.side.lower()

        if quantity <= 0:
            raise ValueError("Execution quantity must be positive.")

        if side == "buy":
            group["quantity"] += quantity
        elif side == "sell":
            group["quantity"] -= quantity
        else:
            raise ValueError(f"Unknown execution side: {side}")

        if group["quantity"] < 0:
            raise ValueError(
                f"Short positions are not supported yet: {execution.symbol}"
            )

        group["executions"].append(execution)

        if group["quantity"] == 0:
            cycles.append({
                "connection_id": key[0],
                "symbol": key[1],
                "executions": group["executions"],
                "status": "closed",
            })
            group["executions"] = []

    for (connection_id, symbol), group in groups.items():
        if group["executions"]:
            cycles.append({
                "connection_id": connection_id,
                "symbol": symbol,
                "executions": group["executions"],
                "status": "open",
            })

    return cycles
