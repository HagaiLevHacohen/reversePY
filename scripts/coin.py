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
    "BASE": CryptoCoin( # BASE
        symbol="ETH",
        chainId="BASE",
        contract="8453",
        memo=""
    ),
    "ARB": CryptoCoin( # ARBITUM
        symbol="ETH",
        chainId="ARETH",
        contract="42161",
        memo=""
    ),
    "OPT": CryptoCoin( # OPTIMISM
        symbol="ETH",
        chainId="OPTIMISM",
        contract="10",
        memo=""
    ),
    "TRON": CryptoCoin( # TRON
        symbol="USDT",
        chainId="TRX",
        contract="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        memo=""
    ),
    "POLY": CryptoCoin( # POLYGON
        symbol="USDT",
        chainId="POLYGON",
        contract="0xc2132d05d31c914a87c6611c10748aeb04b58e8f",
        memo=""
    ),
    "SOL": CryptoCoin( # SOLANA
        symbol="USDT",
        chainId="SOL",
        contract="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        memo=""
    ),
    "OPBNB": CryptoCoin( # OPBNB
        symbol="USDT",
        chainId="OPBNB",
        contract="0x9e5AAC1Ba1a2e6aEd6b32689DFcF62A509Ca96f3",
        memo=""
    ),
    "AVAX": CryptoCoin( # AVAX
        symbol="USDT",
        chainId="AVAX",
        contract="0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7",
        memo=""
    ),
}