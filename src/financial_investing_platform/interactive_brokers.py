from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import TickerId


class IBKRClient(EWrapper, EClient):
    """Minimal IBKR API client to fetch account summary."""

    def __init__(self):
        EClient.__init__(self, self)
        self.account_summary = []

    # Required callback when connection is established
    def nextValidId(self, orderId: int):
        """Called once the connection is ready."""
        # Subscribe to account summary for TotalCashValue and NetLiquidation
        self.reqAccountSummary(9001, "All", "TotalCashValue,NetLiquidation")

    # Streaming account summary values
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        self.account_summary.append((account, tag, value, currency))

    def accountSummaryEnd(self, reqId: int):
        # End of subscription – disconnect
        self.disconnect()


# Convenience function for one-shot usage

def fetch_account_summary(host: str = "127.0.0.1", port: int = 7497, client_id: int = 1):
    """Connect to TWS/Gateway and return account summary list."""
    app = IBKRClient()
    app.connect(host, port, client_id)
    app.run()  # blocks until accountSummaryEnd triggers disconnect
    return app.account_summary


if __name__ == "__main__":
    summary = fetch_account_summary()
    for account, tag, value, currency in summary:
        print(f"[{account}] {tag} = {value} {currency}")
