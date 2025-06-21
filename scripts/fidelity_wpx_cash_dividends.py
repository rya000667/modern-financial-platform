import os
import requests
from typing import List, Tuple


# ------------------------------------------------------------------
# 1.  Configuration helpers
# ------------------------------------------------------------------
BASE_URL = os.getenv("FIDELITY_API_BASE", "https://api.fidelity.com/wpx")
TOKEN_URL = f"{BASE_URL}/oauth2/token"

# WI Balances endpoint (non-delegated, client-credentials flow).
BALANCES_ENDPOINT = (
    f"{BASE_URL}/workplace-investing/v1/participants/{{participant_id}}/balances"
)


# ------------------------------------------------------------------
# 2.  Auth – Client-Credentials flow
# ------------------------------------------------------------------
def get_access_token() -> str:
    """Exchange your client_id/client_secret for a bearer token."""
    auth = (os.environ["FIDELITY_CLIENT_ID"], os.environ["FIDELITY_CLIENT_SECRET"])
    data = {
        "grant_type": "client_credentials",
        "scope": "wi.balances.read",
    }
    resp = requests.post(TOKEN_URL, data=data, auth=auth, timeout=15)
    resp.raise_for_status()
    return resp.json()["access_token"]


# ------------------------------------------------------------------
# 3.  API call
# ------------------------------------------------------------------
def get_balances(participant_id: str, bearer_token: str) -> dict:
    """Call WI Balances for a single participant."""
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json",
    }
    url = BALANCES_ENDPOINT.format(participant_id=participant_id)
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------
# 4.  Business logic – pull out dividend values
# ------------------------------------------------------------------
def extract_cash_dividends(response_json: dict) -> List[Tuple[str, float]]:
    """Parse the balances payload and return a list of (plan_type, cash_div) tuples."""
    results = []
    for plan in response_json.get("stockPlans", []):
        cash_div = plan.get("cashDividendsValue")
        if cash_div is not None:
            results.append((plan.get("planType", "Unknown plan"), cash_div))
    return results


# ------------------------------------------------------------------
# 5.  Glue code / simple CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    PARTICIPANT_ID = "REPLACE_WITH_PARTICIPANT_ID"

    token = get_access_token()
    balances_payload = get_balances(PARTICIPANT_ID, token)
    dividend_rows = extract_cash_dividends(balances_payload)

    if not dividend_rows:
        print("No cash-dividend data returned for this participant.")
    else:
        print("Cash dividends currently held inside each stock plan:")
        for plan_type, amount in dividend_rows:
            print(f"\u2022 {plan_type:20s} : ${amount:,.2f}")

