import argparse, yaml, pandas as pd, logging
from dotenv import load_dotenv
from broker import Broker
from strategy import BB_RSI_StochRSIStrategy
from risk import position_size, levels, trail_stop
from utils import setup_logger, sleep_s
from backtest import run_backtest

def load_cfg(path='config.yaml'):
    with open(path,'r') as f:
        return yaml.safe_load(f)

def fetch_df(broker, symbol, timeframe, limit=600, since=None):
    ohlcv = broker.fetch_ohlcv(symbol, timeframe, limit=limit, since=since)
    df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
    return df

def run_live(cfg):
    logger = setup_logger(cfg['general']['log_level'])
    b = Broker(cfg['general']['exchange'], cfg['general']['mode'], cfg['general']['leverage'])
    sym = cfg['general']['symbol']
    tf  = cfg['general']['timeframe']
    strat = BB_RSI_StochRSIStrategy(cfg['strategy'])

    equity = b.fetch_balance() if cfg['general']['mode']=='live' else 1000.0
    logger.info(f"Starting in {cfg['general']['mode']} mode | Equity ~ {equity:.2f}")

    open_pos = None
    last_ts = None

    while True:
        df = fetch_df(b, sym, tf, limit=400)
        df = strat.compute_indicators(df)
        # detect new candle
        ts = int(df['time'].iloc[-1])
        if last_ts == ts:
            sleep_s(5); continue
        last_ts = ts

        sig = strat.signal(df)
        last = df.iloc[-2]

        # position management
        if open_pos:
            price = last['close']
            rr = abs(price - open_pos['entry']) / abs(open_pos['entry'] - open_pos['sl'])
            new_sl = trail_stop(open_pos['side'], open_pos['entry'], open_pos['sl'], price, last['atr'], cfg['risk'], rr)
            if new_sl != open_pos['sl']:
                logger.info(f"Trailing SL from {open_pos['sl']:.4f} to {new_sl:.4f}")
                open_pos['sl'] = new_sl

        # entries
        if not open_pos and sig in ('long','short'):
            entry = last['close']
            sl, tp = levels(sig, entry, last['bb_low'], last['bb_high'], last['atr'], cfg['risk'])
            qty = position_size(equity, entry, sl, cfg['risk']['equity_risk_pct'])
            if qty > 0:
                logger.info(f"Signal {sig.upper()} | entry {entry:.4f} sl {sl:.4f} tp {tp:.4f} qty {qty:.6f}")
                b.market_order(sym, 'buy' if sig=='long' else 'sell', qty)
                open_pos = {'side':sig,'entry':entry,'sl':sl,'tp':tp,'qty':qty}

        sleep_s(10)  # poll interval

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--mode', default=None, help='paper|live|backtest')
    parser.add_argument('--exchange', default=None)
    parser.add_argument('--symbol', default=None)
    parser.add_argument('--timeframe', default=None)
    parser.add_argument('--since', default=None, help='e.g., 60d or 2024-01-01')
    args = parser.parse_args()

    cfg = load_cfg(args.config)
    # CLI overrides
    for k in ['mode','exchange','symbol','timeframe']:
        v = getattr(args, k)
        if v:
            cfg['general'][k] = v

    if (args.mode or cfg['general']['mode']) == 'backtest':
        # quick backtest using latest data from broker (paper fetch ok)
        b = Broker(cfg['general']['exchange'], 'paper')
        df = fetch_df(b, cfg['general']['symbol'], cfg['general']['timeframe'], limit=1500)
        trades, stats = run_backtest(df, cfg)
        print(stats)
        print(trades.tail())
        return

    run_live(cfg)

if __name__ == '__main__':
    main()