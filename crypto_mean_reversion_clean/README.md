# Crypto Mean-Reversion Dashboard

Multi-coin mean-reversion project.

## What changed

Old workflow had logic spread across notebooks and Streamlit. This version separates the project into:

```text
crypto_mean_reversion_clean/
├── app.py                         # Streamlit web app only
├── requirements.txt
├── src/
│   └── crypto_mr/
│       ├── __init__.py
│       ├── config.py              # coins + constants
│       ├── data.py                # CoinGecko fetch + retries
│       ├── indicators.py          # EMA, RSI, Bollinger Bands
│       ├── strategy.py            # scores, watch, action, signals
│       ├── pipeline.py            # one-coin + multi-coin runners
│       └── plotting.py            # Plotly chart styling
└── data/
    └── csv/                       # optional exports
```

## Install

```bash
pip install -r requirements.txt
```

## Run Streamlit app

```bash
streamlit run app.py
```

## Key rule

- Change indicator logic in `src/crypto_mr/indicators.py`
- Change buy/sell scoring in `src/crypto_mr/strategy.py`
- Change BB shade / chart colors in `src/crypto_mr/plotting.py`
- Change web layout in `app.py`

## BB shade color

The web app uses Plotly, not matplotlib. The BB range shade is here:

```python
fillcolor="rgba(156, 163, 175, 0.15)"
```

That equals soft gray `#9ca3af` with 15% opacity.

## Notes

CoinGecko may rate-limit requests. If you get HTTP 429, lower auto-refresh frequency, reduce coins, or wait before rerunning.
