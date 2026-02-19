import base64
import json
import httpx
import asyncio
from post import post
from attack import CWalletClient



def main():
    authCookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2N3NxZzltcXpiaWJzanE1YW0zNnhkNHJhaGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ1NjQ2MDYsImlhdCI6MTc3MTQ5MjYwNn0.WaYNCgKpUPE-PTSDivVkK3G4XpgH1YcJGRa52AYlijs"
    client = CWalletClient(authCookie=authCookie, payPassCode="111111")
    # Wrap the async call in asyncio.run()
    address = "0x2a8435c5D3607F9b8DA7E778f5bcd62cEb57b337"
    chainId = "ETH"
    contract = "1"
    memo = ""
    is_inner = asyncio.run(client.checkInnerAddress(address, chainId, contract, memo))
    print(is_inner)


if __name__ == "__main__":
    main()
