import math

def position_size(equity_usdt: float, price: float, sl_price: float, risk_pct: float):
    risk_amount = equity_usdt * (risk_pct/100.0)
    per_unit_risk = abs(price - sl_price)
    if per_unit_risk <= 0:
        return 0.0
    qty = risk_amount / per_unit_risk
    return max(qty, 0.0)

def levels(side: str, entry: float, bb_low: float, bb_high: float, atr: float, cfg):
    # SL buffer: max(ATR*mult, band_buffer_pct*price)
    buf = max(atr * cfg['atr_mult_sl'], entry * (cfg['band_buffer_pct']/100.0))
    if side == 'long':
        sl = entry - buf
        tp = bb_high if cfg['take_profit_mode']=='bands' else entry + (entry - sl)*cfg['rr_ratio']
    else:
        sl = entry + buf
        tp = bb_low if cfg['take_profit_mode']=='bands' else entry - (sl - entry)*cfg['rr_ratio']
    return sl, tp

def trail_stop(side: str, entry: float, sl: float, price: float, atr: float, cfg, rr_reached: float):
    if not cfg['trailing']['enabled']:
        return sl
    # Activate trailing after certain RR
    if rr_reached < cfg['trailing']['activation_rr']:
        return sl
    trail_dist = atr * cfg['trailing']['atr_mult_trail']
    if side == 'long':
        new_sl = max(sl, price - trail_dist)
    else:
        new_sl = min(sl, price + trail_dist)
    return new_sl