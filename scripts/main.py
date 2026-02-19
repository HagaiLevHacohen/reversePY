import asyncio
from post import post
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



def main():
    authCookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjk2MzI3NmZnejg5M2pieWhibTh6YWplc3dwZXBqeSIsInNlc3Npb25faWQiOiI0MDk2N3NxZzltcXpiaWJzanE1YW0zNnhkNHJhaGUiLCJwbGF0Zm9ybSI6ImVtYWlsIiwicm9sZXMiOiIiLCJwcm9wcyI6eyJib3RJZCI6IiIsImhlYWRVcmwiOiIiLCJuaWNrbmFtZSI6IiJ9LCJleHAiOjE4MzQ1NjQ2MDYsImlhdCI6MTc3MTQ5MjYwNn0.WaYNCgKpUPE-PTSDivVkK3G4XpgH1YcJGRa52AYlijs"
    client = CWalletClient(authCookie=authCookie, payPassCode="111111")

    targetAddress = "0x4bfc2af88c133f4c7abf5a6799d9ea920056b65b"
    amount = "0.0000011"
    cryptoCoin = COINS["ETH"]
    userId = asyncio.run(client.executeFullTransaction(targetAddress, amount, cryptoCoin))
    print(userId)


if __name__ == "__main__":
    setup_logging(enabled=True)
    main()
