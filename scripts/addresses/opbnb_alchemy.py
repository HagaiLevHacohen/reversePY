import asyncio
import httpx
import os
import math

API_KEY = "ee111vAO19WhZBGBR-3dV"  # replace with your Alchemy API key
ADDRESS = "0x109babe5fc1467774f03b53e3349f6359b236088".lower()
BASE_URL = f"https://opbnb-mainnet.g.alchemy.com/v2/{API_KEY}"

# Transfer event signature for ERC20/ERC721/ERC1155
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# Number of blocks per batch
BATCH_SIZE = 1

async def fetch_logs(client, from_block, to_block):
    """Fetch logs in a block range."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getLogs",
        "params": [
            {
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "topics": [
                    TRANSFER_TOPIC,
                    None,
                    "0x000000000000000000000000" + ADDRESS[2:]
                ],
            }
        ],
    }
    try:
        resp = await client.post(BASE_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            print(f"RPC error: {data['error']}")
            return []
        return data.get("result", [])
    except Exception as e:
        print(f"Error fetching blocks {from_block}-{to_block}: {e}")
        return []

async def get_latest_block(client):
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}
    resp = await client.post(BASE_URL, json=payload)
    resp.raise_for_status()
    return int(resp.json()["result"], 16)

async def main():
    async with httpx.AsyncClient(timeout=120.0) as client:
        latest_block = await get_latest_block(client)
        print(f"Latest block: {latest_block}")

        # Prepare block ranges
        ranges = []
        for start in range(0, latest_block + 1, BATCH_SIZE):
            end = min(start + BATCH_SIZE - 1, latest_block)
            ranges.append((start, end))

        print(f"Fetching logs in {len(ranges)} batches...")

        # Fetch all logs concurrently
        unique_senders = set()
        for i in range(0, len(ranges), 10):  # 10 batches at a time to avoid overload
            batch = ranges[i:i+10]
            tasks = [fetch_logs(client, f, t) for f, t in batch]
            results = await asyncio.gather(*tasks)
            for logs in results:
                for log in logs:
                    # log["topics"][1] is the sender address
                    sender = "0x" + log["topics"][1][-40:]
                    unique_senders.add(sender.lower())
            print(f"Processed batches {i+1}-{i+len(batch)} | Unique senders so far: {len(unique_senders)}")

        # Save to file
        with open("unique_senders_opbnb.txt", "w") as f:
            for addr in sorted(unique_senders):
                f.write(addr + "\n")

        print(f"Done! Total unique senders: {len(unique_senders)}")

if __name__ == "__main__":
    asyncio.run(main())