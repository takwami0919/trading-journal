from abc import ABC, abstractmethod
from typing import Any


class BrokerAdapter(ABC):
    """Common interface for brokerage integrations."""

    @abstractmethod
    def get_account(self) -> dict[str, Any]:
        """Return basic information about the connected brokerage account."""
        pass

    @abstractmethod
    def get_executions(self) -> list[dict[str, Any]]:
        """Return filled executions from the brokerage."""
        pass