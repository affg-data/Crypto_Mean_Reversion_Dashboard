from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .config import EMA_FAST, EMA_SLOW, RSI_LEN, OVERBOUGHT, OVERSOLD, VS_CURRENCY

# Central chart palette. Change colors here once and Streamlit updates everywhere.
COLORS = {
    "price": "#1f77b4",
    "ema_fast": "#ff7f0e",
    "ema_slow": "#2ca02c",
    "bb_upper": "#ef6f6c",
    "bb_mid": "#8b5cf6",
    "bb_lower": "#8d6e63",
    "bb_fill": "rgba(156, 163, 175, 0.15)",  # #9ca3af at 15% opacity
    "buy": "#16a34a",
    "sell": "#dc2626",
    "squeeze": "rgba(107,114,128,0.35)",
}

def make_price_chart(df: pd.DataFrame, title: str = "") -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["price"], name="Price",
        line=dict(color=COLORS["price"], width=2.2)
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA_fast"], name=f"EMA {EMA_FAST}",
        line=dict(color=COLORS["ema_fast"], width=1.5)
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["EMA_slow"], name=f"EMA {EMA_SLOW}",
        line=dict(color=COLORS["ema_slow"], width=1.5)
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Upper"], name="BB Upper",
        line=dict(color=COLORS["bb_upper"], dash="dash", width=1)
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Mid"], name="BB Mid",
        line=dict(color=COLORS["bb_mid"], dash="dot", width=1)
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Lower"], name="BB Lower",
        line=dict(color=COLORS["bb_lower"], dash="dash", width=1)
    ))

    # Plot upper invisible boundary, then lower with fill="tonexty".
    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Upper"],
        name="BB Range Upper Boundary",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["BB_Lower"],
        name="BB Range",
        fill="tonexty",
        fillcolor=COLORS["bb_fill"],
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=True,
    ))

    buy = df["Action"] == "BUY"
    sell = df["Action"] == "SELL"

    fig.add_trace(go.Scatter(
        x=df.index[buy], y=df.loc[buy, "price"],
        mode="markers", name="BUY",
        marker=dict(symbol="triangle-up", size=11, color=COLORS["buy"], line=dict(width=1, color="white")),
    ))

    fig.add_trace(go.Scatter(
        x=df.index[sell], y=df.loc[sell, "price"],
        mode="markers", name="SELL",
        marker=dict(symbol="triangle-down", size=11, color=COLORS["sell"], line=dict(width=1, color="white")),
    ))

    if "BB_Squeeze" in df.columns:
        squeeze = df["BB_Squeeze"].fillna(False)
        fig.add_trace(go.Scatter(
            x=df.index[squeeze], y=df.loc[squeeze, "price"],
            mode="markers", name="Squeeze",
            marker=dict(size=5, color=COLORS["squeeze"]),
        ))

    fig.update_layout(
        title=title,
        height=540,
        template="plotly_white",
        margin=dict(l=10, r=10, t=55, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title=f"Price ({VS_CURRENCY.upper()})",
    )

    return fig

def make_rsi_chart(df: pd.DataFrame, title: str = "RSI") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name=f"RSI {RSI_LEN}", line=dict(width=2)))
    fig.add_hline(y=OVERBOUGHT, line_dash="dash", annotation_text="Overbought")
    fig.add_hline(y=OVERSOLD, line_dash="dash", annotation_text="Oversold")
    fig.update_layout(
        title=title,
        height=280,
        template="plotly_white",
        margin=dict(l=10, r=10, t=45, b=20),
        hovermode="x unified",
        yaxis_title="RSI",
    )
    return fig
