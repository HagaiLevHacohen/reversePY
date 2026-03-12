import sys
import os

# Make sure scripts folder is in sys.path
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

import asyncio
import httpx

from attack import CWalletClient
from parse import read_addresses, getDataFilePath
from coin import COINS

# ------------------------------
# Helper: robust HTTP fetch with retries and 429 handling
# ------------------------------
async def fetch_with_retry(client, url, retries=5):
    for attempt in range(retries):
        try:
            resp = await client.get(url)
            if resp.status_code == 429:
                wait_time = 2 ** attempt
                print(f"[429] Rate limited. Waiting {wait_time}s before retrying {url}")
                await asyncio.sleep(wait_time)
                continue
            resp.raise_for_status()
            return resp
        except (httpx.RequestError, httpx.TimeoutException) as e:
            if attempt < retries - 1:
                wait_time = 1.5 * (attempt + 1)
                print(f"[Retry] {e}, waiting {wait_time}s before retrying {url}")
                await asyncio.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed to fetch {url} after {retries} retries")

# ------------------------------
# Get all input addresses of outgoing transactions
# ------------------------------
async def get_all_inputs_of_outgoing(target_address: str, client: httpx.AsyncClient) -> set[str]:
    target_address = target_address.strip()
    collected_inputs = set()
    base_url = f"https://blockstream.info/api/address/{target_address}/txs"
    next_url = base_url
    previous_last_txid = ""

    while next_url:
        resp = await fetch_with_retry(client, next_url)
        txs = resp.json()
        if not txs:
            break

        for tx in txs:
            vin = tx.get("vin", [])
            is_outgoing = any(inp.get("prevout", {}).get("scriptpubkey_address") == target_address for inp in vin)
            if not is_outgoing:
                continue
            for inp in vin:
                addr = inp.get("prevout", {}).get("scriptpubkey_address")
                if addr:
                    collected_inputs.add(addr)

        # Pagination
        last_txid = txs[-1].get("txid")
        if not last_txid or last_txid == previous_last_txid:
            break
        previous_last_txid = last_txid
        next_url = f"https://blockstream.info/api/address/{target_address}/txs/chain/{last_txid}"
        await asyncio.sleep(0.2)  # prevent rate limiting

    return collected_inputs

