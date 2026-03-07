import asyncio
import httpx
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from scripts.proxy import get_random_proxy

API_KEY = "ee111vAO19WhZBGBR-3dV"
ADDRESS = "0xe3b205DA6D47989538f03553BC394d941677ffd3".lower()
BASE_URL = f"https://base-mainnet.g.alchemy.com/v2/{API_KEY}"

async def main():
    unique_senders = set()
    page_key = None
    prev_page_key = None
    async with httpx.AsyncClient(timeout=60.0) as client:
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
                        "maxCount": "0x3e8",  # 1000 per page
                        "category": [
                            "external",
                            "erc20",
                            "erc721",
                            "erc1155"
                        ],
                        **({"pageKey": page_key} if page_key else {})
                    }
                ],
            }

            try:
                response = await client.post(BASE_URL, json=payload)
                response.raise_for_status()
            except httpx.HTTPError as e:
                print("HTTP error:", str(e))
                break

            data = response.json()

            # Stop on RPC error
            if "error" in data:
                print("RPC error:", data["error"])
                break

            result = data.get("result", {})
            transfers = result.get("transfers", [])

            # Add senders
            for tx in transfers:
                from_addr = tx.get("from")
                if from_addr:
                    unique_senders.add(from_addr.lower())

            prev_page_key = page_key
            page_key = result.get("pageKey")

            # No more pages
            if not page_key:
                print("Finished — no more pageKey")
                break

            # Prevent infinite loop
            if page_key == prev_page_key:
                print("No progress on pagination — stopping")
                break

            # Small async delay (instead of time.sleep)
            await asyncio.sleep(0.1)

    print("Unique senders count:", len(unique_senders))

    with open("unique_senders_alchemy_base.txt", "w") as f:
        for addr in sorted(unique_senders):
            f.write(addr + "\n")

    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())