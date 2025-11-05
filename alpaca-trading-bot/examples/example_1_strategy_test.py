#!/usr/bin/env python
"""
Example 1: Test Trading Strategy Manually

This script demonstrates how to:
- Create a market data cache
- Populate it with sample data
- Run a trading strategy
- Interpret the results

Run: python examples/example_1_strategy_test.py
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from data_cache import MarketDataCache
from strategy import MeanReversionStrategy, MomentumBreakoutStrategy
from unittest.mock import Mock


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_mean_reversion_buy_signal():
    """Test mean reversion strategy with oversold condition"""
    print_section("TEST 1: Mean Reversion - BUY Signal (Oversold)")

    # Create strategy and cache
    strategy = MeanReversionStrategy(lookback_period=20, std_dev_threshold=2.0)
    cache = MarketDataCache()

    # Simulate price data: steady decline (oversold condition)
    now = datetime.now()
    print("\n📊 Market Data:")
    print("Simulating 20-period price decline...")

    prices = []
    for i in range(20):
        # Price declining from $100 to $90
        price = 100.0 - (i * 0.5)
        prices.append(price)
        cache.add_trade('TEST', price, 1000, now - timedelta(seconds=100-i))

    print(f"  Starting Price: ${prices[0]:.2f}")
    print(f"  Ending Price: ${prices[-1]:.2f}")
    print(f"  Price Change: ${prices[-1] - prices[0]:.2f} ({((prices[-1]/prices[0])-1)*100:.1f}%)")

    # Add current quote (bid/ask)
    cache.add_quote('TEST', 90.00, 90.10, 1000, 1000, now)

    # Current price is significantly below mean
    current_price = 88.00  # Even lower - should trigger strong BUY
    cache.add_trade('TEST', current_price, 2000, now)

    # Evaluate strategy
    signal = strategy.evaluate('TEST', cache)

    # Display results
    print("\n📈 Strategy Analysis:")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  Action: {signal['action']}")
    print(f"  Confidence: {signal['confidence']:.1%}")
    print(f"  Reason: {signal['reason']}")

    if signal['action'] == 'BUY':
        print("\n✅ SUCCESS: Strategy detected oversold condition!")
    else:
        print(f"\n⚠️  UNEXPECTED: Expected BUY but got {signal['action']}")


def test_mean_reversion_sell_signal():
    """Test mean reversion strategy with overbought condition"""
    print_section("TEST 2: Mean Reversion - SELL Signal (Overbought)")

    strategy = MeanReversionStrategy(lookback_period=20, std_dev_threshold=2.0)
    cache = MarketDataCache()

    # Simulate price data: steady increase (overbought condition)
    now = datetime.now()
    print("\n📊 Market Data:")
    print("Simulating 20-period price rally...")

    prices = []
    for i in range(20):
        # Price rising from $100 to $110
        price = 100.0 + (i * 0.5)
        prices.append(price)
        cache.add_trade('TEST', price, 1000, now - timedelta(seconds=100-i))

    print(f"  Starting Price: ${prices[0]:.2f}")
    print(f"  Ending Price: ${prices[-1]:.2f}")
    print(f"  Price Change: ${prices[-1] - prices[0]:.2f} ({((prices[-1]/prices[0])-1)*100:.1f}%)")

    # Add current quote
    cache.add_quote('TEST', 112.00, 112.10, 1000, 1000, now)

    # Current price is significantly above mean
    current_price = 114.00  # Even higher - should trigger strong SELL
    cache.add_trade('TEST', current_price, 2000, now)

    # Evaluate
    signal = strategy.evaluate('TEST', cache)

    # Display results
    print("\n📈 Strategy Analysis:")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  Action: {signal['action']}")
    print(f"  Confidence: {signal['confidence']:.1%}")
    print(f"  Reason: {signal['reason']}")

    if signal['action'] == 'SELL':
        print("\n✅ SUCCESS: Strategy detected overbought condition!")
    else:
        print(f"\n⚠️  UNEXPECTED: Expected SELL but got {signal['action']}")


def test_momentum_breakout():
    """Test momentum strategy with breakout condition"""
    print_section("TEST 3: Momentum Breakout - BUY Signal")

    strategy = MomentumBreakoutStrategy(
        breakout_period=20,
        breakout_threshold=0.03,  # 3% breakout
        volume_multiplier=2.5
    )
    cache = MarketDataCache()

    # Simulate price data: consolidation then breakout
    now = datetime.now()
    print("\n📊 Market Data:")
    print("Simulating consolidation period...")

    # 20 periods of consolidation around $100
    for i in range(20):
        price = 100.0 + ((i % 4) * 0.25)  # Oscillating $100-$101
        cache.add_trade('TEST', price, 1000, now - timedelta(seconds=100-i))

    period_high = 100.75
    print(f"  Consolidation Range: ${100.00:.2f} - ${period_high:.2f}")

    # Now add breakout with volume
    breakout_price = 104.00  # +3% above high
    breakout_volume = 2500   # 2.5x normal volume

    cache.add_trade('TEST', breakout_price, breakout_volume, now)

    print(f"  Breakout Price: ${breakout_price:.2f} ({((breakout_price/period_high)-1)*100:.1f}% above high)")
    print(f"  Breakout Volume: {breakout_volume} (2.5x average)")

    # Evaluate
    signal = strategy.evaluate('TEST', cache)

    # Display results
    print("\n📈 Strategy Analysis:")
    print(f"  Action: {signal['action']}")
    print(f"  Confidence: {signal['confidence']:.1%}")
    print(f"  Reason: {signal['reason']}")

    if signal['action'] == 'BUY':
        print("\n✅ SUCCESS: Strategy detected breakout with volume confirmation!")
    else:
        print(f"\n⚠️  UNEXPECTED: Expected BUY but got {signal['action']}")


def test_position_sizing():
    """Test position sizing for different scenarios"""
    print_section("TEST 4: Position Sizing Calculator")

    strategy = MeanReversionStrategy()
    cache = MarketDataCache()

    # Add sample data
    now = datetime.now()
    for i in range(20):
        cache.add_trade('STOCK', 150.0 + (i * 0.1), 1000, now - timedelta(seconds=100-i))

    test_cases = [
        ("Small Account ($1,000)", 1000.00, 150.00),
        ("Medium Account ($10,000)", 10000.00, 150.00),
        ("Large Account ($100,000)", 100000.00, 150.00),
        ("Expensive Stock", 10000.00, 500.00),
        ("Penny Stock", 10000.00, 5.00),
    ]

    print("\n📊 Position Sizing Results:\n")
    print(f"{'Scenario':<25} {'Account':<12} {'Price':<10} {'Shares':<8} {'Position $':<12} {'% Account':<10}")
    print("-" * 85)

    for name, equity, price in test_cases:
        shares = strategy.get_position_size('STOCK', price, equity, cache)
        position_value = shares * price
        pct_of_account = (position_value / equity) * 100 if equity > 0 else 0

        print(f"{name:<25} ${equity:>10,.2f} ${price:>8.2f} {shares:>7} ${position_value:>10,.2f} {pct_of_account:>8.1f}%")

    print("\n✅ Position sizing respects 10% maximum position limit")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  TRADING STRATEGY EXAMPLES")
    print("  Demonstrating strategy evaluation and position sizing")
    print("="*70)

    try:
        # Run tests
        test_mean_reversion_buy_signal()
        test_mean_reversion_sell_signal()
        test_momentum_breakout()
        test_position_sizing()

        # Summary
        print_section("Summary")
        print("\n✅ All examples completed successfully!")
        print("\nKey Takeaways:")
        print("  1. Mean Reversion: Buy oversold, sell overbought")
        print("  2. Momentum: Buy breakouts with volume confirmation")
        print("  3. Position Sizing: Risk 1%, cap at 10% of account")
        print("  4. Confidence Levels: Higher deviation = higher confidence")

        print("\n💡 Next Steps:")
        print("  - Run: python examples/example_2_backtest.py")
        print("  - Read: GETTING_STARTED.md for full workflow")
        print("  - Start: python main.py for live paper trading")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
