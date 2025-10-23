"""
Real-time market data storage with rolling windows.
Why: Strategies need historical context (VWAP, moving averages) without API calls.
Complexity: O(1) append, O(n) calculations where n = window size (typically <1000)
"""
from collections import deque
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional

class MarketDataCache:
    def __init__(self, window_size: int = 1000):
        """
        Args:
            window_size: Max number of ticks to retain per symbol
        """
        self.trades: Dict[str, deque] = {}  # symbol -> deque of trade dicts
        self.quotes: Dict[str, deque] = {}  # symbol -> deque of quote dicts
        self.bars: Dict[str, deque] = {}    # symbol -> deque of 1-min bars
        self.window_size = window_size

    def add_trade(self, symbol: str, price: float, size: int, timestamp: datetime):
        """Store incoming trade tick"""
        if symbol not in self.trades:
            self.trades[symbol] = deque(maxlen=self.window_size)

        self.trades[symbol].append({
            'timestamp': timestamp,
            'price': price,
            'size': size
        })

    def add_quote(self, symbol: str, bid: float, ask: float, bid_size: int, ask_size: int, timestamp: datetime):
        """Store incoming quote tick"""
        if symbol not in self.quotes:
            self.quotes[symbol] = deque(maxlen=self.window_size)

        self.quotes[symbol].append({
            'timestamp': timestamp,
            'bid': bid,
            'ask': ask,
            'bid_size': bid_size,
            'ask_size': ask_size,
            'spread': ask - bid
        })

    def get_last_price(self, symbol: str) -> Optional[float]:
        """Get most recent trade price"""
        if symbol not in self.trades or not self.trades[symbol]:
            return None
        return self.trades[symbol][-1]['price']

    def get_last_quote(self, symbol: str) -> Optional[dict]:
        """Get most recent bid/ask"""
        if symbol not in self.quotes or not self.quotes[symbol]:
            return None
        return self.quotes[symbol][-1]

    def get_vwap(self, symbol: str, lookback_seconds: int = 60) -> Optional[float]:
        """
        Calculate Volume-Weighted Average Price.
        Why: Better execution benchmark than simple average.
        Edge case: Returns None if no data in lookback period.
        """
        if symbol not in self.trades or not self.trades[symbol]:
            return None

        cutoff = datetime.now() - timedelta(seconds=lookback_seconds)
        recent_trades = [
            t for t in self.trades[symbol]
            if t['timestamp'] > cutoff
        ]

        if not recent_trades:
            return None

        total_value = sum(t['price'] * t['size'] for t in recent_trades)
        total_volume = sum(t['size'] for t in recent_trades)

        return total_value / total_volume if total_volume > 0 else None

    def get_price_change(self, symbol: str, lookback_seconds: int = 300) -> Optional[float]:
        """
        Calculate percentage price change over lookback period.
        Returns: Float (e.g., 0.025 = 2.5% increase)
        """
        if symbol not in self.trades or len(self.trades[symbol]) < 2:
            return None

        cutoff = datetime.now() - timedelta(seconds=lookback_seconds)
        recent_trades = [
            t for t in self.trades[symbol]
            if t['timestamp'] > cutoff
        ]

        if len(recent_trades) < 2:
            return None

        start_price = recent_trades[0]['price']
        end_price = recent_trades[-1]['price']

        return (end_price - start_price) / start_price

    def get_spread_bps(self, symbol: str) -> Optional[float]:
        """
        Get current bid-ask spread in basis points.
        Why: Wide spreads = high transaction cost, low liquidity.
        Edge case: Returns None if no quote data available.
        """
        quote = self.get_last_quote(symbol)
        if not quote or quote['bid'] == 0:
            return None

        spread_pct = (quote['ask'] - quote['bid']) / quote['bid']
        return spread_pct * 10000  # Convert to basis points

    def to_dataframe(self, symbol: str, data_type: str = 'trades') -> pd.DataFrame:
        """
        Convert cached data to pandas DataFrame for analysis.
        Args:
            data_type: 'trades' or 'quotes'
        """
        if data_type == 'trades':
            if symbol not in self.trades or not self.trades[symbol]:
                return pd.DataFrame()
            return pd.DataFrame(list(self.trades[symbol]))

        elif data_type == 'quotes':
            if symbol not in self.quotes or not self.quotes[symbol]:
                return pd.DataFrame()
            return pd.DataFrame(list(self.quotes[symbol]))

        return pd.DataFrame()

    def get_statistics(self, symbol: str) -> dict:
        """Get summary statistics for monitoring"""
        return {
            'num_trades': len(self.trades.get(symbol, [])),
            'num_quotes': len(self.quotes.get(symbol, [])),
            'last_price': self.get_last_price(symbol),
            'vwap_1min': self.get_vwap(symbol, 60),
            'price_change_5min': self.get_price_change(symbol, 300),
            'spread_bps': self.get_spread_bps(symbol)
        }
