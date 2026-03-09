import asyncio
import httpx
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from scripts.proxy import get_random_proxy

API_KEY = "ee111vAO19WhZBGBR-3dV"

ADDRESS = "AHXDVNdFAaMrBMnSiBLQT6MGsvPS4aSne5FV7DSP4BWt"

BASE_URL = f"https://solana-mainnet.g.alchemy.com/v2/{API_KEY}"


async def rpc_call(client, method, params):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }

    response = await client.post(BASE_URL, json=payload)
    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise Exception(data["error"])

    return data["result"]


async def main():
    unique_senders = set()
    before = None
    total_scanned = 0

    async with httpx.AsyncClient(timeout=60.0) as client:

        while True:

            params = [
                ADDRESS,
                {
                    "limit": 1000,
                    **({"before": before} if before else {})
                }
            ]

            try:
                signatures = await rpc_call(client, "getSignaturesForAddress", params)
            except Exception as e:
                print("RPC error:", e)
                break

            if not signatures:
                print("Finished — no more signatures")
                break

            for entry in signatures:

                sig = entry["signature"]

                try:
                    tx = await rpc_call(
                        client,
                        "getTransaction",
                        [
                            sig,
                            {
                                "encoding": "json",
                                "maxSupportedTransactionVersion": 0
                            }
                        ]
                    )
                except Exception as e:
                    print("Transaction fetch error:", e)
                    continue

                if not tx:
                    continue

                try:
                    message = tx["transaction"]["message"]
                    account_keys = message["accountKeys"]

                    sender = account_keys[0]
                    unique_senders.add(sender)

                except Exception:
                    continue

                total_scanned += 1

                if total_scanned % 100 == 0:
                    print("Transactions scanned:", total_scanned)

            before = signatures[-1]["signature"]

            await asyncio.sleep(0.1)

    print("Unique senders count:", len(unique_senders))

    with open("unique_senders_solana.txt", "w") as f:
        for addr in sorted(unique_senders):
            f.write(addr + "\n")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())