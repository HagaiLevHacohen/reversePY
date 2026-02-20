import requests
import time

# ------------------------
# CONFIGURATION
# ------------------------

API_KEY = "cqt_rQyFrrmc84hm6xyvkGcvvftBDyV8"  # replace with your actual API Key
TARGET_ADDRESS = "0x82916c48225948887faae3c4b6b819f6bf773ca2".lower()

# Chains to fetch history for
CHAINS = ["eth-mainnet", "bsc-mainnet"]  # e.g., Ethereum and BNB Smart Chain

# Unique senders set
unique_senders = set()

# ------------------------
# FETCH & PAGINATION
# ------------------------

def fetch_transactions_for_chain(chain):
    """
    Fetch all transactions for the given chain,
    then extract only incoming sender addresses.
    """
    page = 0

    while True:
        url = (
            f"https://api.covalenthq.com/v1/{chain}/address/{TARGET_ADDRESS}/"
            f"transactions_v3/page/{page}/"
        )
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"[{chain}] HTTP error {resp.status_code}:", resp.text)
            return

        data = resp.json()

        # "items" contains the list of transactions for this page
        items = data.get("data", {}).get("items", [])
        
        print(f"[{chain}] page {page}, fetched {len(items)} transactions")

        # no items => no more pages
        if not items:
            break

        # process items
        for tx in items:
            to_addr = tx.get("to_address") or ""
            if to_addr and to_addr.lower() == TARGET_ADDRESS:
                from_addr = tx.get("from_address")
                if from_addr:
                    unique_senders.add(from_addr.lower())

        page += 1

        # small delay to respect rate limits
        time.sleep(0.2)

# ------------------------
# MAIN LOOP
# ------------------------

for chain in CHAINS:
    print(f"\nFetching transactions for {chain}...")
    fetch_transactions_for_chain(chain)

print("\nDone!")
print("Unique senders count:", len(unique_senders))

# Save to file
with open("unique_senders_covalent.txt", "w") as f:
    for addr in sorted(unique_senders):
        f.write(addr + "\n")

print("Results written to unique_senders_covalent.txt")