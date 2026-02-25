import csv
import json
from pathlib import Path


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


def read_userIds_rows(file_path: Path) -> list[str]:
    """
    Reads a csv file containing: address, userId, timestamp
    and returns a list of rows of data.
    """
    rows = []
    if not file_path.exists():
        return rows

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            userId = row["userId"]
            if userId != "" and userId is not None:
                rows.append(row)

    return rows


def read_processed_userIds(results_file: Path) -> set[str]:
    """
    Reads processed userIds from results CSV file.
    Returns a set for fast lookup.
    """
    processed = set()

    if not results_file.exists():
        return processed

    with open(results_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed.add(str(json.loads(row["result"]).get("id")))

    return processed



def read_results_csv(file_name: str):
    results = []
    file_path = getDataFilePath(file_name)

    with open(file_path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            address = row["address"]
            raw_result = row["result"]
            timestamp = row.get("timestamp")  # safely read timestamp

            # Handle null values
            if raw_result == "" or raw_result is None:
                parsed_result = None
            else:
                parsed_result = json.loads(raw_result)

            results.append({
                "address": address,
                "result": parsed_result,
                "timestamp": timestamp
            })

    return results


def print_address_email(data):
    for row in data:
        address = row["address"]
        result = row["result"]
        timestamp = row.get("timestamp")

        if result and result.get("email"):
            email = result["email"]
        else:
            email = None

        print(f"[{timestamp}] {address}: {email}")


# print_address_email(read_results_csv("results_eth_two.txt"))