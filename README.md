# Bollinger + RSI(6/14/24) + StochRSI — 30m Trading Bot (Binance/Bybit via CCXT)

A robust, configurable trading bot for crypto perpetuals/spot.  
Core features:
- Strategy: Bollinger Bands (21, 2.0–2.2), RSI(6, 14, 24), StochRSI(14,14,3,3) on **30m**
- Risk: % of equity per trade, ATR-based SL buffer, TP on bands, optional trailing stop
- Filters: trend filter via RSI(24) & BB middle, time-of-day session filter
- Modes: `paper` (dry-run), `live`, `backtest`
- Alerts: optional Telegram push
- Logs: structured JSON + human logs
- Modular: Strategy ↔ Execution separated

> ⚠️ You run this at your own risk. Test with `paper` & `backtest` before going live.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env  # fill API keys, Telegram bot token (optional)
python bot.py --exchange binance --symbol ETH/USDT --timeframe 30m --mode paper
```

Backtest example:

```bash
python bot.py --exchange binance --symbol ETH/USDT --timeframe 30m --mode backtest --since 60d
```

## Files
- `bot.py` — main entrypoint
- `strategy.py` — indicators & signals
- `risk.py` — position sizing, SL/TP, trailing
- `broker.py` — CCXT wrapper (paper/live)
- `backtest.py` — vectorized backtester
- `config.yaml` — defaults you can edit
- `requirements.txt` — deps
- `.env.example` — template for keys
- `utils.py` — helpers