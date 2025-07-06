from financial_investing_platform.interactive_brokers import fetch_account_summary

if __name__ == "__main__":
    summary = fetch_account_summary()
    if not summary:
        print("No data returned. Make sure TWS or IB Gateway is running and API access is enabled.")
    else:
        for account, tag, value, currency in summary:
            print(f"[{account}] {tag} = {value} {currency}")
