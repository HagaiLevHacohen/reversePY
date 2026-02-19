import requests
import time

API_KEY = "DRVZPFAJPBM2455Q7HEYZ2MR68BFPKNMFP"
ADDRESS = "0x935D2e470284Fb536227A76A723F96a94eFaE6A9".lower()  # the address you are monitoring

# Base URL for Etherscan API
BASE_URL = "https://api.etherscan.io/v2/api"

# Endpoints to fetch
ENDPOINTS = [
    {"action": "txlist", "name": "Normal ETH"},
    {"action": "txlistinternal", "name": "Internal"},
    {"action": "tokentx", "name": "ERC20 Token"},
    {"action": "tokennfttx", "name": "ERC721 NFT"},
]

unique_senders = set()

def fetch_paginated(action):
    """Fetch all pages for a given Etherscan API action."""
    page = 1
    offset = 1000  # number of results per page

    while True:
        params = {
            "module": "account",
            "chainid": "1",      # Ethereum mainnet
            "action": action,
            "address": ADDRESS,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": offset,
            "sort": "asc",
            "apikey": API_KEY
        }
        print(f"Page: {page}, offset: {offset}")

        resp = requests.get(BASE_URL, params=params).json()

        if resp.get("status") != "1" or not resp.get("result"):
            # no more results
            return
        
        results = resp["result"]

        # loop through results and grab incoming transactions
        for tx in results:
            to_addr = tx.get("to")
            if to_addr and to_addr.lower() == ADDRESS:
                from_addr = tx.get("from")
                if from_addr:
                    unique_senders.add(from_addr.lower())

        page += 1

        # if fewer results than offset, we are done
        if len(results) < offset:
            return

        # small delay for rate limit
        time.sleep(0.35)

# Loop through each endpoint and collect senders
for ep in ENDPOINTS:
    print(f"Fetching {ep['name']}...")
    print(len(unique_senders))
    fetch_paginated(ep["action"])

# Write unique addresses to file
with open("unique_senders_eth.txt", "w") as file:
    for addr in sorted(unique_senders):
        file.write(addr + "\n")

print("Done! Unique senders stored in unique_senders_eth.txt")
