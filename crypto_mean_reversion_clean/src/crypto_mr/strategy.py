from __future__ import annotations

import numpy as np
import pandas as pd

from .config import OVERBOUGHT, OVERSOLD, WATCH_THRESHOLD

def add_probability_scores_mean_reversion(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    rsi = df["RSI"]
    rsi_prev = rsi.shift(1)

    dip_strength = (-df["BB_PctB"]).clip(lower=0, upper=1)
    rip_strength = (df["BB_PctB"] - 1).clip(lower=0, upper=1)

    dip_z = ((-df["BB_Z"] - 2) / 2).clip(lower=0, upper=1)
    rip_z = ((df["BB_Z"] - 2) / 2).clip(lower=0, upper=1)

    stretch_long = (0.55 * dip_strength + 0.45 * dip_z).fillna(0)
    stretch_short = (0.55 * rip_strength + 0.45 * rip_z).fillna(0)

    rsi_oversold = ((30 - rsi) / 30).clip(lower=0, upper=1)
    rsi_overbought = ((rsi - 70) / 30).clip(lower=0, upper=1)

    rsi_turn_long = (rsi > rsi_prev).fillna(False).astype(float)
    rsi_turn_short = (rsi < rsi_prev).fillna(False).astype(float)

    trend = df["Trend_State"].fillna("Neutral")
    penalty_long = np.where(trend == "Bearish", 0.25, 0.0)
    penalty_short = np.where(trend == "Bullish", 0.25, 0.0)

    in_squeeze = df["BB_Squeeze"].fillna(False).astype(float) if "BB_Squeeze" in df.columns else 0.0
    squeeze_caution = in_squeeze * 0.15

    long_raw = (0.55 * stretch_long + 0.35 * rsi_oversold + 0.10 * rsi_turn_long).clip(0, 1)
    short_raw = (0.55 * stretch_short + 0.35 * rsi_overbought + 0.10 * rsi_turn_short).clip(0, 1)

    long_raw = (long_raw * (1 - penalty_long) * (1 - squeeze_caution)).clip(0, 1)
    short_raw = (short_raw * (1 - penalty_short) * (1 - squeeze_caution)).clip(0, 1)

    df["Long_Score"] = (100 * long_raw).round(1)
    df["Short_Score"] = (100 * short_raw).round(1)

    df["Bias"] = np.where(
        df["Long_Score"] > df["Short_Score"],
        "LONG",
        np.where(df["Short_Score"] > df["Long_Score"], "SHORT", "NEUTRAL"),
    )

    df["Watch"] = ""
    df.loc[df["Long_Score"] >= WATCH_THRESHOLD, "Watch"] = "BUY THE DIP"
    df.loc[df["Short_Score"] >= WATCH_THRESHOLD, "Watch"] = "SELL THE RIP"

    df["Action"] = ""
    df.loc[(df["Watch"] == "BUY THE DIP") & (df["Trend_State"] != "Bearish"), "Action"] = "BUY"
    df.loc[(df["Watch"] == "SELL THE RIP") & (df["Trend_State"] != "Bullish"), "Action"] = "SELL"

    return df

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["ema_bull"] = (df["EMA_fast"] > df["EMA_slow"]).astype(bool)
    df["ema_bear"] = (df["EMA_fast"] < df["EMA_slow"]).astype(bool)

    prev_bull = df["ema_bull"].shift(1, fill_value=False).astype(bool)
    prev_bear = df["ema_bear"].shift(1, fill_value=False).astype(bool)

    buy_cross = (df["ema_bull"] & (~prev_bull) & (df["RSI"] < OVERBOUGHT)).astype(bool)
    sell_cross = (df["ema_bear"] & (~prev_bear) & (df["RSI"] > OVERSOLD)).astype(bool)

    rsi_buy = ((df["RSI"].shift(1) < OVERSOLD) & (df["RSI"] >= OVERSOLD)).fillna(False).astype(bool)
    rsi_sell = ((df["RSI"].shift(1) > OVERBOUGHT) & (df["RSI"] <= OVERBOUGHT)).fillna(False).astype(bool)

    df["Signal"] = ""
    df.loc[buy_cross | rsi_buy, "Signal"] = "BUY"
    df.loc[sell_cross | rsi_sell, "Signal"] = "SELL"

    return df
