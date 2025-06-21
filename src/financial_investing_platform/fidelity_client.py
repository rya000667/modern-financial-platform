import os
from typing import List, Tuple

import requests

class FidelityClient:
    """Client for interacting with Fidelity Workplace Investing APIs."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("FIDELITY_API_BASE", "https://api.fidelity.com/wpx")
        self._token_url = f"{self.base_url}/oauth2/token"
        self._balances_endpoint = (
            f"{self.base_url}/workplace-investing/v1/participants/{{participant_id}}/balances"
        )

    def get_access_token(self) -> str:
        """Exchange client credentials for an OAuth bearer token."""
        auth = (
            os.environ["FIDELITY_CLIENT_ID"],
            os.environ["FIDELITY_CLIENT_SECRET"],
        )
        data = {
            "grant_type": "client_credentials",
            "scope": "wi.balances.read",
        }
        resp = requests.post(self._token_url, data=data, auth=auth, timeout=15)
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_balances(self, participant_id: str, bearer_token: str) -> dict:
        """Retrieve balances for a single participant."""
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json",
        }
        url = self._balances_endpoint.format(participant_id=participant_id)
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def extract_cash_dividends(self, response_json: dict) -> List[Tuple[str, float]]:
        """Return a list of (plan_type, cash_dividend_value) from the balances payload."""
        results: List[Tuple[str, float]] = []
        for plan in response_json.get("stockPlans", []):
            cash_div = plan.get("cashDividendsValue")
            if cash_div is not None:
                results.append((plan.get("planType", "Unknown plan"), cash_div))
        return results
