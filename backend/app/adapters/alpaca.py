
import requests

from app.adapters.broker import BrokerAdapter


class AlpacaAdapter(BrokerAdapter):
    """Broker adapter for Alpaca paper trading."""

    def __init__(self, api_key: str, secret_key: str, base_url: str):
        self.base_url = base_url.rstrip("/")

        self.headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
        }

    def get_account(self) -> dict:
        response = requests.get(
            f"{self.base_url}/v2/account",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def get_positions(self) -> list[dict]:
        response = requests.get(
            f"{self.base_url}/v2/positions",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def get_activities(self, activity_type: str) -> list[dict]:
        """Fetch all activities of a specific type."""
        all_activities = []
        page_token = None

        while True:
            params = {
                "direction": "asc",
                "page_size": 100,
            }

            if page_token:
                params["page_token"] = page_token

            response = requests.get(
                f"{self.base_url}/v2/account/activities/{activity_type}",
                headers=self.headers,
                params=params,
                timeout=10,
            )

            response.raise_for_status()
            activities = response.json()

            if not activities:
                break

            all_activities.extend(activities)

            if len(activities) < 100:
                break

            next_token = activities[-1]["id"]

            if next_token == page_token:
                raise RuntimeError(
                    "Alpaca pagination did not advance."
                )

            page_token = next_token

        return all_activities

    def get_executions(self) -> list[dict]:
        """Fetch all filled executions."""
        return self.get_activities("FILL")

    def get_crypto_fees(self) -> list[dict]:
        """Fetch cryptocurrency fee activities."""
        return self.get_activities("CFEE")
