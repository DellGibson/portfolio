"""
Unit tests for MarketDataCache.

Tests:
- Trade and quote storage
- Window size limits (FIFO eviction)
- VWAP calculation
- Price change calculation
- Spread calculation
- Stale data handling
- Edge cases (empty cache, insufficient data)
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_cache import MarketDataCache


class TestMarketDataCache:
    """Test suite for MarketDataCache"""

    def test_basic_trade_storage(self):
        """Test 1: Basic trade storage and retrieval"""
        cache = MarketDataCache()

        # Add trades
        cache.add_trade('AAPL', 150.00, 100, datetime.now())
        cache.add_trade('AAPL', 150.50, 200, datetime.now())
        cache.add_trade('AAPL', 151.00, 150, datetime.now())

        # Verify last price
        assert cache.get_last_price('AAPL') == 151.00

        # Verify trade count
        assert len(cache.trades['AAPL']) == 3

    def test_window_size_limit(self):
        """Test 2: Window size enforces FIFO eviction"""
        cache = MarketDataCache(window_size=5)

        # Add 10 trades
        for i in range(10):
            cache.add_trade('SPY', 400.00 + i, 100, datetime.now())

        # Should only retain last 5
        assert len(cache.trades['SPY']) == 5

        # First trade should be price 405 (5th trade), not 400 (1st trade)
        oldest_trade = cache.trades['SPY'][0]
        assert oldest_trade['price'] == 405.00

        # Last trade should be price 409
        assert cache.get_last_price('SPY') == 409.00

    def test_vwap_calculation(self):
        """Test 3: VWAP calculation with known values"""
        cache = MarketDataCache()

        now = datetime.now()

        # Add trades with known prices and volumes
        # VWAP = (100*100 + 101*200 + 102*300) / (100+200+300)
        # VWAP = (10000 + 20200 + 30600) / 600 = 60800 / 600 = 101.33
        cache.add_trade('TEST', 100.00, 100, now - timedelta(seconds=30))
        cache.add_trade('TEST', 101.00, 200, now - timedelta(seconds=20))
        cache.add_trade('TEST', 102.00, 300, now - timedelta(seconds=10))

        vwap = cache.get_vwap('TEST', lookback_seconds=60)

        # Should be close to 101.33
        assert vwap is not None
        assert abs(vwap - 101.33) < 0.01

    def test_vwap_stale_data(self):
        """Test 4: VWAP returns None for stale data"""
        cache = MarketDataCache()

        # Add trades 2 hours ago
        old_time = datetime.now() - timedelta(hours=2)
        cache.add_trade('TSLA', 200.00, 100, old_time)
        cache.add_trade('TSLA', 201.00, 100, old_time)

        # Request VWAP with 60 second lookback
        vwap = cache.get_vwap('TSLA', lookback_seconds=60)

        # Should return None (no data in lookback window)
        assert vwap is None

    def test_price_change_calculation(self):
        """Test 5: Price change calculation"""
        cache = MarketDataCache()

        now = datetime.now()

        # Start at $100, end at $105 = 5% gain
        cache.add_trade('NVDA', 100.00, 100, now - timedelta(seconds=300))
        cache.add_trade('NVDA', 102.00, 100, now - timedelta(seconds=200))
        cache.add_trade('NVDA', 103.00, 100, now - timedelta(seconds=100))
        cache.add_trade('NVDA', 105.00, 100, now - timedelta(seconds=10))

        price_change = cache.get_price_change('NVDA', lookback_seconds=400)

        # Should be 0.05 (5% increase)
        assert price_change is not None
        assert abs(price_change - 0.05) < 0.001

    def test_spread_in_basis_points(self):
        """Test 6: Bid-ask spread calculation in basis points"""
        cache = MarketDataCache()

        # Bid $100, Ask $100.10 = $0.10 spread
        # Spread % = 0.10 / 100 = 0.001 = 0.1%
        # Basis points = 0.1% * 10000 = 10 bps
        cache.add_quote('META', 100.00, 100.10, 500, 500, datetime.now())

        spread_bps = cache.get_spread_bps('META')

        assert spread_bps is not None
        assert abs(spread_bps - 10.0) < 0.1

    def test_empty_cache_edge_case(self):
        """Test 7: Empty cache returns None without crashing"""
        cache = MarketDataCache()

        # All methods should return None or empty for non-existent symbol
        assert cache.get_last_price('NONEXISTENT') is None
        assert cache.get_last_quote('NONEXISTENT') is None
        assert cache.get_vwap('NONEXISTENT') is None
        assert cache.get_price_change('NONEXISTENT') is None
        assert cache.get_spread_bps('NONEXISTENT') is None

    def test_quote_storage(self):
        """Test 8: Quote storage and retrieval"""
        cache = MarketDataCache()

        now = datetime.now()
        cache.add_quote('GOOGL', 140.00, 140.20, 1000, 800, now)

        quote = cache.get_last_quote('GOOGL')

        assert quote is not None
        assert quote['bid'] == 140.00
        assert quote['ask'] == 140.20
        assert quote['spread'] == 0.20
        assert quote['bid_size'] == 1000
        assert quote['ask_size'] == 800

    def test_insufficient_data_for_calculations(self):
        """Test 9: Calculations with insufficient data"""
        cache = MarketDataCache()

        # Add only 1 trade
        cache.add_trade('AMZN', 180.00, 100, datetime.now())

        # Price change needs at least 2 trades
        price_change = cache.get_price_change('AMZN', lookback_seconds=60)
        assert price_change is None

    def test_statistics_summary(self):
        """Test 10: Statistics summary generation"""
        cache = MarketDataCache()

        now = datetime.now()

        # Add sample data
        cache.add_trade('MSFT', 380.00, 100, now - timedelta(seconds=60))
        cache.add_trade('MSFT', 381.00, 150, now - timedelta(seconds=30))
        cache.add_trade('MSFT', 382.00, 200, now)
        cache.add_quote('MSFT', 381.90, 382.10, 500, 500, now)

        stats = cache.get_statistics('MSFT')

        assert stats['num_trades'] == 3
        assert stats['num_quotes'] == 1
        assert stats['last_price'] == 382.00
        assert stats['vwap_1min'] is not None
        assert stats['price_change_5min'] is not None
        assert stats['spread_bps'] is not None

    def test_dataframe_conversion(self):
        """Test 11: Convert cache to pandas DataFrame"""
        cache = MarketDataCache()

        now = datetime.now()
        cache.add_trade('QQQ', 350.00, 100, now - timedelta(seconds=20))
        cache.add_trade('QQQ', 350.50, 150, now - timedelta(seconds=10))
        cache.add_trade('QQQ', 351.00, 200, now)

        df = cache.to_dataframe('QQQ', data_type='trades')

        assert len(df) == 3
        assert 'price' in df.columns
        assert 'size' in df.columns
        assert 'timestamp' in df.columns

    def test_multiple_symbols(self):
        """Test 12: Cache handles multiple symbols independently"""
        cache = MarketDataCache()

        now = datetime.now()

        # Add data for multiple symbols
        cache.add_trade('AAPL', 150.00, 100, now)
        cache.add_trade('MSFT', 380.00, 200, now)
        cache.add_trade('GOOGL', 140.00, 150, now)

        # Each symbol should have independent data
        assert cache.get_last_price('AAPL') == 150.00
        assert cache.get_last_price('MSFT') == 380.00
        assert cache.get_last_price('GOOGL') == 140.00

        # Counts should be independent
        assert len(cache.trades['AAPL']) == 1
        assert len(cache.trades['MSFT']) == 1
        assert len(cache.trades['GOOGL']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
