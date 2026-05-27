from dataclasses import dataclass
from pathlib import Path
from typing import Dict

COINS: Dict[str, str] = {
    "bonk": "BONK",
    "bitcoin": "BTC",
    "chainlink": "LINK",
    "cardano": "ADA",
    "ripple": "XRP",
    "ondo-finance": "ONDO",
    "ethereum": "ETH",
    "solana": "SOL",
}

VS_CURRENCY = "usd"

DAYS_DEFAULT = 180

RSI_LEN = 14
EMA_FAST = 10
EMA_SLOW = 30
OVERBOUGHT = 70
OVERSOLD = 30

BB_LEN = 20
BB_STD = 2.0

SQUEEZE_LOOKBACK = 120
SQUEEZE_Q = 0.10

WATCH_THRESHOLD = 70

SLEEP_BETWEEN_COINS_SEC = 1.2
MAX_429_RETRIES = 5

@dataclass(frozen=True)
class FetchConfig:
    vs_currency: str = VS_CURRENCY
    days: int = DAYS_DEFAULT
    timeout: int = 20
    max_429_retries: int = MAX_429_RETRIES

@dataclass(frozen=True)
class ExportConfig:
    out_dir: Path = Path("data") / "csv"
    enabled: bool = False
