import pandas as pd
import numpy as np
from strategy import BB_RSI_StochRSIStrategy
from risk import position_size, levels

def run_backtest(df: pd.DataFrame, cfg: dict, equity=1000.0, fee_pct=0.04):
    strat = BB_RSI_StochRSIStrategy(cfg['strategy'])
    df = strat.compute_indicators(df)
    trades = []
    position = None  # dict: side, entry, sl, tp, qty

    for i in range(100, len(df)-1):  # skip warmup and use next candle for fills
        row = df.iloc[:i+1]
        signal = strat.signal(row)
        last = row.iloc[-2]

        if position is None and signal in ('long','short'):
            entry = last['close']
            sl, tp = levels(signal, entry, last['bb_low'], last['bb_high'], last['atr'], cfg['risk'])
            qty = position_size(equity, entry, sl, cfg['risk']['equity_risk_pct'])
            if qty > 0:
                position = {'side':signal,'entry':entry,'sl':sl,'tp':tp,'qty':qty,'entry_idx':i-1}
        elif position is not None:
            nxt = df.iloc[i-1:i+1]
            low = nxt['low'].iloc[-1]
            high = nxt['high'].iloc[-1]

            exit_price = None
            reason = None
            if position['side']=='long':
                if low <= position['sl']:
                    exit_price, reason = position['sl'],'SL'
                elif high >= position['tp']:
                    exit_price, reason = position['tp'],'TP'
            else:
                if high >= position['sl']:
                    exit_price, reason = position['sl'],'SL'
                elif low <= position['tp']:
                    exit_price, reason = position['tp'],'TP'

            if exit_price is not None:
                pnl = (exit_price - position['entry']) * (1 if position['side']=='long' else -1) * position['qty']
                pnl -= (position['entry'] + exit_price) * fee_pct/100.0 * position['qty']
                equity += pnl
                trades.append({'side':position['side'],'entry':position['entry'],'exit':exit_price,'reason':reason,'pnl':pnl,'equity':equity,'index':i})
                position=None

    stats = {
        'n_trades': len(trades),
        'equity_final': equity,
        'equity_return_pct': (equity-1000.0)/10.0
    }
    return pd.DataFrame(trades), stats