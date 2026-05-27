from __future__ import annotations

import numpy as np
import pandas as pd

from .config import (
    BB_LEN,
    BB_STD,
    EMA_FAST,
    EMA_SLOW,
    OVERBOUGHT,
    OVERSOLD,
    RSI_LEN,
    SQUEEZE_LOOKBACK,
    SQUEEZE_Q,
)

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

def rsi_wilder(series: pd.Series, length: int = RSI_LEN) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def bollinger_bands(series: pd.Series, length: int = BB_LEN, std_mult: float = BB_STD):
    mid = series.rolling(length).mean()
    std = series.rolling(length).std()
    upper = mid + std_mult * std
    lower = mid - std_mult * std
    return mid, upper, lower

def add_bb_squeeze(df: pd.DataFrame, lookback: int = SQUEEZE_LOOKBACK, q: float = SQUEEZE_Q) -> pd.DataFrame:
    df = df.copy()
    df["BB_Width"] = (df["BB_Upper"] - df["BB_Lower"]) / df["BB_Mid"].replace(0, np.nan)
    df["BB_Width_Thresh"] = df["BB_Width"].rolling(lookback).quantile(q)
    df["BB_Squeeze"] = (df["BB_Width"] <= df["BB_Width_Thresh"]).fillna(False).astype(bool)

    previous_squeeze = df["BB_Squeeze"].shift(1, fill_value=False).astype(bool)
    df["BB_Squeeze_Release"] = (previous_squeeze & (~df["BB_Squeeze"])).astype(bool)
    return df

def add_bb_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    denom = (df["BB_Upper"] - df["BB_Lower"]).replace(0, np.nan)
    df["BB_PctB"] = (df["price"] - df["BB_Lower"]) / denom

    implied_std = (df["BB_Upper"] - df["BB_Mid"]) / BB_STD
    df["BB_Z"] = (df["price"] - df["BB_Mid"]) / implied_std.replace(0, np.nan)
    return df

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["EMA_fast"] = ema(df["price"], EMA_FAST)
    df["EMA_slow"] = ema(df["price"], EMA_SLOW)

    df["RSI"] = rsi_wilder(df["price"], RSI_LEN)

    df["BB_Mid"], df["BB_Upper"], df["BB_Lower"] = bollinger_bands(df["price"], BB_LEN, BB_STD)

    df["RSI_State"] = "Neutral"
    df.loc[df["RSI"] >= OVERBOUGHT, "RSI_State"] = "Overbought"
    df.loc[df["RSI"] <= OVERSOLD, "RSI_State"] = "Oversold"

    df["Trend_State"] = "Neutral"
    df.loc[df["EMA_fast"] > df["EMA_slow"], "Trend_State"] = "Bullish"
    df.loc[df["EMA_fast"] < df["EMA_slow"], "Trend_State"] = "Bearish"

    df["BB_State"] = "Inside"
    df.loc[df["price"] >= df["BB_Upper"], "BB_State"] = "Above Upper"
    df.loc[df["price"] <= df["BB_Lower"], "BB_State"] = "Below Lower"

    df = add_bb_squeeze(df)
    df = add_bb_metrics(df)

    return df
