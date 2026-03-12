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
# Proxy configuration
# ------------------------------

PROXIES = [
    None,  # your own IP
    ("2.59.20.98:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.35:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.107:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.72:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.124:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.128:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.153:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
    ("2.59.20.162:33333", "johnsmith943", "E3FD596E42DC9DFDAF4AAF9563089020"),
]

# ------------------------------
# Proxy rotator
# ------------------------------

class ProxyRotator:
    def __init__(self, clients):
        self.clients = clients
        self.index = 0

    def next(self):
        client = self.clients[self.index]
        self.index = (self.index + 1) % len(self.clients)
        return client

# ------------------------------
# Create http clients
# ------------------------------

def create_clients(timeout):
    clients = []

    for proxy in PROXIES:
        if proxy is None:
            clients.append(httpx.AsyncClient(timeout=timeout))
        else:
            host, user, password = proxy
            proxy_url = f"http://{user}:{password}@{host}"

            clients.append(
                httpx.AsyncClient(
                    timeout=timeout,
                    proxy=proxy_url
                )
            )

    return clients

# ------------------------------
# Robust HTTP fetch
# ------------------------------

async def fetch_with_retry(rotator, url, retries=5):
    for attempt in range(retries):
        client = rotator.next()

        try:
            resp = await client.get(url)

            if resp.status_code == 429:
                wait_time = 2 ** attempt
                print(f"[429] Rate limited. Waiting {wait_time}s before retrying {url}")
                await asyncio.sleep(wait_time)
                continue

            resp.raise_for_status()

            # small delay between requests
            await asyncio.sleep(0.34)

            return resp

        except (httpx.RequestError, httpx.TimeoutException) as e:
            if attempt < retries - 1:
                wait_time = 1.5 * (attempt + 1)
                print(f"[Retry] {e}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise

    raise Exception(f"Failed to fetch {url}")

# ------------------------------
# Get input addresses
# ------------------------------

async def get_all_inputs_of_outgoing(target_address, rotator):
    target_address = target_address.strip()
    collected_inputs = set()

    BASE = "https://mempool.space/api"
    next_url = f"{BASE}/address/{target_address}/txs"

    previous_last_txid = ""

    while next_url:
        try:
            resp = await fetch_with_retry(rotator, next_url)
            txs = resp.json()

        except Exception as e:
            print(f"[Partial] Error fetching {target_address}: {e}")
            print(f"[Partial] Returning {len(collected_inputs)} collected addresses")
            return collected_inputs

        if not txs:
            break

        try:
            for tx in txs:
                vin = tx.get("vin", [])

                is_outgoing = any(
                    inp.get("prevout", {}).get("scriptpubkey_address") == target_address
                    for inp in vin
                )

                if not is_outgoing:
                    continue

                for inp in vin:
                    addr = inp.get("prevout", {}).get("scriptpubkey_address")
                    if addr:
                        collected_inputs.add(addr)

        except Exception as e:
            print(f"[Partial] Parsing error for {target_address}: {e}")
            print(f"[Partial] Returning {len(collected_inputs)} collected addresses")
            return collected_inputs

        last_txid = txs[-1].get("txid")

        if not last_txid or last_txid == previous_last_txid:
            break

        previous_last_txid = last_txid
        next_url = f"{BASE}/address/{target_address}/txs/chain/{last_txid}"

    return collected_inputs

# ------------------------------
# Discover BTC addresses
# ------------------------------

async def btcExplore(inputFileName, outputFileName, processedFileName=None):
    addresses = set(read_addresses(getDataFilePath(inputFileName)))
    processed = set()

    if processedFileName:
        try:
            processed = set(read_addresses(getDataFilePath(processedFileName)))
            print(f"Loaded {len(processed)} processed addresses")

        except FileNotFoundError:
            print("Processed file not found")

    addresses = list(addresses - processed)
    print(f"{len(addresses)} addresses to explore")

    timeout = httpx.Timeout(connect=10, read=60, write=30, pool=10)
    clients = create_clients(timeout)
    rotator = ProxyRotator(clients)

    collected = set()
    total = len(addresses)

    for i, addr in enumerate(addresses):
        print(f"[{i+1}/{total}] Fetching {addr}")

        try:
            result = await get_all_inputs_of_outgoing(addr, rotator)
            collected.update(result)
            processed.add(addr)

        except Exception as e:
            print(f"Error with {addr}: {e}")

    new_addresses = collected - set(addresses)

    if new_addresses:
        print(f"Writing {len(new_addresses)} new addresses")

        with open(getDataFilePath(outputFileName), "a", encoding="utf-8") as f:
            for addr in sorted(new_addresses):
                f.write(addr + "\n")

    if processedFileName:
        with open(getDataFilePath(processedFileName), "w", encoding="utf-8") as f:
            for addr in sorted(processed):
                f.write(addr + "\n")

    for c in clients:
        await c.aclose()

    print("Exploration finished")


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
# Merge addresses
# ------------------------------

def mergeAddresses(inputFileName, outputFileName):
    input_addresses = set(read_addresses(getDataFilePath(inputFileName)))
    output_addresses = set(read_addresses(getDataFilePath(outputFileName)))

    new_addresses = input_addresses - output_addresses

    if not new_addresses:
        print("No new addresses")
        return

    print(f"Adding {len(new_addresses)} addresses")

    with open(getDataFilePath(outputFileName), "a", encoding="utf-8") as f:
        for addr in sorted(new_addresses):
            f.write(addr + "\n")

# ------------------------------
# CLI
# ------------------------------

print("Choose option:")
print("0 - Discover candidate BTC addresses")
print("1 - Filter internal BTC addresses")
print("2 - Merge new addresses")

choice = input("Enter choice: ")

if choice == "0":
    inputFileName = input("Input file: ")
    outputFileName = input("Output file: ")
    processedFileName = input("Processed file (optional): ")

    if processedFileName.strip() == "":
        processedFileName = None

    asyncio.run(btcExplore(inputFileName, outputFileName, processedFileName))

elif choice == "1":
    inputFileName = input("Input file with candidate BTC addresses: ")
    outputFileName = input("Output file for validated internal addresses: ")

    asyncio.run(filterBtcAddresses(inputFileName, outputFileName))

elif choice == "2":
    inputFileName = input("Input file: ")
    outputFileName = input("Output file: ")

    mergeAddresses(inputFileName, outputFileName)

else:
    print("Invalid option")