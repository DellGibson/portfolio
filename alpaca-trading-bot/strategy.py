"""
Trading strategy logic with modular architecture.
Why: Separate strategy from infrastructure so algorithms can be swapped without
touching data feeds or order management.

Implements:
- Base strategy interface
- Mean reversion strategy (oversold/overbought detection)
- Momentum breakout strategy (trend following)
- Regime detection (market condition analysis)
- Position sizing (Kelly Criterion, volatility-adjusted)
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import numpy as np
from data_cache import MarketDataCache
from config import Config
from utils import log_info, log_warning, log_error
import alpaca_trade_api as tradeapi


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Forces consistent interface across different algorithms.
    """

    def __init__(self, name: str):
        self.name = name
        self.signals_generated = 0
        self.last_signal_time = {}  # symbol -> timestamp

    @abstractmethod
    def evaluate(self, symbol: str, cache: MarketDataCache) -> Dict:
        """
        Analyze market data and generate trading signal.

        Args:
            symbol: Ticker to analyze
            cache: Market data cache with historical context

        Returns:
            Signal dictionary with keys:
            - action: "BUY", "SELL", or "HOLD"
            - symbol: Ticker symbol
            - confidence: 0.0 to 1.0 (signal strength)
            - reason: Human-readable explanation
            - quantity: Number of shares to trade (0 if HOLD)
        """
        pass

    @abstractmethod
    def get_position_size(self, symbol: str, price: float, account_equity: float,
                         cache: MarketDataCache) -> int:
        """
        Calculate position size based on risk and account size.

        Args:
            symbol: Ticker to trade
            price: Current price
            account_equity: Total account value
            cache: Market data for volatility calculation

        Returns:
            Number of shares to trade
        """
        pass

    def get_name(self) -> str:
        """Return strategy identifier"""
        return self.name

    def _check_signal_cooldown(self, symbol: str, cooldown_seconds: int = 300) -> bool:
        """
        Prevent signal spam - don't generate signals too frequently for same symbol.
        Why: Avoid overtrading on noise.

        Args:
            symbol: Ticker to check
            cooldown_seconds: Minimum time between signals (default 5 minutes)

        Returns:
            True if enough time has passed, False if still in cooldown
        """
        if symbol not in self.last_signal_time:
            return True

        time_since_last = (datetime.now() - self.last_signal_time[symbol]).total_seconds()
        return time_since_last >= cooldown_seconds

    def _update_signal_time(self, symbol: str):
        """Record timestamp of signal generation"""
        self.last_signal_time[symbol] = datetime.now()


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy: Buy oversold, sell overbought.

    Theory: Prices oscillate around moving average. When price deviates >2 standard
    deviations, expect reversion to mean.

    Parameters:
    - lookback_period: Number of trades for moving average (default 20)
    - std_dev_threshold: Standard deviations for entry signal (default 2.0)
    - max_spread_bps: Maximum bid-ask spread in basis points (default 20)
    """

    def __init__(self, lookback_period: int = 20, std_dev_threshold: float = 2.0,
                 max_spread_bps: float = 20.0):
        super().__init__("MeanReversion")
        self.lookback_period = lookback_period
        self.std_dev_threshold = std_dev_threshold
        self.max_spread_bps = max_spread_bps

    def evaluate(self, symbol: str, cache: MarketDataCache) -> Dict:
        """Generate mean reversion signal"""

        # Default HOLD signal
        default_signal = {
            'action': 'HOLD',
            'symbol': symbol,
            'confidence': 0.0,
            'reason': '',
            'quantity': 0
        }

        # Check cooldown
        if not self._check_signal_cooldown(symbol):
            default_signal['reason'] = 'Signal cooldown active'
            return default_signal

        # Get current price
        current_price = cache.get_last_price(symbol)
        if current_price is None:
            default_signal['reason'] = 'No price data available'
            return default_signal

        # Check data freshness
        if symbol not in cache.trades or len(cache.trades[symbol]) < self.lookback_period:
            default_signal['reason'] = f'Insufficient data (need {self.lookback_period} trades)'
            return default_signal

        # Check spread quality
        spread_bps = cache.get_spread_bps(symbol)
        if spread_bps is None or spread_bps > self.max_spread_bps:
            default_signal['reason'] = f'Spread too wide ({spread_bps:.1f} bps > {self.max_spread_bps} bps)'
            return default_signal

        # Calculate moving average and standard deviation
        recent_trades = list(cache.trades[symbol])[-self.lookback_period:]
        prices = np.array([t['price'] for t in recent_trades])

        mean_price = np.mean(prices)
        std_price = np.std(prices)

        if std_price == 0:
            default_signal['reason'] = 'Zero volatility (stale data)'
            return default_signal

        # Calculate z-score (number of standard deviations from mean)
        z_score = (current_price - mean_price) / std_price

        # Generate signals
        if z_score < -self.std_dev_threshold:
            # Oversold: price significantly below mean
            self._update_signal_time(symbol)
            self.signals_generated += 1

            return {
                'action': 'BUY',
                'symbol': symbol,
                'confidence': min(abs(z_score) / 3.0, 1.0),  # Cap at 1.0
                'reason': f'Oversold: {z_score:.2f} std devs below mean (${mean_price:.2f})',
                'quantity': 0  # Will be calculated by position sizing
            }

        elif z_score > self.std_dev_threshold:
            # Overbought: price significantly above mean
            self._update_signal_time(symbol)
            self.signals_generated += 1

            return {
                'action': 'SELL',
                'symbol': symbol,
                'confidence': min(abs(z_score) / 3.0, 1.0),
                'reason': f'Overbought: {z_score:.2f} std devs above mean (${mean_price:.2f})',
                'quantity': 0
            }

        # Within normal range
        default_signal['reason'] = f'Within range: {z_score:.2f} std devs from mean'
        return default_signal

    def get_position_size(self, symbol: str, price: float, account_equity: float,
                         cache: MarketDataCache) -> int:
        """
        Calculate position size using volatility-adjusted method.

        Logic: Risk 1% of account per trade, adjust for volatility
        """
        # Risk 1% of account
        risk_amount = account_equity * 0.01

        # Calculate stop loss distance (2% from entry)
        stop_loss_distance = price * Config.STOP_LOSS_PCT

        # Position size = risk amount / stop loss distance
        shares = int(risk_amount / stop_loss_distance)

        # Apply maximum position limit from config
        max_position_value = account_equity * Config.MAX_POSITION_PCT
        max_shares = int(max_position_value / price)

        return min(shares, max_shares)


class MomentumBreakoutStrategy(BaseStrategy):
    """
    Momentum breakout strategy: Buy strength, sell weakness.

    Theory: Stocks breaking above recent highs continue moving up (momentum effect).
    Institutional buying triggers at technical levels.

    Parameters:
    - breakout_period: Lookback for high/low (default 20)
    - breakout_threshold: % above high to trigger (default 2%)
    - volume_multiplier: Required volume vs average (default 2x)
    """

    def __init__(self, breakout_period: int = 20, breakout_threshold: float = 0.02,
                 volume_multiplier: float = 2.0):
        super().__init__("MomentumBreakout")
        self.breakout_period = breakout_period
        self.breakout_threshold = breakout_threshold
        self.volume_multiplier = volume_multiplier

    def evaluate(self, symbol: str, cache: MarketDataCache) -> Dict:
        """Generate momentum breakout signal"""

        default_signal = {
            'action': 'HOLD',
            'symbol': symbol,
            'confidence': 0.0,
            'reason': '',
            'quantity': 0
        }

        # Check cooldown
        if not self._check_signal_cooldown(symbol):
            default_signal['reason'] = 'Signal cooldown active'
            return default_signal

        # Get current price
        current_price = cache.get_last_price(symbol)
        if current_price is None:
            default_signal['reason'] = 'No price data available'
            return default_signal

        # Check sufficient data
        if symbol not in cache.trades or len(cache.trades[symbol]) < self.breakout_period:
            default_signal['reason'] = f'Insufficient data (need {self.breakout_period} trades)'
            return default_signal

        # Calculate period high and average volume from previous period (excluding current trade)
        # This ensures we're comparing current price against PREVIOUS highs/lows
        recent_trades = list(cache.trades[symbol])[-(self.breakout_period+1):-1]  # Exclude last trade
        if len(recent_trades) < self.breakout_period:
            default_signal['reason'] = f'Insufficient historical data'
            return default_signal

        prices = np.array([t['price'] for t in recent_trades])
        volumes = np.array([t['size'] for t in recent_trades])

        period_high = np.max(prices)
        period_low = np.min(prices)
        avg_volume = np.mean(volumes)

        # Get current trade volume
        current_volume = cache.trades[symbol][-1]['size']

        # Check for breakout above resistance
        breakout_level = period_high * (1 + self.breakout_threshold)

        if current_price >= breakout_level:
            # Potential breakout - verify with volume
            if current_volume >= avg_volume * self.volume_multiplier:
                self._update_signal_time(symbol)
                self.signals_generated += 1

                breakout_pct = ((current_price - period_high) / period_high) * 100

                return {
                    'action': 'BUY',
                    'symbol': symbol,
                    'confidence': min(breakout_pct / 5.0, 1.0),  # Higher breakout = higher confidence
                    'reason': f'Breakout: {breakout_pct:.1f}% above ${period_high:.2f} high, volume {current_volume/avg_volume:.1f}x avg',
                    'quantity': 0
                }
            else:
                default_signal['reason'] = f'Breakout without volume confirmation ({current_volume/avg_volume:.1f}x < {self.volume_multiplier}x)'
                return default_signal

        # Check for breakdown below support
        breakdown_level = period_low * (1 - self.breakout_threshold)

        if current_price <= breakdown_level:
            if current_volume >= avg_volume * self.volume_multiplier:
                self._update_signal_time(symbol)
                self.signals_generated += 1

                breakdown_pct = ((period_low - current_price) / period_low) * 100

                return {
                    'action': 'SELL',
                    'symbol': symbol,
                    'confidence': min(breakdown_pct / 5.0, 1.0),
                    'reason': f'Breakdown: {breakdown_pct:.1f}% below ${period_low:.2f} low, volume {current_volume/avg_volume:.1f}x avg',
                    'quantity': 0
                }

        default_signal['reason'] = f'No breakout: price ${current_price:.2f} within ${period_low:.2f}-${period_high:.2f} range'
        return default_signal

    def get_position_size(self, symbol: str, price: float, account_equity: float,
                         cache: MarketDataCache) -> int:
        """
        Calculate position size using volatility-adjusted method.
        Higher volatility = smaller position to normalize risk.
        """
        # Calculate ATR (Average True Range) as volatility proxy
        if symbol not in cache.trades or len(cache.trades[symbol]) < 14:
            # Fallback to simple percentage if insufficient data
            max_position_value = account_equity * Config.MAX_POSITION_PCT
            return int(max_position_value / price)

        recent_trades = list(cache.trades[symbol])[-14:]
        prices = np.array([t['price'] for t in recent_trades])

        # Simple ATR approximation: average of high-low ranges
        ranges = []
        for i in range(1, len(prices)):
            ranges.append(abs(prices[i] - prices[i-1]))

        atr = np.mean(ranges) if ranges else price * 0.02  # Default 2% if no ranges

        # Normalize position size by volatility
        # Higher ATR = smaller position
        volatility_pct = atr / price
        risk_adjusted_pct = Config.MAX_POSITION_PCT / max(volatility_pct / 0.02, 1.0)  # 2% baseline

        position_value = account_equity * min(risk_adjusted_pct, Config.MAX_POSITION_PCT)
        return int(position_value / price)


class RegimeDetector:
    """
    Detects market regime to select appropriate strategy.

    Regimes:
    - TRENDING: Low volatility, clear direction → use momentum
    - RANGING: Medium volatility, oscillating → use mean reversion
    - VOLATILE: High volatility → reduce exposure or go to cash
    """

    def __init__(self, api: tradeapi.REST):
        self.api = api
        self.current_regime = "RANGING"  # Default
        self.last_regime_check = None

    def detect_regime(self, spy_cache: MarketDataCache) -> str:
        """
        Detect market regime based on SPY behavior and VIX.

        Args:
            spy_cache: Market data cache for SPY (S&P 500 ETF)

        Returns:
            Regime string: "TRENDING", "RANGING", or "VOLATILE"
        """
        # Only check regime once per hour (expensive calculation)
        if self.last_regime_check:
            time_since_check = (datetime.now() - self.last_regime_check).total_seconds()
            if time_since_check < 3600:  # 1 hour
                return self.current_regime

        try:
            # Get VIX level (volatility index)
            # Note: In production, would fetch from API. Here we use SPY volatility as proxy

            # Check if we have enough SPY data
            if 'SPY' not in spy_cache.trades or len(spy_cache.trades['SPY']) < 20:
                log_warning("Insufficient SPY data for regime detection, using default RANGING")
                return "RANGING"

            # Calculate SPY volatility
            spy_trades = list(spy_cache.trades['SPY'])[-20:]
            spy_prices = np.array([t['price'] for t in spy_trades])

            # Calculate returns volatility
            returns = np.diff(spy_prices) / spy_prices[:-1]
            volatility = np.std(returns) * np.sqrt(252)  # Annualized

            # Calculate trend (slope of moving average)
            ma_slope = (spy_prices[-1] - spy_prices[0]) / len(spy_prices)

            # Regime logic
            if volatility > 0.25:  # >25% annualized volatility
                regime = "VOLATILE"
            elif abs(ma_slope) > 0.1 and volatility < 0.15:  # Clear trend, low volatility
                regime = "TRENDING"
            else:
                regime = "RANGING"

            self.current_regime = regime
            self.last_regime_check = datetime.now()

            log_info(f"Regime detected: {regime} (volatility: {volatility:.2%}, slope: {ma_slope:.4f})")

            return regime

        except Exception as e:
            log_error(f"Regime detection failed: {e}")
            return "RANGING"  # Safe default


class HybridStrategy(BaseStrategy):
    """
    Hybrid strategy that switches between mean reversion and momentum
    based on market regime.

    - TRENDING regime → use momentum breakout
    - RANGING regime → use mean reversion
    - VOLATILE regime → reduce position sizes or go to cash
    """

    def __init__(self, api: tradeapi.REST):
        super().__init__("Hybrid")
        self.mean_reversion = MeanReversionStrategy()
        self.momentum = MomentumBreakoutStrategy()
        self.regime_detector = RegimeDetector(api)
        self.current_strategy = self.mean_reversion  # Default

    def evaluate(self, symbol: str, cache: MarketDataCache,
                spy_cache: Optional[MarketDataCache] = None) -> Dict:
        """
        Evaluate based on current market regime.

        Args:
            symbol: Ticker to analyze
            cache: Market data for the symbol
            spy_cache: Market data for SPY (for regime detection)
        """
        # Detect regime if SPY data available
        if spy_cache:
            regime = self.regime_detector.detect_regime(spy_cache)

            # Select strategy based on regime
            if regime == "TRENDING":
                self.current_strategy = self.momentum
            elif regime == "RANGING":
                self.current_strategy = self.mean_reversion
            elif regime == "VOLATILE":
                # In volatile regime, be very conservative
                return {
                    'action': 'HOLD',
                    'symbol': symbol,
                    'confidence': 0.0,
                    'reason': 'VOLATILE regime detected - staying in cash',
                    'quantity': 0
                }

        # Use selected strategy
        signal = self.current_strategy.evaluate(symbol, cache)

        # Add regime info to reason
        if spy_cache:
            signal['reason'] = f"[{self.regime_detector.current_regime}] {signal['reason']}"

        return signal

    def get_position_size(self, symbol: str, price: float, account_equity: float,
                         cache: MarketDataCache) -> int:
        """Delegate to current active strategy"""
        position_size = self.current_strategy.get_position_size(symbol, price, account_equity, cache)

        # Reduce position size in volatile regime
        if self.regime_detector.current_regime == "VOLATILE":
            position_size = int(position_size * 0.5)  # Half size in volatile markets

        return position_size
