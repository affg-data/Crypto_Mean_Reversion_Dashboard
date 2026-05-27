from __future__ import annotations

import json
import time
from typing import Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import MAX_429_RETRIES, VS_CURRENCY, DAYS_DEFAULT

def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update({
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (crypto-mean-reversion-dashboard)",
    })
    return session

SESSION = make_session()

def fetch_daily_coin(
    coin_id: str,
    days: int = DAYS_DEFAULT,
    vs: str = VS_CURRENCY,
    *,
    timeout: int = 20,
    max_429_retries: int = MAX_429_RETRIES,
    session: Optional[requests.Session] = None,
    verbose: bool = False,
) -> Optional[pd.DataFrame]:
    """Fetch CoinGecko market_chart data and return daily close prices."""
    sess = session or SESSION
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs, "days": str(days)}

    for attempt in range(1, max_429_retries + 1):
        try:
            response = sess.get(url, params=params, timeout=timeout)
            status = response.status_code

            if verbose:
                print(f"[fetch {coin_id}] status={status}")

            if status == 429:
                sleep_s = min(2 ** attempt, 30)
                if verbose:
                    print(f"[fetch {coin_id}] rate limited. sleeping {sleep_s}s.")
                time.sleep(sleep_s)
                continue

            if status != 200:
                if verbose:
                    print(f"[fetch {coin_id}] HTTP {status}: {response.text[:300]}")
                return None

            data = response.json()

        except Exception as exc:
            if verbose:
                print(f"[fetch {coin_id}] request error: {exc}")
            return None

        if not isinstance(data, dict) or "prices" not in data:
            if verbose:
                print(f"[fetch {coin_id}] unexpected JSON: {json.dumps(data)[:600]}")
            return None

        df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp").sort_index()
        df = df.resample("1D").last().dropna()

        return df

    if verbose:
        print(f"[fetch {coin_id}] gave up after {max_429_retries} retries.")
    return None
