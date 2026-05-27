from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

from .config import COINS, SLEEP_BETWEEN_COINS_SEC, VS_CURRENCY
from .data import fetch_daily_coin
from .indicators import compute_indicators
from .strategy import add_probability_scores_mean_reversion, generate_signals

def analyze_coin(coin_id: str, days: int = 180, vs: str = VS_CURRENCY, verbose: bool = False) -> Optional[pd.DataFrame]:
    df = fetch_daily_coin(coin_id, days=days, vs=vs, verbose=verbose)
    if df is None or df.empty:
        return None

    df = compute_indicators(df)
    df = add_probability_scores_mean_reversion(df)
    df = generate_signals(df)
    return df

def latest_row(coin_id: str, ticker: str, df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    return {
        "coin_id": coin_id,
        "ticker": ticker,
        "Date": df.index[-1].date(),
        "price": float(last["price"]),
        "Trend_State": str(last["Trend_State"]),
        "RSI": float(last["RSI"]),
        "RSI_State": str(last["RSI_State"]),
        "BB_State": str(last["BB_State"]),
        "BB_Squeeze": bool(last["BB_Squeeze"]),
        "Long_Score": float(last["Long_Score"]),
        "Short_Score": float(last["Short_Score"]),
        "Bias": str(last["Bias"]),
        "Watch": str(last["Watch"]),
        "Action": str(last["Action"]),
        "Signal": str(last["Signal"]),
    }

def run_all_coins(
    coins: Dict[str, str] = COINS,
    days: int = 180,
    vs: str = VS_CURRENCY,
    sleep_between: float = SLEEP_BETWEEN_COINS_SEC,
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Return latest_df, combined_df, and coin_cache."""
    rows = []
    frames = []
    coin_cache: Dict[str, pd.DataFrame] = {}

    for coin_id, ticker in coins.items():
        df = analyze_coin(coin_id, days=days, vs=vs, verbose=verbose)
        if df is None or df.empty:
            continue

        coin_cache[coin_id] = df
        rows.append(latest_row(coin_id, ticker, df))

        tmp = df.copy()
        tmp["coin_id"] = coin_id
        tmp["ticker"] = ticker
        frames.append(tmp)

        if sleep_between:
            time.sleep(sleep_between)

    latest_df = pd.DataFrame(rows)
    combined_df = pd.concat(frames, axis=0) if frames else pd.DataFrame()

    if not latest_df.empty:
        latest_df = latest_df.sort_values(["Action", "Long_Score", "Short_Score"], ascending=[True, False, False])

    return latest_df, combined_df, coin_cache

def export_coin_csv(df: pd.DataFrame, coin_id: str, ticker: str, out_dir: Path = Path("data") / "csv") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{ticker}_{coin_id}_mean_reversion.csv"
    df.to_csv(out_path)
    return out_path
