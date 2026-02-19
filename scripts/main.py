import base64
import json
import httpx
import asyncio
from post import post




def main():
    baseURL = "https://my.cwallet.com/cctip/v1/"
    endpoint = "account/other/user" # Note: endpoint SHOULDN'T begin with a /
    payload = {
    "id": "72349133"
    }
    authCookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2a21ucWJoamkzYmJ3OGM3OGJjc2g0b3c5Z2UiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ0ODI4ODMsImlhdCI6MTc3MTQxMDg4M30.AVP8J7y4coZAfuBnLUmnhePzuaCScEvU1EZwHl_MxKw"
    asyncio.run(post(baseURL, endpoint, payload, authCookie))


if __name__ == "__main__":
    main()
