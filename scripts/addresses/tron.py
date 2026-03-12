import asyncio
import httpx

ADDRESS = "TPjJDf6nMjrmRxfW7wEQBM4tvVQag8RDCq"
URL = f"https://api.trongrid.io/v1/accounts/{ADDRESS}/transactions/trc20"

OUTPUT_FILE = "unique_senders_tron.txt"


async def main():
    unique_senders = set()
    fingerprint = None
    total = 0

    limits = httpx.Limits(max_connections=10, max_keepalive_connections=10)

    async with httpx.AsyncClient(timeout=60, limits=limits) as client:

        while True:

            params = {"limit": 200}

            if fingerprint:
                params["fingerprint"] = fingerprint

            try:
                r = await client.get(URL, params=params)

                if r.status_code == 429:
                    print("Rate limited — sleeping 5 seconds")
                    await asyncio.sleep(5)
                    continue

                r.raise_for_status()

            except Exception as e:
                print("Request error:", e)
                await asyncio.sleep(5)
                continue

            data = r.json()
            transfers = data.get("data", [])

            if not transfers:
                print("No more transfers")
                break

            for tx in transfers:
                sender = tx.get("from")
                if sender:
                    unique_senders.add(sender)

            total += len(transfers)

            meta = data.get("meta", {})
            fingerprint = meta.get("fingerprint")

            print(
                f"Processed {total} transfers | "
                f"Unique senders: {len(unique_senders)}"
            )

            if not fingerprint:
                break

            # small delay prevents most rate limits
            await asyncio.sleep(0.2)

    print("\nFinished scanning")
    print("Total transfers:", total)
    print("Unique senders:", len(unique_senders))

    with open(OUTPUT_FILE, "w") as f:
        for addr in sorted(unique_senders):
            f.write(addr + "\n")

    print("Saved to", OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(main())