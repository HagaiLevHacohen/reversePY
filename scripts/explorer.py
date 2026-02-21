from coin import CryptoCoin
from attack import CWalletClient
from script import read_addresses, getDataFilePath
from coin import COINS
import asyncio
import httpx


async def fetch_with_retry(client, url, retries=3):
    for attempt in range(retries):
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp
        except (httpx.RequestError, httpx.TimeoutException) as e:
            if attempt < retries - 1:
                await asyncio.sleep(1.5 * (attempt + 1))  # backoff
            else:
                raise



async def get_all_inputs_of_outgoing(target_address: str) -> set[str]:
    """
    For a Bitcoin address:
    - Find all outgoing transactions (where address appears in vin)
    - Collect ALL input addresses from those transactions
    - Return as a set
    """

    target_address = target_address.strip()
    collected_inputs = set()

    base_url = f"https://blockstream.info/api/address/{target_address}/txs"
    next_url = base_url

    timeout = httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        previous_last_txid = ""
        while next_url:
            resp = await fetch_with_retry(client, next_url)
            if resp.status_code != 200:
                print("HTTP error:", resp.status_code)
                break

            txs = resp.json()
            if not txs:
                break

            print(f"Fetched {len(txs)} transactions")

            for tx in txs:
                vin = tx.get("vin", [])

                # Check if THIS transaction is outgoing
                is_outgoing = any(inp.get("prevout", {}).get("scriptpubkey_address") == target_address for inp in vin)

                if not is_outgoing:
                    continue

                # Collect ALL input addresses of this outgoing transaction
                for inp in vin:
                    prevout = inp.get("prevout", {})
                    addr = prevout.get("scriptpubkey_address")
                    if addr:
                        collected_inputs.add(addr)

            # Pagination
            last_txid = txs[-1].get("txid")
            if not last_txid or last_txid == previous_last_txid:
                break
            previous_last_txid = last_txid
            next_url = f"https://blockstream.info/api/address/{target_address}/txs/chain/{last_txid}"

            await asyncio.sleep(0.2)

    return collected_inputs


async def btcExplore(addressesFileName: str) -> None:
    addresses_file = getDataFilePath(addressesFileName)
    addresses = read_addresses(addresses_file)
    inputs_of_outgoing_addresses = set()

    semaphore = asyncio.Semaphore(2)
    async def limited_get(address):
        async with semaphore:
            return await get_all_inputs_of_outgoing(address)
    tasks = [limited_get(address) for address in addresses]
    results = await asyncio.gather(*tasks)

    for result_set in results:
        inputs_of_outgoing_addresses.update(result_set)

    # Determine only NEW addresses
    new_addresses = set(inputs_of_outgoing_addresses) - set(addresses)

    if not new_addresses:
        print("No new addresses found.")
        return

    print(f"Writing {len(new_addresses)} new addresses to file...")

    results_file = getDataFilePath("btc_new_addresses.txt")
    with open(results_file, "w", encoding="utf-8") as f:
        for addr in sorted(new_addresses):
            f.write(f"{addr}\n")


async def filterBtcAddresses(addressesFileName: str) -> None:
    addresses_file = getDataFilePath(addressesFileName)
    addresses = read_addresses(addresses_file)

    authCookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2cWlrNjgzcXhyM2RmNWZjZWtoZHNxeDNqZG8iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ3Mjg5NjMsImlhdCI6MTc3MTY1Njk2M30._VPo1bI4P1kK_z5jS0N0S5Goi9bIzF3gBTmMOWQ2SL0"
    client = CWalletClient(authCookie=authCookie, payPassCode="111111")

    cryptoCoin = COINS["BTC"]
    print("Flitering addresses, Length - " + str(len(addresses)))
    inner_addresses = await client.filterInnerAddresses(list(addresses), cryptoCoin)

    if not inner_addresses:
        print("No new inner addresses found.")
        return

    print(f"Writing {len(inner_addresses)} new addresses to file...")

    results_file = getDataFilePath("btc_new_inner_addresses.txt")
    with open(results_file, "w", encoding="utf-8") as f:
        for addr in sorted(inner_addresses):
            f.write(f"{addr}\n")

asyncio.run(btcExplore("btc_new_addresses.txt"))