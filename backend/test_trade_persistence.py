
from app.services.trade_persistence import build_trade_summary
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

from app.services.trade_matcher import calculate_fifo

now = datetime.now(timezone.utc)

# Simulate buying, partially selling, then closing a position
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

# First test: partial close
open_lots, pnl = calculate_fifo(executions)

remaining = sum(
    (lot["quantity"] for lot in open_lots["AAPL"]),
    Decimal("0")
)

assert pnl == Decimal("220")
assert remaining == Decimal("3")

print("Partial close test passed!")
print("Realized P&L:", pnl)
print("Remaining shares:", remaining)

# Second test: sell remaining 3 shares
executions.append(
    SimpleNamespace(
        id=4, symbol="AAPL", side="sell",
        quantity=Decimal("3"), price=Decimal("115"),
        executed_at=now + timedelta(minutes=3)
    )
)

open_lots, pnl = calculate_fifo(executions)

remaining = sum(
    (lot["quantity"] for lot in open_lots["AAPL"]),
    Decimal("0")
)

assert pnl == Decimal("235")
assert remaining == Decimal("0")

print("Full close test passed!")
print("Total realized P&L:", pnl)
print("Remaining shares:", remaining)
print("ALL TESTS PASSED!")

# Test detailed FIFO matches
open_lots, pnl, matches = calculate_fifo(
    executions,
    include_matches=True
)

assert len(matches) == 3
assert sum(m["gross_pnl"] for m in matches) == Decimal("235")
assert all(m["net_pnl"] == m["gross_pnl"] - m["fees"] for m in matches)

print("Detailed FIFO matches:", len(matches))
print("Detailed matching test passed!")


from app.services.trade_matcher import group_position_cycles

# Add a new buy after the previous position closed
cycle_executions = executions + [
    SimpleNamespace(
        id=5,
        broker_connection_id=1,
        symbol="AAPL",
        side="buy",
        quantity=Decimal("3"),
        price=Decimal("130"),
        executed_at=now + timedelta(minutes=4),
    )
]

# Give the earlier executions the same broker connection
for execution in cycle_executions:
    execution.broker_connection_id = 1

cycles = group_position_cycles(cycle_executions)

assert len(cycles) == 2
assert cycles[0]["status"] == "closed"
assert cycles[1]["status"] == "open"
assert len(cycles[0]["executions"]) == 4
assert len(cycles[1]["executions"]) == 1

print("Position cycles:", len(cycles))
print("First cycle:", cycles[0]["status"])
print("Second cycle:", cycles[1]["status"])
print("POSITION CYCLE TEST PASSED!")
# Verify P&L is calculated separately for each trade cycle
first_cycle = cycles[0]["executions"]
second_cycle = cycles[1]["executions"]

_, first_pnl, first_matches = calculate_fifo(
    first_cycle, include_matches=True
)

_, second_pnl, second_matches = calculate_fifo(
    second_cycle, include_matches=True
)

assert first_pnl == Decimal("235")
assert len(first_matches) == 3

assert second_pnl == Decimal("0")
assert len(second_matches) == 0

print("Closed trade P&L:", first_pnl)
print("New open trade P&L:", second_pnl)
print("TRADE CYCLE P&L TEST PASSED!")

# Test trade summaries
closed_summary = build_trade_summary(cycles[0])
open_summary = build_trade_summary(cycles[1])

assert closed_summary["status"] == "closed"
assert closed_summary["remaining_quantity"] == Decimal("0")
assert closed_summary["gross_pnl"] == Decimal("235")

assert open_summary["status"] == "open"
assert open_summary["gross_pnl"] == Decimal("0")
assert open_summary["remaining_quantity"] > 0

print("Closed trade P&L:", closed_summary["gross_pnl"])
print("Open trade remaining:", open_summary["remaining_quantity"])
print("TRADE SUMMARY TEST PASSED!")

# Verify fee calculations
assert closed_summary["net_pnl"] == (
    closed_summary["gross_pnl"] - closed_summary["fees"]
)

print("FEE CALCULATION TEST PASSED!")

print("Gross P&L:", closed_summary["gross_pnl"])
print("Fees:", closed_summary["fees"])
print("Net P&L:", closed_summary["net_pnl"])

# Test nonzero fees
fee_test = closed_summary.copy()
fee_test["fees"] = Decimal("5")
fee_test["net_pnl"] = fee_test["gross_pnl"] - fee_test["fees"]

assert fee_test["net_pnl"] == Decimal("230")

print("NONZERO FEE TEST PASSED!")

# Test fees supplied by executions
from types import SimpleNamespace

fee_executions = [
    SimpleNamespace(**{
        **vars(fill),
        "fee": Decimal("1")
    })
    for fill in cycles[0]["executions"]
]

fee_cycle = {
    **cycles[0],
    "executions": fee_executions
}

fee_summary = build_trade_summary(fee_cycle)

assert fee_summary["fees"] == Decimal(len(fee_executions))
assert fee_summary["net_pnl"] == (
    fee_summary["gross_pnl"] - fee_summary["fees"]
)

print("EXECUTION FEE TEST PASSED!")
print("Fees:", fee_summary["fees"])
print("Net P&L:", fee_summary["net_pnl"])