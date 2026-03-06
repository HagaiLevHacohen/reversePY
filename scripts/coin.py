class CryptoCoin:
    def __init__(
        self,
        symbol: str,
        chainId: str,
        contract: str = "",
        memo: str = "",
    ):
        self.symbol = symbol          # e.g. "ETH"
        self.chainId = chainId      # e.g. "ETH"
        self.contract = contract      # contract address
        self.memo = memo                # default fee

    def __repr__(self):
        return f"<CryptoCoin {self.symbol} ({self.chainId})>"
    

COINS = {
    "ETH": CryptoCoin( # ERC20
        symbol="ETH",
        chainId="ETH",
        contract="1",
        memo=""
    ),
    "BTC": CryptoCoin( 
        symbol="BTC",
        chainId="BTC",
        contract="BTC",
        memo=""
    ),
    "BEP20": CryptoCoin( # BEP20
        symbol="ETH",
        chainId="BSC",
        contract="0x2170ed0880ac9a755fd29b2688956bd959f933f8",
        memo=""
    ),
}