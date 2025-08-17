import ccxt, math, os, logging
from dotenv import load_dotenv

class Broker:
    def __init__(self, exchange_id: str, mode: str = 'paper', leverage: int = 1):
        load_dotenv()
        self.mode = mode
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': os.getenv('API_KEY',''),
            'secret': os.getenv('API_SECRET',''),
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self.leverage = leverage
        self.logger = logging.getLogger("bot")

    def fetch_ohlcv(self, symbol, timeframe, limit=500, since=None):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, since=since)

    def fetch_balance(self):
        bal = self.exchange.fetch_balance()
        # try common fields; fallback to total USDT
        for k in ['USDT','USD']:
            if k in bal['total']:
                return float(bal['total'][k])
        return float(bal['info'].get('totalWalletBalance', 0))

    def market_order(self, symbol, side, amount):
        self.logger.info(f"[{self.mode}] Market {side} {amount} {symbol}")
        if self.mode == 'paper':
            return {'id': 'paper', 'amount': amount}
        return self.exchange.create_order(symbol, 'market', side, amount)

    def set_leverage(self, symbol):
        try:
            self.exchange.set_leverage(self.leverage, symbol.replace('/',''))
        except Exception as e:
            self.logger.warning(f"set_leverage failed: {e}")