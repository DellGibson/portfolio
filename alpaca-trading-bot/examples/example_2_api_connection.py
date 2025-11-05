#!/usr/bin/env python
"""
Example 2: Test Alpaca API Connection

This script demonstrates how to:
- Connect to Alpaca API
- Verify account access
- Check market status
- View current positions
- Get account balance

Run: python examples/example_2_api_connection.py
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import alpaca_trade_api as tradeapi
from config import Config
from datetime import datetime


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_configuration():
    """Test 1: Verify configuration is loaded"""
    print_section("TEST 1: Configuration Check")

    try:
        # Check API keys
        if not Config.ALPACA_API_KEY:
            print("❌ ALPACA_API_KEY is not set")
            print("   Please check your .env file")
            return False

        if not Config.ALPACA_SECRET_KEY:
            print("❌ ALPACA_SECRET_KEY is not set")
            print("   Please check your .env file")
            return False

        print(f"✅ API Key: {Config.ALPACA_API_KEY[:8]}... (hidden)")
        print(f"✅ Secret Key: {Config.ALPACA_SECRET_KEY[:8]}... (hidden)")
        print(f"✅ Base URL: {Config.ALPACA_BASE_URL}")

        # Check other settings
        print(f"\n📋 Risk Settings:")
        print(f"   Max Position: {Config.MAX_POSITION_PCT*100:.1f}%")
        print(f"   Daily Loss Limit: {Config.MAX_DAILY_LOSS_PCT*100:.1f}%")
        print(f"   Stop Loss: {Config.STOP_LOSS_PCT*100:.1f}%")
        print(f"   Take Profit: {Config.TAKE_PROFIT_PCT*100:.1f}%")

        print(f"\n📋 Watchlist: {', '.join(Config.WATCHLIST)}")
        print(f"📋 Data Feed: {Config.DATA_FEED}")

        return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_api_connection():
    """Test 2: Connect to Alpaca API"""
    print_section("TEST 2: API Connection")

    try:
        # Initialize API
        print("Connecting to Alpaca API...")
        api = tradeapi.REST(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY,
            Config.ALPACA_BASE_URL
        )

        # Get account info
        account = api.get_account()

        print(f"✅ Connected successfully!")
        print(f"\n📊 Account Details:")
        print(f"   Account Number: {account.account_number}")
        print(f"   Status: {account.status}")
        print(f"   Pattern Day Trader: {account.pattern_day_trader}")

        return api

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your API keys in .env file")
        print("   2. Verify you're using paper-api URL for paper trading")
        print("   3. Check internet connection")
        print("   4. Try generating new API keys from Alpaca dashboard")
        return None


def test_account_balance(api):
    """Test 3: Get account balance and buying power"""
    print_section("TEST 3: Account Balance")

    try:
        account = api.get_account()

        # Portfolio value
        portfolio_value = float(account.portfolio_value)
        equity = float(account.equity)
        cash = float(account.cash)
        buying_power = float(account.buying_power)

        print(f"💰 Account Balance:")
        print(f"   Portfolio Value: ${portfolio_value:,.2f}")
        print(f"   Total Equity: ${equity:,.2f}")
        print(f"   Cash: ${cash:,.2f}")
        print(f"   Buying Power: ${buying_power:,.2f}")

        # P&L
        if hasattr(account, 'equity') and hasattr(account, 'last_equity'):
            last_equity = float(account.last_equity)
            daily_pnl = equity - last_equity
            daily_pnl_pct = (daily_pnl / last_equity * 100) if last_equity > 0 else 0

            print(f"\n📈 Performance:")
            print(f"   Daily P&L: ${daily_pnl:,.2f} ({daily_pnl_pct:+.2f}%)")

        return True

    except Exception as e:
        print(f"❌ Failed to get account balance: {e}")
        return False


def test_market_status(api):
    """Test 4: Check market hours"""
    print_section("TEST 4: Market Status")

    try:
        clock = api.get_clock()

        print(f"🕐 Market Status:")
        print(f"   Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Market Open: {'✅ YES' if clock.is_open else '❌ NO'}")

        if clock.is_open:
            print(f"   Next Close: {clock.next_close}")
        else:
            print(f"   Next Open: {clock.next_open}")

        # Get calendar
        from datetime import date, timedelta
        today = date.today()
        calendar = api.get_calendar(start=today, end=today + timedelta(days=7))

        print(f"\n📅 Trading Days (Next 7 Days):")
        for day in calendar[:5]:  # Show max 5 days
            print(f"   {day.date}: {day.open} - {day.close}")

        return True

    except Exception as e:
        print(f"❌ Failed to get market status: {e}")
        return False


def test_positions(api):
    """Test 5: View current positions"""
    print_section("TEST 5: Current Positions")

    try:
        positions = api.list_positions()

        if not positions:
            print("📭 No open positions")
            print("   Your account has no current holdings")
            return True

        print(f"📊 Open Positions ({len(positions)} total):\n")
        print(f"{'Symbol':<8} {'Qty':<8} {'Entry $':<12} {'Current $':<12} {'P&L $':<12} {'P&L %':<10}")
        print("-" * 72)

        total_pnl = 0
        for position in positions:
            symbol = position.symbol
            qty = int(position.qty)
            entry_price = float(position.avg_entry_price)
            current_price = float(position.current_price)
            pnl = float(position.unrealized_pl)
            pnl_pct = float(position.unrealized_plpc) * 100
            total_pnl += pnl

            print(f"{symbol:<8} {qty:<8} ${entry_price:<11,.2f} ${current_price:<11,.2f} ${pnl:<11,.2f} {pnl_pct:>+8.2f}%")

        print("-" * 72)
        print(f"{'TOTAL':<8} {'':<8} {'':<12} {'':<12} ${total_pnl:<11,.2f}")

        return True

    except Exception as e:
        print(f"❌ Failed to get positions: {e}")
        return False


def test_orders(api):
    """Test 6: View recent orders"""
    print_section("TEST 6: Recent Orders")

    try:
        # Get orders from last 7 days
        from datetime import date, timedelta
        after = (date.today() - timedelta(days=7)).isoformat()

        orders = api.list_orders(status='all', limit=10, after=after)

        if not orders:
            print("📭 No recent orders")
            print("   No orders placed in the last 7 days")
            return True

        print(f"📋 Recent Orders ({len(orders)} shown):\n")
        print(f"{'Symbol':<8} {'Side':<6} {'Qty':<6} {'Type':<10} {'Status':<10} {'Time':<20}")
        print("-" * 70)

        for order in orders[:10]:  # Show max 10
            symbol = order.symbol
            side = order.side
            qty = order.qty
            order_type = order.type
            status = order.status
            created_at = order.created_at.strftime('%Y-%m-%d %H:%M:%S')

            print(f"{symbol:<8} {side:<6} {qty:<6} {order_type:<10} {status:<10} {created_at}")

        return True

    except Exception as e:
        print(f"❌ Failed to get orders: {e}")
        return False


def test_quote(api):
    """Test 7: Get real-time quote"""
    print_section("TEST 7: Real-Time Quote Test")

    try:
        symbol = 'SPY'  # Test with SPY ETF
        print(f"Getting quote for {symbol}...")

        quote = api.get_latest_quote(symbol)

        bid = float(quote.bp)
        ask = float(quote.ap)
        bid_size = int(quote.bs)
        ask_size = int(quote.as_)
        spread = ask - bid
        spread_pct = (spread / bid * 100) if bid > 0 else 0

        print(f"\n📊 {symbol} Quote:")
        print(f"   Bid: ${bid:.2f} x {bid_size}")
        print(f"   Ask: ${ask:.2f} x {ask_size}")
        print(f"   Spread: ${spread:.2f} ({spread_pct:.3f}%)")

        # Get latest trade
        trade = api.get_latest_trade(symbol)
        price = float(trade.p)
        size = int(trade.s)

        print(f"\n📊 {symbol} Last Trade:")
        print(f"   Price: ${price:.2f}")
        print(f"   Size: {size} shares")

        return True

    except Exception as e:
        print(f"❌ Failed to get quote: {e}")
        return False


def main():
    """Run all connection tests"""
    print("\n" + "="*70)
    print("  ALPACA API CONNECTION TEST")
    print("  Verifying configuration and API access")
    print("="*70)

    # Track results
    tests_passed = 0
    tests_total = 7

    # Test 1: Configuration
    if test_configuration():
        tests_passed += 1
    else:
        print("\n❌ Configuration test failed - cannot continue")
        print("   Please fix your .env file and try again")
        return 1

    # Test 2: API Connection
    api = test_api_connection()
    if api:
        tests_passed += 1
    else:
        print("\n❌ API connection failed - cannot continue")
        print("   Please check your credentials and try again")
        return 1

    # Test 3-7: Account tests
    if test_account_balance(api):
        tests_passed += 1

    if test_market_status(api):
        tests_passed += 1

    if test_positions(api):
        tests_passed += 1

    if test_orders(api):
        tests_passed += 1

    if test_quote(api):
        tests_passed += 1

    # Summary
    print_section("Test Summary")
    print(f"\n✅ Passed: {tests_passed}/{tests_total} tests")

    if tests_passed == tests_total:
        print("\n🎉 All tests passed! You're ready to start trading.")
        print("\n💡 Next Steps:")
        print("   1. Review your account settings above")
        print("   2. Run: python examples/example_1_strategy_test.py")
        print("   3. Start bot: python main.py")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")
        print("   Please review the errors above and fix them before continuing")

    return 0 if tests_passed == tests_total else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
