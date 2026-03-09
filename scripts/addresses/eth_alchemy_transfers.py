import asyncio
import httpx
import sys
import os
import random

# ===== CONFIG =====
API_KEY = "ee111vAO19WhZBGBR-3dV"

# Target address (incoming transfers)
ADDRESS = "0x109babe5fc1467774f03b53e3349f6359b236088".lower()

# Chain endpoint
BASE_URL = f"https://opbnb-mainnet.g.alchemy.com/v2/{API_KEY}"

# ERC20 Transfer event topic
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55aebd5b3efc"

# Address padded for topics
ADDRESS_TOPIC = "0x" + ADDRESS[2:].rjust(64, "0")

# Free tier friendly block step
BLOCK_STEP = 200  # adjust 100–500 for stability

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds

# Delay between requests
REQUEST_DELAY = 0.2  # seconds


# ===== UTILITY FUNCTIONS =====
async def get_block_number(client):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_blockNumber",
        "params": []
    }

    for i in range(MAX_RETRIES):
        try:
            r = await client.post(BASE_URL, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            return int(data["result"], 16)
        except Exception as e:
            print(f"[get_block_number] Retry {i+1}/{MAX_RETRIES} failed: {e}")
            await asyncio.sleep(RETRY_DELAY)
    raise RuntimeError("Failed to fetch latest block number")


async def get_logs(client, start, end):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getLogs",
        "params": [{
            "fromBlock": hex(start),
            "toBlock": hex(end),
            "topics": [
                TRANSFER_TOPIC,
                None,
                ADDRESS_TOPIC
            ]
        }]
    }

    for i in range(MAX_RETRIES):
        try:
            r = await client.post(BASE_URL, json=payload, timeout=30)
            r.raise_for_status()
            try:
                data = r.json()
            except Exception:
                print(f"[get_logs] Bad JSON response at blocks {start}-{end}")
                print("Response preview:", r.text[:500])
                await asyncio.sleep(RETRY_DELAY)
                continue

            if "error" in data:
                raise Exception(data["error"])

            return data.get("result", [])
        except Exception as e:
            print(f"[get_logs] Retry {i+1}/{MAX_RETRIES} for blocks {start}-{end} failed: {e}")
            await asyncio.sleep(RETRY_DELAY)
    return []


# ===== MAIN SCRIPT =====
async def main():
    unique_senders = set()

    async with httpx.AsyncClient(timeout=60.0) as client:
        latest_block = await get_block_number(client)
        print("Latest block:", latest_block)

        start = 0
        while start <= latest_block:
            end = min(start + BLOCK_STEP, latest_block)
            print(f"Scanning blocks {start} → {end}")

            logs = await get_logs(client, start, end)
            for log in logs:
                topic_from = log["topics"][1]
                addr = "0x" + topic_from[-40:]
                unique_senders.add(addr.lower())

            start = end + 1
            await asyncio.sleep(REQUEST_DELAY)

    print(f"Unique senders collected: {len(unique_senders)}")

    filename = "incoming_erc20_senders.txt"
    with open(filename, "w") as f:
        for addr in sorted(unique_senders):
            f.write(addr + "\n")
    print(f"Saved to {filename}")


if __name__ == "__main__":
    asyncio.run(main())