import asyncio
import httpx

API_KEY = "44bc564e-22d7-4881-a274-591a50715f4c"  # Your Helius API Key
ADDRESS = "AHXDVNdFAaMrBMnSiBLQT6MGsvPS4aSne5FV7DSP4BWt"

URL = f"https://api.helius.xyz/v0/addresses/{ADDRESS}/transactions"
OUTPUT_FILE = "unique_senders_solana.txt"


async def main():
    unique_senders = set()
    before = None
    total = 0

    async with httpx.AsyncClient(timeout=60) as client:

        while True:
            params = {
                "limit": 100,
                "api-key": API_KEY
            }
            if before:
                params["before"] = before

            try:
                r = await client.get(URL, params=params)

                if r.status_code == 429:
                    print("Rate limited — sleeping 5 seconds...")
                    await asyncio.sleep(5)
                    continue

                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                print("HTTP error:", e)
                await asyncio.sleep(5)
                continue
            except Exception as e:
                print("Request failed:", e)
                await asyncio.sleep(5)
                continue

            txs = r.json()

            if not txs:
                print("Finished — no more transactions")
                break

            for tx in txs:
                sender = tx.get("feePayer")
                if sender:
                    unique_senders.add(sender)
                total += 1

            print(f"Transactions scanned: {total} | Unique senders: {len(unique_senders)}")

            before = txs[-1]["signature"]

            # small delay to avoid hitting rate limit
            await asyncio.sleep(0.2)

    print("\nDone scanning!")
    print("Total transactions scanned:", total)
    print("Unique senders:", len(unique_senders))

    with open(OUTPUT_FILE, "w") as f:
        for addr in sorted(unique_senders):
            f.write(addr + "\n")

    print(f"Saved unique senders to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())