# Getting Started Guide - Alpaca Trading Bot

**Complete step-by-step instructions with tests, examples, and workflows**

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running Tests](#running-tests)
5. [First Run](#first-run)
6. [Workflow Examples](#workflow-examples)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
1. **Alpaca Account** (Free)
   - Sign up at: https://alpaca.markets
   - Get Paper Trading API credentials (free, no real money)
   - Navigate to: Dashboard → API Keys → Generate New Key

### Required Software
- **Python 3.8+** (Check: `python --version`)
- **pip** (Check: `pip --version`)
- **Git** (Check: `git --version`)

### System Requirements
- **OS:** Linux, macOS, or Windows
- **RAM:** 512MB minimum
- **Disk:** 100MB free space
- **Internet:** Stable connection required

---

## Installation

### Step 1: Clone the Repository
```bash
# Navigate to your projects folder
cd ~/projects

# Clone the repository
git clone https://github.com/YOUR_USERNAME/portfolio.git
cd portfolio/alpaca-trading-bot

# Verify you're in the right directory
ls -la
# You should see: config.py, main.py, strategy.py, etc.
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# OR activate it (Windows)
venv\Scripts\activate

# Your prompt should now show (venv)
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "numpy|pandas|alpaca|pytest"
```

**Expected Output:**
```
alpaca-trade-api    3.0.2
numpy               1.24.3
pandas              2.0.3
pytest              8.4.2
pytest-asyncio      1.2.0
pytest-cov          7.0.0
python-dotenv       1.0.0
```

### Step 4: Verify Installation
```bash
# Check if imports work
python -c "
import numpy as np
import pandas as pd
import alpaca_trade_api as tradeapi
from config import Config
print('✅ All imports successful!')
"
```

---

## Configuration

### Step 1: Get Your API Keys

1. **Log into Alpaca:** https://app.alpaca.markets
2. **Navigate to:** Paper Trading → API Keys
3. **Generate keys:** Click "Generate New Key"
4. **Copy both:**
   - API Key ID (starts with `PK...`)
   - Secret Key (starts with `...`)

⚠️ **IMPORTANT:** Never share your secret key or commit it to Git!

### Step 2: Create .env File
```bash
# Copy the example file
cp .env.example .env

# Open it in your editor
nano .env   # or vim, code, etc.
```

### Step 3: Configure .env File

**Minimal Configuration (Required):**
```bash
# Alpaca API Credentials (REQUIRED)
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Risk Management (RECOMMENDED - Use defaults to start)
MAX_POSITION_PCT=0.10        # Max 10% of account per position
MAX_DAILY_LOSS_PCT=0.02      # Stop trading if lose 2% in one day
STOP_LOSS_PCT=0.02           # 2% stop loss per trade
TAKE_PROFIT_PCT=0.06         # 6% take profit (3:1 risk/reward)
TRAIL_STOP_PCT=0.015         # 1.5% trailing stop

# Watchlist (Stocks to trade)
WATCHLIST=SPY,QQQ,AAPL,MSFT,TSLA

# Data Feed
DATA_FEED=iex                # Use 'iex' (free, 15min delay) or 'sip' (paid, real-time)
```

**Optional Configuration (Telegram Alerts):**
```bash
# Telegram Bot (Optional - for mobile alerts)
TELEGRAM_BOT_TOKEN=           # Leave empty to disable
TELEGRAM_CHAT_ID=             # Leave empty to disable
```

### Step 4: Verify Configuration
```bash
# Test if config loads correctly
python -c "
from config import Config
print('API Key:', Config.ALPACA_API_KEY[:8] + '...')
print('Watchlist:', Config.WATCHLIST)
print('Max Position:', f'{Config.MAX_POSITION_PCT*100}%')
print('✅ Configuration valid!')
"
```

**Expected Output:**
```
API Key: PKxxxxxx...
Watchlist: ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']
Max Position: 10.0%
✅ Configuration valid!
```

---

## Running Tests

### Test 1: Quick Smoke Test (30 seconds)
```bash
# Run just the cache tests
python -m pytest tests/test_cache.py -v

# Expected: 12 tests passing
```

### Test 2: Full Test Suite (2 minutes)
```bash
# Run all 47 tests with verbose output
python -m pytest tests/ -v

# Expected output:
# ============================== 47 passed in 1.20s ==============================
```

### Test 3: Test with Coverage Report
```bash
# Run tests with code coverage analysis
python -m pytest tests/ --cov=. --cov-report=html

# View report
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html   # Linux
start htmlcov/index.html   # Windows
```

### Test 4: Test Specific Component
```bash
# Test only order management
python -m pytest tests/test_orders.py -v

# Test only strategy logic
python -m pytest tests/test_strategy.py -v

# Test only data cache
python -m pytest tests/test_cache.py -v
```

### Test 5: Dry Run (No API calls)
```bash
# Validate all Python files for syntax errors
python -m py_compile *.py

# Check imports work
python -c "
from config import Config
from data_cache import MarketDataCache
from order_manager import OrderManager
from strategy import MeanReversionStrategy
from main import TradingBot
print('✅ All modules import successfully')
"
```

---

## First Run

### Option A: Paper Trading (Recommended for beginners)

#### Step 1: Verify API Connection
```bash
# Test API connection
python -c "
import alpaca_trade_api as tradeapi
from config import Config

api = tradeapi.REST(
    Config.ALPACA_API_KEY,
    Config.ALPACA_SECRET_KEY,
    Config.ALPACA_BASE_URL
)

account = api.get_account()
print(f'Account Status: {account.status}')
print(f'Buying Power: \${float(account.buying_power):,.2f}')
print(f'Portfolio Value: \${float(account.portfolio_value):,.2f}')
print('✅ API connection successful!')
"
```

**Expected Output:**
```
Account Status: ACTIVE
Buying Power: $100,000.00
Portfolio Value: $100,000.00
✅ API connection successful!
```

#### Step 2: Start the Bot
```bash
# Start paper trading
python main.py

# You should see:
# [2025-11-05 10:30:00] INFO: Configuration validated successfully
# [2025-11-05 10:30:01] INFO: Connected to Alpaca API
# [2025-11-05 10:30:01] INFO: Starting account: $100,000.00
# [2025-11-05 10:30:02] INFO: Subscribed to 5 symbols
# [2025-11-05 10:30:02] INFO: Trading bot is RUNNING
```

#### Step 3: Monitor Output
```bash
# In another terminal, watch the log file
tail -f trading_bot.log

# You should see real-time updates:
# [INFO] Trade: AAPL @ $178.50, size 100
# [INFO] Signal evaluated: AAPL -> HOLD (Within range)
# [INFO] Quote: SPY bid $445.20 / ask $445.22
```

#### Step 4: Stop the Bot
```bash
# Press Ctrl+C in the bot terminal
# The bot will gracefully shutdown:
# [INFO] Keyboard interrupt received
# [INFO] Cancelling all pending orders
# [INFO] Closing all positions
# [INFO] Trading bot stopped
```

### Option B: Backtest Mode (Simulate without API)

```bash
# Run simulation demo with $100
python simulation_demo.py

# This shows all 8 layers without placing real orders
```

---

## Workflow Examples

### Workflow 1: Morning Startup Routine

**Before Market Open (9:00 AM ET)**
```bash
# 1. Activate environment
cd ~/projects/portfolio/alpaca-trading-bot
source venv/bin/activate

# 2. Check API status
python -c "
import alpaca_trade_api as tradeapi
from config import Config
api = tradeapi.REST(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, Config.ALPACA_BASE_URL)
clock = api.get_clock()
print(f'Market Open: {clock.next_open}')
print(f'Is Open: {clock.is_open}')
"

# 3. Review yesterday's performance
tail -100 trading_bot.log | grep "Daily P&L"

# 4. Start bot (it will wait for market open)
python main.py
```

**Output:**
```
Market Open: 2025-11-05 09:30:00-05:00
Is Open: False
[INFO] Market opens in 30.5 minutes - waiting...
[INFO] Market is opening soon - preparing to trade
[INFO] Trading bot is RUNNING
```

### Workflow 2: Strategy Testing

**Test Mean Reversion Strategy:**
```python
# test_mean_reversion_manual.py
from datetime import datetime, timedelta
from data_cache import MarketDataCache
from strategy import MeanReversionStrategy
from unittest.mock import Mock

# Create strategy and cache
strategy = MeanReversionStrategy(lookback_period=20, std_dev_threshold=2.0)
cache = MarketDataCache()

# Add test data (simulating price drop)
now = datetime.now()
for i in range(20):
    price = 100.0 - (i * 0.5)  # Gradual price decline
    cache.add_trade('TEST', price, 1000, now - timedelta(seconds=100-i))

# Add bid/ask spread
cache.add_quote('TEST', 95.00, 95.10, 1000, 1000, now)

# Current price significantly below mean
current_price = 90.00  # Should trigger BUY signal

# Evaluate
cache.add_trade('TEST', current_price, 2000, now)
signal = strategy.evaluate('TEST', cache)

# Display results
print(f"\n{'='*60}")
print(f"Strategy: {strategy.name}")
print(f"Symbol: TEST")
print(f"Current Price: ${current_price:.2f}")
print(f"Signal: {signal['action']}")
print(f"Confidence: {signal['confidence']:.2%}")
print(f"Reason: {signal['reason']}")
print(f"{'='*60}\n")
```

**Run it:**
```bash
python test_mean_reversion_manual.py
```

**Expected Output:**
```
============================================================
Strategy: MeanReversion
Symbol: TEST
Current Price: $90.00
Signal: BUY
Confidence: 85%
Reason: Oversold: -2.54 std devs below mean ($95.00)
============================================================
```

### Workflow 3: Position Sizing Calculator

```bash
# Calculate position size for different scenarios
python -c "
from strategy import MeanReversionStrategy
from data_cache import MarketDataCache
from datetime import datetime, timedelta
from unittest.mock import Mock

strategy = MeanReversionStrategy()
cache = MarketDataCache()

# Add sample price data
now = datetime.now()
for i in range(20):
    cache.add_trade('AAPL', 175.0 + (i * 0.1), 1000, now - timedelta(seconds=100-i))

# Test different account sizes
test_cases = [
    ('Small Account', 1000.00, 175.00),
    ('Medium Account', 10000.00, 175.00),
    ('Large Account', 100000.00, 175.00),
    ('Expensive Stock', 10000.00, 500.00),
]

print('\n' + '='*70)
print('POSITION SIZING CALCULATOR')
print('='*70)

for name, equity, price in test_cases:
    shares = strategy.get_position_size('AAPL', price, equity, cache)
    position_value = shares * price
    pct_of_account = (position_value / equity) * 100

    print(f'\n{name}:')
    print(f'  Account: \${equity:,.2f}')
    print(f'  Price: \${price:.2f}')
    print(f'  Shares: {shares}')
    print(f'  Position Value: \${position_value:,.2f} ({pct_of_account:.1f}% of account)')
    print(f'  Risk per Trade: \${equity * 0.01:.2f} (1% of account)')

print('\n' + '='*70 + '\n')
"
```

### Workflow 4: Daily Performance Report

```bash
# Generate daily summary
python -c "
import re
from datetime import datetime

# Parse today's log file
today = datetime.now().strftime('%Y-%m-%d')
orders_placed = 0
signals_evaluated = 0
errors = 0

with open('trading_bot.log', 'r') as f:
    for line in f:
        if today in line:
            if 'Order submitted' in line:
                orders_placed += 1
            elif 'Signal evaluated' in line:
                signals_evaluated += 1
            elif 'ERROR' in line:
                errors += 1

print('\n' + '='*60)
print(f'DAILY TRADING SUMMARY - {today}')
print('='*60)
print(f'Signals Evaluated: {signals_evaluated}')
print(f'Orders Placed: {orders_placed}')
print(f'Errors: {errors}')
print('='*60 + '\n')

# Get final P&L
print('Run this in Python with API:')
print('  from order_manager import OrderManager')
print('  om = OrderManager(api)')
print('  pnl = om.daily_pnl')
print('  print(f\"Daily P&L: \${pnl:.2f}\")')
"
```

### Workflow 5: Emergency Stop

**If you need to stop trading immediately:**

```bash
# Method 1: Keyboard interrupt (graceful)
# Press Ctrl+C in bot terminal

# Method 2: Kill process (if frozen)
ps aux | grep "python main.py"
kill -9 <PID>

# Method 3: Emergency liquidation script
python -c "
import alpaca_trade_api as tradeapi
from config import Config

api = tradeapi.REST(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, Config.ALPACA_BASE_URL)

# Cancel all orders
api.cancel_all_orders()
print('✅ All orders cancelled')

# Close all positions
positions = api.list_positions()
for position in positions:
    api.close_position(position.symbol)
    print(f'✅ Closed {position.symbol}: {position.qty} shares')

print('\n✅ Emergency stop complete!')
"
```

---

## Monitoring

### Real-Time Monitoring

**Terminal 1: Bot Output**
```bash
python main.py
```

**Terminal 2: Log File**
```bash
tail -f trading_bot.log
```

**Terminal 3: Account Status**
```bash
# Watch script for account updates every 30 seconds
watch -n 30 "python -c \"
import alpaca_trade_api as tradeapi
from config import Config
api = tradeapi.REST(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, Config.ALPACA_BASE_URL)
account = api.get_account()
positions = api.list_positions()
print(f'Portfolio: \\\${float(account.portfolio_value):,.2f}')
print(f'Buying Power: \\\${float(account.buying_power):,.2f}')
print(f'P&L: \\\${float(account.equity) - 100000:.2f}')
print(f'Positions: {len(positions)}')
for p in positions:
    pnl = float(p.unrealized_pl)
    pnl_pct = float(p.unrealized_plpc) * 100
    print(f'  {p.symbol}: {p.qty} @ \\\${float(p.avg_entry_price):.2f} | P&L: \\\${pnl:.2f} ({pnl_pct:+.2f}%)')
\""
```

### Key Metrics to Watch

**1. Daily P&L**
```bash
grep "Daily P&L" trading_bot.log | tail -1
```

**2. Order Fill Rate**
```bash
# Count orders placed vs filled
grep -c "Order submitted" trading_bot.log
grep -c "filled" trading_bot.log
```

**3. Strategy Performance**
```bash
# Count buy vs sell signals
echo "BUY signals: $(grep -c 'Signal evaluated.*BUY' trading_bot.log)"
echo "SELL signals: $(grep -c 'Signal evaluated.*SELL' trading_bot.log)"
echo "HOLD signals: $(grep -c 'Signal evaluated.*HOLD' trading_bot.log)"
```

**4. Error Rate**
```bash
# Check for errors
grep -c "ERROR" trading_bot.log
grep "ERROR" trading_bot.log | tail -5
```

### Alerts Setup (Optional Telegram)

**Step 1: Create Telegram Bot**
1. Open Telegram, search for `@BotFather`
2. Send `/newbot` and follow instructions
3. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Step 2: Get Chat ID**
1. Send a message to your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id":123456789}` in the response

**Step 3: Update .env**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Step 4: Test Alerts**
```python
python -c "
from utils import send_alert
send_alert('🤖 Trading bot connected!', priority='low')
print('Check your Telegram - you should receive a message!')
"
```

---

## Troubleshooting

### Issue 1: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'alpaca_trade_api'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify
pip list | grep alpaca
```

### Issue 2: API Authentication Failed

**Error:**
```
ValueError: Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in environment
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify keys are set
cat .env | grep ALPACA_API_KEY

# Test loading
python -c "
from config import Config
print('API Key:', Config.ALPACA_API_KEY[:10] if Config.ALPACA_API_KEY else 'NOT SET')
"

# If not set, check dotenv is loading
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Loaded:', os.getenv('ALPACA_API_KEY', 'MISSING')[:10])
"
```

### Issue 3: Tests Failing

**Error:**
```
FAILED tests/test_strategy.py::test_buy_signal_breakout
```

**Solution:**
```bash
# Run single test with verbose output
python -m pytest tests/test_strategy.py::test_buy_signal_breakout -vv

# Check if it's the random seed issue
grep "np.random.seed" tests/test_strategy.py

# Verify all test dependencies installed
pip install pytest pytest-asyncio pytest-cov
```

### Issue 4: Bot Won't Start

**Error:**
```
[ERROR] Failed to connect to Alpaca API
```

**Solution:**
```bash
# Test API connection directly
python -c "
import alpaca_trade_api as tradeapi
from config import Config

try:
    api = tradeapi.REST(
        Config.ALPACA_API_KEY,
        Config.ALPACA_SECRET_KEY,
        Config.ALPACA_BASE_URL
    )
    account = api.get_account()
    print(f'✅ Connected! Account: {account.account_number}')
except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('\nCheck:')
    print('1. API keys are correct in .env')
    print('2. Using paper-api URL for paper trading')
    print('3. Internet connection is working')
"
```

### Issue 5: Bot Exits Immediately

**Error:**
```
[INFO] Market closed - initiating shutdown
```

**Solution:**
```bash
# Check market hours
python -c "
import alpaca_trade_api as tradeapi
from config import Config
from datetime import datetime

api = tradeapi.REST(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, Config.ALPACA_BASE_URL)
clock = api.get_clock()

print(f'Current Time: {datetime.now()}')
print(f'Market Open: {clock.is_open}')
print(f'Next Open: {clock.next_open}')
print(f'Next Close: {clock.next_close}')

if not clock.is_open:
    print('\n⚠️  Market is currently CLOSED')
    print('US Stock Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday')
"
```

### Issue 6: No Trades Executing

**Problem:** Bot runs but never places orders

**Solution:**
```bash
# Check signal generation
grep "Signal evaluated" trading_bot.log | tail -20

# Look for reasons signals aren't triggering
grep "reason" trading_bot.log | tail -20

# Common reasons:
# - "Within range" = price not extreme enough for mean reversion
# - "No breakout" = price not breaking resistance/support
# - "Insufficient data" = not enough price history yet
# - "Signal cooldown active" = wait 5 minutes between signals
# - "Wide spread" = stock too illiquid

# Test with more volatile stocks
# Edit .env:
# WATCHLIST=TSLA,GME,AMC,NVDA,AAPL  # More volatile = more signals
```

### Issue 7: Division by Zero Error

**Error:**
```
ZeroDivisionError: division by zero in get_position_size
```

**Solution:**
```bash
# This should be fixed in strategy.py after bug check
# Verify fix is present:
grep "if price <= 0" strategy.py

# Should show:
# if price <= 0:
#     log_warning(f"Invalid price {price} for {symbol} in position sizing")
#     return 0

# If not present, re-pull latest code
git pull origin claude/alpaca-trading-bot-setup-011CUPGM1gWqvDDgFcLiyYJf
```

---

## Quick Reference Commands

```bash
# Installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Testing
python -m pytest tests/ -v                    # Run all tests
python -m pytest tests/test_cache.py -v       # Run specific test file
python -m pytest -k "breakout" -v             # Run tests matching pattern

# Configuration
cp .env.example .env                          # Create config file
nano .env                                     # Edit config

# Running
python main.py                                # Start bot
python simulation_demo.py                     # Run simulation
tail -f trading_bot.log                       # Watch logs

# Monitoring
grep "Daily P&L" trading_bot.log              # Check performance
grep ERROR trading_bot.log                    # Check for errors
ps aux | grep "python main.py"                # Check if running

# Emergency
# Press Ctrl+C to stop gracefully
# Or: kill -9 <PID> to force stop
```

---

## Next Steps

After successfully running the bot:

1. **Week 1:** Run in paper trading mode, monitor daily
2. **Week 2:** Adjust strategy parameters based on performance
3. **Week 3:** Test different watchlists and time periods
4. **Week 4:** Review TEST_VALIDATION_REPORT.md and BUG_REPORT.md
5. **After 4 weeks:** Consider live trading with small capital ($500-1000)

**Important:** Never risk money you can't afford to lose. Start small!

---

## Support Resources

- **Bug Report:** See `BUG_REPORT.md` for known issues
- **Test Report:** See `TEST_VALIDATION_REPORT.md` for test details
- **GUI Options:** See `GUI_ANALYSIS.md` for dashboard options
- **Alpaca Docs:** https://alpaca.markets/docs/
- **Python Help:** https://docs.python.org/3/

---

**Last Updated:** 2025-11-05
**Version:** 1.0.0
**Status:** Production Ready (Paper Trading)