# ------------------------------
# Discover candidate BTC addresses
# ------------------------------
async def btcExplore(inputFileName: str, outputFileName: str, processedFileName: str | None = None):
    addresses = set(read_addresses(getDataFilePath(inputFileName)))

    processed = set()
    if processedFileName:
        try:
            processed = set(read_addresses(getDataFilePath(processedFileName)))
            print(f"Loaded {len(processed)} already processed addresses")
        except FileNotFoundError:
            print("Processed file not found, starting fresh")

    # remove processed addresses
    addresses = list(addresses - processed)

    print(f"{len(addresses)} addresses left to explore")

    collected = set()
    semaphore = asyncio.Semaphore(3)

    total = len(addresses)
    done_count = 0

    timeout = httpx.Timeout(connect=10, read=60, write=30, pool=10)
    async with httpx.AsyncClient(timeout=timeout) as client:

        async def limited(addr):
            nonlocal done_count
            async with semaphore:
                print(f"[{done_count}/{total}] Fetching {addr}")
                result = await get_all_inputs_of_outgoing(addr, client)
                done_count += 1
                print(f"[{done_count}/{total}] Done {addr}")
                return addr, result

        tasks = [limited(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)

        for addr, res in results:
            collected.update(res)
            processed.add(addr)

    new_addresses = collected - set(addresses)

    if new_addresses:
        print(f"Writing {len(new_addresses)} new addresses to {outputFileName}")
        with open(getDataFilePath(outputFileName), "a", encoding="utf-8") as f:
            for addr in sorted(new_addresses):
                f.write(addr + "\n")

    # update processed file
    if processedFileName:
        with open(getDataFilePath(processedFileName), "w", encoding="utf-8") as f:
            for addr in sorted(processed):
                f.write(addr + "\n")

    print("Exploration finished.")


# ------------------------------
# Filter internal BTC addresses
# ------------------------------
async def filterBtcAddresses(inputFileName: str, outputFileName: str):
    addresses = read_addresses(getDataFilePath(inputFileName))
    print(f"Filtering {len(addresses)} addresses for internal BTC")

    cookies = [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2ZGN5d2R0Z3d1dGQ1aWRoc3pxdXF4cWlhbW8iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzYxMzQ3NDUsImlhdCI6MTc3MzA2Mjc0NX0.vzAZrKh5wFRjGRPI8Wuht5xC8uYQ2M1BLVeC2QTaq5U", # Tina Smith
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJ6eXdxemJuNTlweXRpcmc2dW9xZHNiY3A5eSIsInNlc3Npb25faWQiOiI0MDk2bTM3NHd6bzQ0ZmczZGdoNDdlYXh5Y283eGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODI1MzAsImlhdCI6MTc3MjMxMDUzMH0.ljwEUieag9mYiVUNQS7oUqCX6_hCSAHsVO1Yj2HgW84", # John Smith
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3MjhkYmVlMzRuZ3BqYmF6cGt0YmExcTl0dzU4eSIsInNlc3Npb25faWQiOiI0MDk2a3I4bmI1ZXk0dGI1aWMxZWQ5a2Rpd3htc28iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODI2NzksImlhdCI6MTc3MjMxMDY3OX0.sZ9gImvVhfcrA3qxUItBW4goGZREbME7378FaAR3ASg", # Roger Smith
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIxdDhrNzliNnM3eWl0ajlveWs1ZnRva3pvYyIsInNlc3Npb25faWQiOiI0MDk2OTF6dGdpanJzZjh4M3FmdHdmbnBzNHl0dGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODI4MDUsImlhdCI6MTc3MjMxMDgwNX0.rKc474GiyNSgqAOH_LXGquwR7Y47tKUfLApLMkpk4-I", # 1
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIzYzQ0eWZhanJ0eTRmamhydTV3aG43NjRjZSIsInNlc3Npb25faWQiOiI0MDk2M201ZXFhaTNvdHl4N2YzdWkxaTFmMzFicm8iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODMwMjAsImlhdCI6MTc3MjMxMTAyMH0.wERHKpKjTCuzkbIHylS6vLCRYN4SZ_sYkI24n5tsQCo", # 2
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJiajh5ZnE5b3FmOHU1ZDVxd2NiOHgzenF5byIsInNlc3Npb25faWQiOiI0MDk2czF1M2hnN3FqdGd4enJvYmQzb3FkOWpyc28iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY1OTAsImlhdCI6MTc3MjMxNDU5MH0.wCHsmE1MeevGoMQHmgzxEIZ3sl5_THLUALxRmusl_hg", # 3
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3Mjhlczlvb3p5dW4zOG9kOGJ5cm83M3llbXhqYSIsInNlc3Npb25faWQiOiI0MDk2ejliOXJ1dDlucGJhcG4xZDN0Ym5oaWNtNGgiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY2ODAsImlhdCI6MTc3MjMxNDY4MH0.3i5AfuKnIbsCWmjr_RxRTzQsZpbAtwiv7EDCqZyGWtA", # 4
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3MjhkODhkZ3F5aGgzZ3d0Z3hjdWVqMWprd3dybyIsInNlc3Npb25faWQiOiI0MDk2YnQ2dWE0Y2traXI5OWpkc21temtwaTUxY2MiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY3ODAsImlhdCI6MTc3MjMxNDc4MH0.DhqL2QVMMPqgQVHWLxIbt7l6ejYr9mCL-ik5vB1YDNM", # 5
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJmOWVtM3g5ZGVmeTVqZ3locXByb3EzanNpbyIsInNlc3Npb25faWQiOiI0MDk2eDV5eWF3em93aWZ1N25ocWZzeHE1b3p6anIiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY4ODQsImlhdCI6MTc3MjMxNDg4NH0.CKfCTDwQXloUB3Y3AyS776tRDA22FlV-C7aathE-qaI", # 6
    ]

    cryptoCoin = COINS["BTC"]

    # Create one client per cookie
    clients = [
        CWalletClient(authCookie=cookie, payPassCode="111111")
        for cookie in cookies
    ]

    # Split addresses evenly between clients
    chunks = [[] for _ in clients]
    for i, addr in enumerate(addresses):
        chunks[i % len(clients)].append(addr)

    async def worker(client, addr_chunk, worker_id):
        print(f"Worker {worker_id}: processing {len(addr_chunk)} addresses")
        if not addr_chunk:
            return []
        result = await client.filterInnerAddresses(addr_chunk, cryptoCoin)
        print(f"Worker {worker_id}: finished")
        return result or []

    tasks = [
        worker(client, chunk, i)
        for i, (client, chunk) in enumerate(zip(clients, chunks))
    ]

    results = await asyncio.gather(*tasks)

    inner_addresses = set()
    for res in results:
        inner_addresses.update(res)

    if not inner_addresses:
        print("No internal addresses found.")
        return

    print(f"Writing {len(inner_addresses)} internal addresses to {outputFileName}")
    with open(getDataFilePath(outputFileName), "w", encoding="utf-8") as f:
        for addr in sorted(inner_addresses):
            f.write(addr + "\n")


# ------------------------------
# Merge new addresses into existing file
# ------------------------------
def mergeAddresses(inputFileName: str, outputFileName: str):
    input_addresses = set(read_addresses(getDataFilePath(inputFileName)))
    output_addresses = set(read_addresses(getDataFilePath(outputFileName)))

    new_addresses = input_addresses - output_addresses
    if not new_addresses:
        print("No new addresses to merge.")
        return

    print(f"Adding {len(new_addresses)} new addresses to {outputFileName}")
    with open(getDataFilePath(outputFileName), "a", encoding="utf-8") as f:
        for addr in sorted(new_addresses):
            f.write(addr + "\n")



# ------------------------------
# CLI menu
# ------------------------------
print("Choose option:")
print("0 - Discover candidate BTC addresses")
print("1 - Filter internal BTC addresses")
print("2 - Merge new addresses into existing file")  # new option

choice = input("Enter choice: ")


if choice == "0":
    inputFileName = input("Input file with initial BTC addresses: ")
    outputFileName = input("Output file for candidate addresses: ")
    processedFileName = input("File with already processed addresses (or leave empty): ")

    if processedFileName.strip() == "":
        processedFileName = None

    asyncio.run(btcExplore(inputFileName, outputFileName, processedFileName))

elif choice == "1":
    inputFileName = input("Input file with candidate BTC addresses: ")
    outputFileName = input("Output file for validated internal addresses: ")
    asyncio.run(filterBtcAddresses(inputFileName, outputFileName))

elif choice == "2":
    inputFileName = input("Input file with new addresses: ")
    outputFileName = input("Output file to merge into: ")
    mergeAddresses(inputFileName, outputFileName)

else:
    print("Invalid option")