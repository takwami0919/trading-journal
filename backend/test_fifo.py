
from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.services.trade_matcher import calculate_fifo

now = datetime.now()

executions = [
    SimpleNamespace(
        id=1, symbol="AAPL", side="buy",
        quantity=Decimal("10"), price=Decimal("100"),
        executed_at=now
    ),
    SimpleNamespace(
        id=2, symbol="AAPL", side="buy",
        quantity=Decimal("5"), price=Decimal("110"),
        executed_at=now + timedelta(minutes=1)
    ),
    SimpleNamespace(
        id=3, symbol="AAPL", side="sell",
        quantity=Decimal("12"), price=Decimal("120"),
        executed_at=now + timedelta(minutes=2)
    ),
]

open_lots, pnl = calculate_fifo(executions)

remaining = sum(
    lot["quantity"] for lot in open_lots["AAPL"]
)

print("Total realized P&L:", pnl)
print("Remaining shares:", remaining)

assert pnl == Decimal("220")
assert remaining == Decimal("3")

print("FIFO TEST PASSED!")
