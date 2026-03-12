import asyncio
import httpx

# ===========================
# CONFIG
# ===========================
API_URL = "https://opbnb-mainnet.nodereal.io/v1/e5718d72aa2d45a6bfc07a5cf26d5e4f"
ADDRESS = "0x109babe5fc1467774f03b53e3349f6359b236088".lower()
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
BLOCK_BATCH = 20000      # Number of blocks per RPC call
CONCURRENCY = 8          # Number of parallel RPC calls
OUTPUT_FILE = "unique_senders_opbnb.txt"


# ===========================
# HELPERS
# ===========================
async def get_latest_block(client):
    payload = {
        "jsonrpc":"2.0",
        "id":1,
        "method":"eth_blockNumber",
        "params":[]
    }
    r = await client.post(API_URL, json=payload)
    r.raise_for_status()
    return int(r.json()["result"], 16)


async def fetch_logs(client, start, end):
    payload = {
        "jsonrpc":"2.0",
        "id":1,
        "method":"eth_getLogs",
        "params":[{
            "fromBlock": hex(start),
            "toBlock": hex(end),
            "topics":[
                TRANSFER_TOPIC,
                None,
                "0x000000000000000000000000" + ADDRESS[2:]
            ]
        }]
    }

    try:
        r = await client.post(API_URL, json=payload)
        if r.status_code == 429:  # rate-limited
            await asyncio.sleep(1)
            return []
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            print("RPC error:", data["error"])
            return []
        return data.get("result", [])
    except Exception as e:
        print(f"Error fetching blocks {start}-{end}:", e)
        return []


# ===========================
# MAIN
# ===========================
async def main():
    unique_senders = set()

    async with httpx.AsyncClient(timeout=120) as client:
        latest_block = await get_latest_block(client)
        print("Latest block:", latest_block)

        # Prepare block ranges
        ranges = [
            (i, min(i + BLOCK_BATCH - 1, latest_block))
            for i in range(0, latest_block + 1, BLOCK_BATCH)
        ]

        print("Total ranges to scan:", len(ranges))

        # Process in concurrent batches
        for i in range(0, len(ranges), CONCURRENCY):
            batch = ranges[i:i+CONCURRENCY]
            tasks = [fetch_logs(client, start, end) for start, end in batch]
            results = await asyncio.gather(*tasks)

            for logs in results:
                for log in logs:
                    sender = "0x" + log["topics"][1][-40:]
                    unique_senders.add(sender.lower())

            print(f"Processed {i+len(batch)}/{len(ranges)} ranges | Unique senders: {len(unique_senders)}")
            await asyncio.sleep(0.05)  # small delay to avoid rate-limit

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        for addr in sorted(unique_senders):
            f.write(addr + "\n")

    print("\nDone! Total unique senders:", len(unique_senders))


if __name__ == "__main__":
    asyncio.run(main())