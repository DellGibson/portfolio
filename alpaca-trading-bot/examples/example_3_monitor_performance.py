#!/usr/bin/env python
"""
Example 3: Monitor Trading Performance

This script demonstrates how to:
- Parse trading logs
- Calculate performance metrics
- Display daily statistics
- Track signal generation
- Monitor error rates

Run: python examples/example_3_monitor_performance.py
"""

import sys
import re
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from collections import defaultdict


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def parse_log_file(log_path='trading_bot.log', days=1):
    """Parse trading bot log file"""
    if not os.path.exists(log_path):
        return None

    # Calculate cutoff date
    cutoff = datetime.now() - timedelta(days=days)

    # Data structures
    logs = {
        'trades': [],
        'signals': [],
        'orders': [],
        'errors': [],
        'warnings': [],
        'info': []
    }

    # Parse log file
    with open(log_path, 'r') as f:
        for line in f:
            try:
                # Extract timestamp
                timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                if not timestamp_match:
                    continue

                timestamp_str = timestamp_match.group(1)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                # Only process recent logs
                if timestamp < cutoff:
                    continue

                # Categorize log entries
                if 'Trade:' in line:
                    logs['trades'].append({'time': timestamp, 'line': line})
                elif 'Signal evaluated' in line:
                    logs['signals'].append({'time': timestamp, 'line': line})
                elif 'Order submitted' in line or 'Bracket order' in line:
                    logs['orders'].append({'time': timestamp, 'line': line})
                elif 'ERROR' in line:
                    logs['errors'].append({'time': timestamp, 'line': line})
                elif 'WARNING' in line:
                    logs['warnings'].append({'time': timestamp, 'line': line})
                else:
                    logs['info'].append({'time': timestamp, 'line': line})

            except Exception:
                continue

    return logs


def analyze_signals(logs):
    """Analyze trading signals"""
    print_section("Signal Analysis")

    if not logs or 'signals' not in logs:
        print("❌ No log data available")
        return

    signals = logs['signals']

    if not signals:
        print("📭 No signals generated yet")
        print("   The bot may still be collecting data or waiting for trading opportunities")
        return

    # Count signal types
    signal_counts = defaultdict(int)
    confidence_levels = []

    for signal in signals:
        line = signal['line']

        # Extract action (BUY, SELL, HOLD)
        if 'BUY' in line:
            signal_counts['BUY'] += 1
        elif 'SELL' in line:
            signal_counts['SELL'] += 1
        elif 'HOLD' in line:
            signal_counts['HOLD'] += 1

        # Extract confidence if present
        confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)', line, re.IGNORECASE)
        if confidence_match:
            confidence_levels.append(float(confidence_match.group(1)))

    # Display results
    total_signals = sum(signal_counts.values())
    print(f"\n📊 Signal Summary (Last 24h):")
    print(f"   Total Signals: {total_signals}")
    print(f"   - BUY signals: {signal_counts['BUY']} ({signal_counts['BUY']/total_signals*100:.1f}%)")
    print(f"   - SELL signals: {signal_counts['SELL']} ({signal_counts['SELL']/total_signals*100:.1f}%)")
    print(f"   - HOLD signals: {signal_counts['HOLD']} ({signal_counts['HOLD']/total_signals*100:.1f}%)")

    if confidence_levels:
        avg_confidence = sum(confidence_levels) / len(confidence_levels)
        print(f"\n📈 Average Confidence: {avg_confidence:.1%}")

    # Show recent signals
    print(f"\n📋 Recent Signals (Last 5):")
    for signal in signals[-5:]:
        time_str = signal['time'].strftime('%H:%M:%S')
        line_clean = signal['line'].split(']', 2)[-1].strip()
        print(f"   [{time_str}] {line_clean[:80]}")


def analyze_orders(logs):
    """Analyze order execution"""
    print_section("Order Execution")

    if not logs or 'orders' not in logs:
        print("❌ No log data available")
        return

    orders = logs['orders']

    if not orders:
        print("📭 No orders placed yet")
        print("   The bot is monitoring but hasn't found high-confidence signals")
        return

    # Count order types
    order_types = defaultdict(int)
    symbols = defaultdict(int)

    for order in orders:
        line = order['line']

        # Extract side
        if ' buy ' in line.lower():
            order_types['BUY'] += 1
        elif ' sell ' in line.lower():
            order_types['SELL'] += 1

        # Extract symbol
        symbol_match = re.search(r'[A-Z]{2,5}', line)
        if symbol_match:
            symbols[symbol_match.group(0)] += 1

    # Display results
    total_orders = len(orders)
    print(f"\n📊 Order Summary (Last 24h):")
    print(f"   Total Orders: {total_orders}")
    print(f"   - Buy Orders: {order_types['BUY']}")
    print(f"   - Sell Orders: {order_types['SELL']}")

    if symbols:
        print(f"\n📊 Most Traded Symbols:")
        sorted_symbols = sorted(symbols.items(), key=lambda x: x[1], reverse=True)
        for symbol, count in sorted_symbols[:5]:
            print(f"   {symbol}: {count} orders")

    # Show recent orders
    print(f"\n📋 Recent Orders (Last 5):")
    for order in orders[-5:]:
        time_str = order['time'].strftime('%H:%M:%S')
        line_clean = order['line'].split(']', 2)[-1].strip()
        print(f"   [{time_str}] {line_clean[:80]}")


