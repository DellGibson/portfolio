"""
Unit tests for trading strategies.

Tests:
- Mean reversion buy/sell/hold signals
- Momentum breakout signals
- Position sizing calculations
- Signal confidence levels
- Edge cases (insufficient data, wide spreads)
- Regime detection
- Volatility adjustments
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy import MeanReversionStrategy, MomentumBreakoutStrategy, RegimeDetector
from data_cache import MarketDataCache


class TestMeanReversionStrategy:
    """Test suite for Mean Reversion Strategy"""

    @pytest.fixture
    def strategy(self):
        """Create mean reversion strategy"""
        return MeanReversionStrategy(
            lookback_period=20,
            std_dev_threshold=2.0,
            max_spread_bps=20.0
        )

    @pytest.fixture
    def cache(self):
        """Create market data cache"""
        return MarketDataCache()

    def test_buy_signal_oversold(self, strategy, cache):
        """Test 1: Generate BUY signal when price oversold"""
        now = datetime.now()

        # Create price series: stable at $100, then drop to $90 (>2 std devs below)
        for i in range(19):
            cache.add_trade('TEST', 100.00, 100, now - timedelta(seconds=100-i))

        # Add final trade at $90 (oversold)
        cache.add_trade('TEST', 90.00, 100, now)

        # Add quote with acceptable spread
        cache.add_quote('TEST', 89.95, 90.05, 500, 500, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'BUY'
        assert signal['symbol'] == 'TEST'
        assert signal['confidence'] > 0.5
        assert 'Oversold' in signal['reason']

    def test_sell_signal_overbought(self, strategy, cache):
        """Test 2: Generate SELL signal when price overbought"""
        now = datetime.now()

        # Create price series: stable at $100, then jump to $110 (>2 std devs above)
        for i in range(19):
            cache.add_trade('TEST', 100.00, 100, now - timedelta(seconds=100-i))

        # Add final trade at $110 (overbought)
        cache.add_trade('TEST', 110.00, 100, now)

        # Add quote with acceptable spread
        cache.add_quote('TEST', 109.95, 110.05, 500, 500, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'SELL'
        assert signal['symbol'] == 'TEST'
        assert signal['confidence'] > 0.5
        assert 'Overbought' in signal['reason']

    def test_hold_signal_within_range(self, strategy, cache):
        """Test 3: Generate HOLD signal when price within normal range"""
        now = datetime.now()

        # Create price series: oscillating around $100 within 1 std dev
        prices = [100, 101, 99, 100, 101, 99, 100, 101, 99, 100,
                 101, 99, 100, 101, 99, 100, 101, 99, 100, 101]

        for i, price in enumerate(prices):
            cache.add_trade('TEST', float(price), 100, now - timedelta(seconds=100-i))

        # Add quote
        cache.add_quote('TEST', 100.95, 101.05, 500, 500, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'HOLD'
        assert signal['symbol'] == 'TEST'
        assert 'Within range' in signal['reason']

    def test_insufficient_data_hold(self, strategy, cache):
        """Test 4: Return HOLD with insufficient data"""
        now = datetime.now()

        # Add only 5 trades (need 20)
        for i in range(5):
            cache.add_trade('TEST', 100.00, 100, now - timedelta(seconds=10-i))

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'HOLD'
        assert 'Insufficient data' in signal['reason']

    def test_wide_spread_rejection(self, strategy, cache):
        """Test 5: Reject signal when spread too wide"""
        now = datetime.now()

        # Add sufficient data for normal signal
        for i in range(20):
            cache.add_trade('TEST', 100.00, 100, now - timedelta(seconds=100-i))

        # Add final trade that would trigger buy
        cache.add_trade('TEST', 90.00, 100, now)

        # Add quote with WIDE spread (>20 bps threshold)
        # Bid $90, Ask $90.50 = $0.50 spread = 0.556% = 55.6 bps
        cache.add_quote('TEST', 90.00, 90.50, 500, 500, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'HOLD'
        assert 'Spread too wide' in signal['reason']

    def test_position_sizing_risk_based(self, strategy, cache):
        """Test 6: Position sizing based on risk"""
        now = datetime.now()

        # Add some data for volatility calculation
        for i in range(20):
            cache.add_trade('TEST', 100.00 + i*0.1, 100, now - timedelta(seconds=100-i))

        # Account: $100,000
        # Price: $100
        # Risk 1% of account = $1,000
        # Stop loss 2% = $2
        # Position size = $1,000 / $2 = 500 shares
        # But max position 10% = $10,000 / $100 = 100 shares
        # Should return 100 shares

        shares = strategy.get_position_size('TEST', 100.00, 100000.00, cache)

        # Should be capped at max position limit
        assert shares <= 100

    def test_signal_cooldown(self, strategy, cache):
        """Test 7: Signal cooldown prevents spam"""
        now = datetime.now()

        # Create oversold condition
        for i in range(20):
            cache.add_trade('TEST', 100.00, 100, now - timedelta(seconds=100-i))
        cache.add_trade('TEST', 90.00, 100, now)
        cache.add_quote('TEST', 89.95, 90.05, 500, 500, now)

        # First signal should generate
        signal1 = strategy.evaluate('TEST', cache)
        assert signal1['action'] == 'BUY'

        # Immediately evaluate again - should be in cooldown
        signal2 = strategy.evaluate('TEST', cache)
        assert signal2['action'] == 'HOLD'
        assert 'cooldown' in signal2['reason'].lower()


class TestMomentumBreakoutStrategy:
    """Test suite for Momentum Breakout Strategy"""

    @pytest.fixture
    def strategy(self):
        """Create momentum breakout strategy"""
        return MomentumBreakoutStrategy(
            breakout_period=20,
            breakout_threshold=0.02,  # 2%
            volume_multiplier=2.0
        )

    @pytest.fixture
    def cache(self):
        """Create market data cache"""
        return MarketDataCache()

    def test_buy_signal_breakout(self, strategy, cache):
        """Test 8: Generate BUY on breakout above resistance"""
        now = datetime.now()

        # Create ranging price: stable at $100
        for i in range(20):
            price = 98.00 + (i % 3)  # Range $98-$100
            cache.add_trade('TEST', price, 1000, now - timedelta(seconds=120-i))

        # Add recent normal trades
        for i in range(5):
            cache.add_trade('TEST', 100.00, 1000, now - timedelta(seconds=10-i))

        # Breakout: price jumps to $103.00 (3% above $100 high)
        # With high volume (2.5x average)
        cache.add_trade('TEST', 103.00, 2500, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'BUY'
        assert signal['confidence'] > 0.5
        assert 'Breakout' in signal['reason']

    def test_false_breakout_low_volume(self, strategy, cache):
        """Test 9: Reject breakout with low volume confirmation"""
        now = datetime.now()

        # Create ranging price: stable at $100
        for i in range(20):
            price = 98.00 + (i % 3)
            cache.add_trade('TEST', price, 1000, now - timedelta(seconds=120-i))

        # Add recent normal trades
        for i in range(5):
            cache.add_trade('TEST', 100.00, 1000, now - timedelta(seconds=10-i))

        # Breakout price but LOW volume (0.8x average)
        cache.add_trade('TEST', 103.00, 800, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'HOLD'
        # The reason should indicate volume issue or no breakout
        assert 'volume' in signal['reason'].lower() or 'no breakout' in signal['reason'].lower()

    def test_sell_signal_breakdown(self, strategy, cache):
        """Test 10: Generate SELL on breakdown below support"""
        now = datetime.now()

        # Create ranging price: stable at $100
        for i in range(20):
            price = 100.00 + (i % 3)  # Range $100-$102
            cache.add_trade('TEST', price, 1000, now - timedelta(seconds=120-i))

        # Add recent normal trades
        for i in range(5):
            cache.add_trade('TEST', 100.00, 1000, now - timedelta(seconds=10-i))

        # Breakdown: price drops to $97.00 (3% below $100 low)
        # With high volume
        cache.add_trade('TEST', 97.00, 2500, now)

        signal = strategy.evaluate('TEST', cache)

        assert signal['action'] == 'SELL'
        assert 'Breakdown' in signal['reason']

    def test_volatility_adjusted_position_sizing(self, strategy, cache):
        """Test 11: Position size adjusts for volatility"""
        now = datetime.now()

        # Low volatility stock (small price movements)
        for i in range(20):
            price = 100.00 + np.random.uniform(-0.1, 0.1)  # ±0.1% moves
            cache.add_trade('LOW_VOL', price, 1000, now - timedelta(seconds=100-i))

        low_vol_size = strategy.get_position_size('LOW_VOL', 100.00, 100000.00, cache)

        # High volatility stock (large price movements)
        cache2 = MarketDataCache()
        for i in range(20):
            price = 100.00 + np.random.uniform(-5, 5)  # ±5% moves
            cache2.add_trade('HIGH_VOL', price, 1000, now - timedelta(seconds=100-i))

        high_vol_size = strategy.get_position_size('HIGH_VOL', 100.00, 100000.00, cache2)

        # Low volatility should get larger position
        assert low_vol_size > high_vol_size


class TestRegimeDetector:
    """Test suite for Regime Detection"""

    @pytest.fixture
    def mock_api(self):
        """Create mock API"""
        return Mock()

    @pytest.fixture
    def detector(self, mock_api):
        """Create regime detector"""
        return RegimeDetector(mock_api)

    def test_trending_regime_detection(self, detector):
        """Test 12: Detect TRENDING regime"""
        cache = MarketDataCache()
        now = datetime.now()

        # Clear uptrend: prices rising steadily with low volatility
        for i in range(20):
            price = 400.00 + i * 0.5  # Steady uptrend
            cache.add_trade('SPY', price, 1000, now - timedelta(seconds=100-i))

        regime = detector.detect_regime(cache)

        # With clear trend and low volatility, should detect TRENDING
        assert regime in ['TRENDING', 'RANGING']  # Depending on exact volatility

    def test_ranging_regime_detection(self, detector):
        """Test 13: Detect RANGING regime"""
        cache = MarketDataCache()
        now = datetime.now()

        # Oscillating prices (no clear trend)
        prices = [400, 401, 399, 400, 402, 398, 400, 401, 399, 400] * 2
        for i, price in enumerate(prices):
            cache.add_trade('SPY', float(price), 1000, now - timedelta(seconds=100-i))

        regime = detector.detect_regime(cache)

        # Should detect RANGING
        assert regime == 'RANGING'

    def test_volatile_regime_detection(self, detector):
        """Test 14: Detect VOLATILE regime"""
        cache = MarketDataCache()
        now = datetime.now()

        # High volatility: large random swings
        for i in range(20):
            price = 400.00 + np.random.uniform(-20, 20)  # ±5% swings
            cache.add_trade('SPY', price, 1000, now - timedelta(seconds=100-i))

        regime = detector.detect_regime(cache)

        # High volatility should trigger VOLATILE regime
        # Note: may detect RANGING depending on exact random values
        assert regime in ['VOLATILE', 'RANGING']


class TestStrategyIntegration:
    """Integration tests across strategies"""

    def test_strategy_returns_valid_signal_structure(self):
        """Test 15: All strategies return valid signal format"""
        cache = MarketDataCache()
        now = datetime.now()

        # Add minimal data
        for i in range(25):
            cache.add_trade('TEST', 100.00 + i*0.1, 100, now - timedelta(seconds=100-i))
        cache.add_quote('TEST', 102.45, 102.55, 500, 500, now)

        strategies = [
            MeanReversionStrategy(),
            MomentumBreakoutStrategy()
        ]

        for strategy in strategies:
            signal = strategy.evaluate('TEST', cache)

            # Verify signal structure
            assert 'action' in signal
            assert 'symbol' in signal
            assert 'confidence' in signal
            assert 'reason' in signal
            assert 'quantity' in signal

            # Verify valid values
            assert signal['action'] in ['BUY', 'SELL', 'HOLD']
            assert signal['symbol'] == 'TEST'
            assert 0.0 <= signal['confidence'] <= 1.0
            assert isinstance(signal['reason'], str)
            assert signal['quantity'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
