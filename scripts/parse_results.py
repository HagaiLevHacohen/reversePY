import csv
import json
from script import getDataFilePath


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
            if raw_result == "null" or raw_result is None:
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



print_address_email(read_results_csv("results_eth.txt"))