def analyze_errors(logs):
    """Analyze errors and warnings"""
    print_section("Error Analysis")

    if not logs:
        print("❌ No log data available")
        return

    errors = logs.get('errors', [])
    warnings = logs.get('warnings', [])

    if not errors and not warnings:
        print("✅ No errors or warnings in the last 24 hours!")
        print("   System is running smoothly")
        return

    # Display error summary
    print(f"\n📊 Issue Summary:")
    print(f"   Errors: {len(errors)}")
    print(f"   Warnings: {len(warnings)}")

    # Show recent errors
    if errors:
        print(f"\n❌ Recent Errors (Last 5):")
        for error in errors[-5:]:
            time_str = error['time'].strftime('%H:%M:%S')
            line_clean = error['line'].split(']', 2)[-1].strip()
            print(f"   [{time_str}] {line_clean[:80]}")

    # Show recent warnings
    if warnings:
        print(f"\n⚠️  Recent Warnings (Last 5):")
        for warning in warnings[-5:]:
            time_str = warning['time'].strftime('%H:%M:%S')
            line_clean = warning['line'].split(']', 2)[-1].strip()
            print(f"   [{time_str}] {line_clean[:80]}")


def analyze_activity(logs):
    """Analyze overall activity"""
    print_section("Activity Overview")

    if not logs:
        print("❌ No log data available")
        return

    trades = logs.get('trades', [])
    signals = logs.get('signals', [])
    orders = logs.get('orders', [])

    if not trades:
        print("📭 No market data received yet")
        print("   Waiting for bot to start or market to open")
        return

    # Calculate activity metrics
    total_trades = len(trades)
    total_signals = len(signals)
    total_orders = len(orders)

    # Calculate time range
    if trades:
        first_trade = trades[0]['time']
        last_trade = trades[-1]['time']
        duration = (last_trade - first_trade).total_seconds() / 60  # minutes

        print(f"\n📊 Activity Metrics:")
        print(f"   Session Duration: {duration:.1f} minutes")
        print(f"   Market Ticks Processed: {total_trades:,}")
        print(f"   Signals Evaluated: {total_signals:,}")
        print(f"   Orders Placed: {total_orders}")

        if duration > 0:
            print(f"\n📈 Rate Analysis:")
            print(f"   Ticks per Minute: {total_trades/duration:.1f}")
            print(f"   Signals per Hour: {total_signals/(duration/60):.1f}")

        # Calculate signal-to-order conversion
        if total_signals > 0:
            conversion = (total_orders / total_signals) * 100
            print(f"   Signal → Order Conversion: {conversion:.2f}%")


def check_log_health():
    """Check if bot is currently running"""
    print_section("System Health Check")

    log_path = 'trading_bot.log'

    if not os.path.exists(log_path):
        print("❌ Log file not found")
        print(f"   Expected: {log_path}")
        print("   The bot may not have been started yet")
        return False

    # Check last modified time
    mod_time = os.path.getmtime(log_path)
    mod_datetime = datetime.fromtimestamp(mod_time)
    age_minutes = (datetime.now() - mod_datetime).total_seconds() / 60

    print(f"\n📄 Log File:")
    print(f"   Path: {log_path}")
    print(f"   Size: {os.path.getsize(log_path):,} bytes")
    print(f"   Last Updated: {mod_datetime.strftime('%Y-%m-%d %H:%M:%S')} ({age_minutes:.1f} min ago)")

    if age_minutes < 5:
        print(f"   Status: ✅ ACTIVE (Recently updated)")
        return True
    elif age_minutes < 60:
        print(f"   Status: ⚠️  IDLE (No updates in {age_minutes:.0f} minutes)")
        return True
    else:
        print(f"   Status: ❌ STALE (No updates in {age_minutes/60:.1f} hours)")
        print("   The bot may not be running")
        return False


def main():
    """Run performance monitoring"""
    print("\n" + "="*70)
    print("  TRADING PERFORMANCE MONITOR")
    print("  Analyzing bot activity and performance")
    print("="*70)

    # Check system health
    is_running = check_log_health()

    # Parse logs
    print("\nParsing log files...")
    logs = parse_log_file(days=1)

    if not logs:
        print("\n❌ Could not parse log file")
        print("\n💡 Next Steps:")
        print("   1. Make sure the bot has been started: python main.py")
        print("   2. Check that trading_bot.log exists in current directory")
        print("   3. Try running the bot for a few minutes to generate logs")
        return 1

    # Analyze different aspects
    try:
        analyze_activity(logs)
        analyze_signals(logs)
        analyze_orders(logs)
        analyze_errors(logs)

        # Summary
        print_section("Summary")

        if is_running:
            print("\n✅ Bot is running and generating logs")
        else:
            print("\n⚠️  Bot may not be actively trading")

        print("\n💡 Tips:")
        print("   - Run this script periodically to monitor performance")
        print("   - Check 'Error Analysis' section for issues")
        print("   - High HOLD signal rate is normal (most conditions don't trigger trades)")
        print("   - Low order count means bot is being selective (this is good!)")

        print("\n📚 For More Details:")
        print("   - Full logs: tail -f trading_bot.log")
        print("   - Test connection: python examples/example_2_api_connection.py")
        print("   - View positions: Check Alpaca dashboard")

        return 0

    except Exception as e:
        print(f"\n❌ Error analyzing logs: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user")
        sys.exit(1)
