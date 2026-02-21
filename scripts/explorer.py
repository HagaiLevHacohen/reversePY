from coin import CryptoCoin
from attack import CWalletClient
import asyncio
import httpx

async def filterInnerAddresses(addresses: list[str], client: CWalletClient, cryptoCoin: CryptoCoin) -> list[str]:
    tasks = []
    for address in addresses:
        tasks.append(client.checkInnerAddress(address, cryptoCoin))

    results = await asyncio.gather(*tasks)

    # Keep only addresses where checkInnerAddress returned True
    return [address for address, is_inner in zip(addresses, results) if is_inner]


async def get_all_inputs_of_outgoing(target_address: str) -> set:
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

    async with httpx.AsyncClient(timeout=60.0) as client:

        while next_url:
            resp = await client.get(next_url)
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
            last_txid = txs[-1]["txid"]
            next_url = f"https://blockstream.info/api/address/{target_address}/txs/chain/{last_txid}"

            await asyncio.sleep(0.2)

    return collected_inputs



