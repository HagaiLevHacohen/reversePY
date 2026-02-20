import asyncio
import httpx
import time
from asyncio import Lock

# ------------------------
# CONFIGURATION
# ------------------------

API_KEY = "cqt_rQyFrrmc84hm6xyvkGcvvftBDyV8"  # Replace with your actual GoldRush/Covalent API key
TARGET_ADDRESS = "0x82916c48225948887faae3c4b6b819f6bf773ca2".lower()

# Chains to fetch history for
CHAINS = ["eth-mainnet", "bsc-mainnet"]

# File to write results
OUTPUT_FILE = "unique_senders_covalent_async.txt"

# ------------------------
# GLOBALS
# ------------------------
unique_senders = set()
write_lock = Lock()  # async lock to prevent simultaneous writes

# ------------------------
# ASYNC FETCH
# ------------------------

async def fetch_chain_transactions(client: httpx.AsyncClient, chain: str):
    """
    Fetch all paginated transactions for a chain following the "links.next" URL.
    Writes unique senders to file as they are found.
    """
    next_url = (
        f"https://api.covalenthq.com/v1/{chain}/address/{TARGET_ADDRESS}/"
        f"transactions_v3/page/0/"
    )
    headers = {"Authorization": f"Bearer {API_KEY}"}
    page_counter = 0

    while next_url:
        try:
            resp = await client.get(next_url, headers=headers)
        except Exception as e:
            print(f"[{chain}] Request error:", e)
            break

        if resp.status_code != 200:
            print(f"[{chain}] HTTP error {resp.status_code}:", await resp.text())
            break

        data = resp.json()
        items = data.get("data", {}).get("items", [])

        print(f"[{chain}] page {page_counter}, fetched {len(items)} transactions")

        for tx in items:
            to_addr = tx.get("to_address") or ""
            if to_addr.lower() == TARGET_ADDRESS:
                from_addr = tx.get("from_address")
                if from_addr:
                    from_addr = from_addr.lower()
                    if from_addr not in unique_senders:
                        unique_senders.add(from_addr)
                        # Write immediately
                        async with write_lock:
                            with open(OUTPUT_FILE, "a") as f:
                                f.write(from_addr + "\n")

        links = data.get("data", {}).get("links", {})
        next_url = links.get("next")
        page_counter += 1

        await asyncio.sleep(0.1)  # avoid rate limits

# ------------------------
# MAIN LOOP
# ------------------------

async def main():
    # Clear output file at start
    with open(OUTPUT_FILE, "w") as f:
        f.write("")

    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [fetch_chain_transactions(client, chain) for chain in CHAINS]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print("\nDone!")
    print("Unique senders count:", len(unique_senders))
    print(f"Results written incrementally to {OUTPUT_FILE}")
    print(f"Elapsed time: {time.time() - start_time:.2f} seconds")