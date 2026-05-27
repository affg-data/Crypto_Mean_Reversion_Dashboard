from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from src.crypto_mr.config import COINS, VS_CURRENCY
from src.crypto_mr.pipeline import analyze_coin, run_all_coins
from src.crypto_mr.plotting import make_price_chart, make_rsi_chart

st.set_page_config(page_title="Mean-Reversion Crypto Dashboard", layout="wide")

st.title("📉 Mean-Reversion Crypto Dashboard")
st.caption("Buy-dip / sell-rip scanner using EMA trend state, RSI, Bollinger Band stretch, and squeeze caution.")

with st.sidebar:
    st.header("Controls")
    coin = st.selectbox(
        "Coin",
        options=list(COINS.keys()),
        format_func=lambda k: f"{COINS[k]} ({k})",
    )
    days = st.slider("History window", 60, 365, 180, step=30)
    show_table_rows = st.slider("Rows to show", 10, 200, 30, step=10)
    show_rsi = st.checkbox("Show RSI chart", value=True)
    scan_all = st.checkbox("Scan all coins", value=True)
    clear_cache = st.button("Clear cache")

if clear_cache:
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=60)
def load_one_coin(coin_id: str, days: int):
    return analyze_coin(coin_id, days=days, vs=VS_CURRENCY, verbose=False)

@st.cache_data(ttl=90)
def load_all_coins(days: int):
    latest_df, combined_df, _ = run_all_coins(days=days, vs=VS_CURRENCY, sleep_between=0.2, verbose=False)
    return latest_df, combined_df

df = load_one_coin(coin, days)

if df is None or df.empty:
    st.error(f"Failed to load data for {coin}. You may be rate-limited by CoinGecko or the coin ID may be unavailable.")
    st.stop()

last = df.iloc[-1]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Ticker", COINS[coin])
c2.metric("Price", f"{last['price']:.8f}")
c3.metric("Trend", str(last["Trend_State"]))
c4.metric("RSI", f"{last['RSI']:.2f}", str(last["RSI_State"]))
c5.metric("Bias", str(last["Bias"]))
c6.metric("Action", str(last["Action"] or "-"))

st.plotly_chart(
    make_price_chart(df, f"{COINS[coin]}/{VS_CURRENCY.upper()} — Price + EMA + Bollinger Bands"),
    use_container_width=True,
)

if show_rsi:
    st.plotly_chart(make_rsi_chart(df, f"{COINS[coin]} — RSI"), use_container_width=True)

table_cols = [
    "price", "Trend_State", "RSI", "RSI_State", "BB_State", "BB_Squeeze",
    "Long_Score", "Short_Score", "Bias", "Watch", "Action", "Signal",
]

st.subheader("Latest rows")
st.dataframe(df[table_cols].tail(show_table_rows), use_container_width=True)

if scan_all:
    st.subheader("Action Dashboard — latest row per coin")
    latest_df, _ = load_all_coins(days)

    if latest_df.empty:
        st.write("No coin data available.")
    else:
        display_df = latest_df.copy()
        display_df["Score"] = np.where(
            display_df["Action"] == "BUY",
            display_df["Long_Score"],
            np.where(display_df["Action"] == "SELL", display_df["Short_Score"], np.nan),
        )

        action_df = display_df[display_df["Action"].isin(["BUY", "SELL"])].copy()

        if action_df.empty:
            st.info("No BUY/SELL actions on the latest candle.")
        else:
            st.dataframe(
                action_df[
                    [
                        "ticker", "coin_id", "Date", "price", "Trend_State", "RSI",
                        "Long_Score", "Short_Score", "Watch", "Action", "Score",
                    ]
                ].sort_values("Score", ascending=False),
                use_container_width=True,
            )

        with st.expander("Show all latest coin states"):
            st.dataframe(display_df, use_container_width=True)
