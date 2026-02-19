import requests
import time

API_KEY = "ee111vAO19WhZBGBR-3dV"
ADDRESS = "0x935d2e470284fb536227a76a723f96a94efae6a9".lower()
BASE_URL = f"https://eth-mainnet.g.alchemy.com/v2/{API_KEY}"

unique_senders = set()
page_key = None
prev_page_key = None

while True:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "toAddress": ADDRESS,
                "excludeZeroValue": False,
                "withMetadata": True,
                "maxCount": "0x3e8",  # 1000 results per page
                "category": [
                    "external",
                    "internal",
                    "erc20",
                    "erc721",
                    "erc1155"
                ],
                **({"pageKey": page_key} if page_key else {})
            }
        ],
    }

    response = requests.post(BASE_URL, json=payload)
    if response.status_code != 200:
        print("HTTP error:", response.status_code)
        break

    data = response.json()

    # Stop on API error
    if "error" in data:
        print("RPC error:", data["error"])
        break

    result = data.get("result", {})
    transfers = result.get("transfers", [])

    # Add all senders
    for tx in transfers:
        from_addr = tx.get("from")
        if from_addr:
            unique_senders.add(from_addr.lower())

    prev_page_key = page_key
    page_key = result.get("pageKey")

    # No more pages — done
    if not page_key:
        print("Finished — no more pageKey")
        break

    # Break if pageKey didn’t change (no progress)
    if page_key == prev_page_key:
        print("No progress on pagination — stopping to avoid infinite loop")
        break

    # Respect TTL (10 min) by querying quickly
    time.sleep(0.1)

print("Unique senders count:", len(unique_senders))

with open("unique_senders_alchemy.txt", "w") as f:
    for addr in sorted(unique_senders):
        f.write(addr + "\n")

print("Done!")
