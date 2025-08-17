import pandas as pd
import numpy as np
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochRSIIndicator

class BB_RSI_StochRSIStrategy:
    def __init__(self, cfg):
        self.cfg = cfg

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # BB
        bb = BollingerBands(df['close'], window=self.cfg['bb']['window'], window_dev=self.cfg['bb']['dev'])
        df['bb_mid'] = bb.bollinger_mavg()
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()

        # RSI
        df['rsi_fast'] = RSIIndicator(df['close'], window=self.cfg['rsi']['fast']).rsi()
        df['rsi_mid']  = RSIIndicator(df['close'], window=self.cfg['rsi']['mid']).rsi()
        df['rsi_slow'] = RSIIndicator(df['close'], window=self.cfg['rsi']['slow']).rsi()

        # StochRSI
        st = StochRSIIndicator(
            close=df['close'],
            window=self.cfg['stochrsi']['rsi_window'],
            smooth1=self.cfg['stochrsi']['smooth_k'],
            smooth2=self.cfg['stochrsi']['smooth_d']
        )
        df['stoch_k'] = st.stochrsi_k()
        df['stoch_d'] = st.stochrsi_d()

        # ATR for risk calc
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - df['close'].shift()).abs()
        tr3 = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span= self.cfg.get('atr_window',14), min_periods=1, adjust=False).mean()

        return df

    def signal(self, df: pd.DataFrame):
        # Use last complete candle for signal
        last = df.iloc[-2]
        c = last['close']

        # filters
        long_ok, short_ok = True, True
        if self.cfg.get('use_trend_filter', True):
            long_ok  = (c > last['bb_mid']) and (last['rsi_slow'] > 50)
            short_ok = (c < last['bb_mid']) and (last['rsi_slow'] < 50)

        # Long conditions
        long_cond = (
            (c <= last['bb_mid'] * 1.005) and
            (last['rsi_mid'] < 60) and
            (last['rsi_fast'] > last['rsi_mid']) and
            (last['stoch_k'] < self.cfg['stochrsi']['os']) and
            (last['stoch_k'] > last['stoch_d'])
        )

        # Short conditions
        short_cond = (
            (c >= last['bb_mid'] * 0.995) and
            (last['rsi_mid'] > 40) and
            (last['rsi_fast'] < last['rsi_mid']) and
            (last['stoch_k'] > self.cfg['stochrsi']['ob']) and
            (last['stoch_k'] < last['stoch_d'])
        )

        if long_cond and long_ok:
            return 'long'
        if short_cond and short_ok:
            return 'short'
        return 'hold'