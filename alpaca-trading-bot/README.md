# Alpaca Trading Bot

Automated trading bot built with Alpaca API featuring real-time market data caching, comprehensive risk management, and intelligent order execution.

## Features

- **Multiple Trading Strategies**: Mean reversion, momentum breakout, and hybrid regime-based strategies
- **Real-time Market Data**: WebSocket streaming with VWAP calculations and spread analysis
- **Risk Management**: Position sizing, daily loss limits, buying power validation
- **Smart Order Execution**: Limit order pricing to minimize slippage
- **Bracket Orders**: Automatic stop-loss and take-profit (3:1 reward:risk ratio)
- **Regime Detection**: Adapts strategy based on market conditions (trending/ranging/volatile)
- **Telegram Alerts**: Real-time trade notifications
- **Comprehensive Testing**: 40+ unit tests with pytest
- **Async Architecture**: Handles 100+ ticks/second efficiently

## Project Structure

```
alpaca-trading-bot/
├── config.py           # API keys and configuration
├── data_cache.py       # Real-time market data storage
├── order_manager.py    # Order execution and risk management
├── strategy.py         # Trading strategy logic (mean reversion, momentum, hybrid)
├── main.py            # Main trading loop (async event-driven)
├── utils.py           # Logging and alerting utilities
├── requirements.txt   # Dependencies
├── pytest.ini         # Test configuration
└── tests/             # Unit tests (40+ tests)
    ├── test_cache.py
    ├── test_orders.py
    └── test_strategy.py
```

## Setup Instructions

### 1. Create Alpaca Account

1. Sign up at https://alpaca.markets
2. Create a paper trading account (free, uses simulated money)
3. Get your API keys from the dashboard

### 2. Install Dependencies

```bash
cd alpaca-trading-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required configuration in `.env`:
```
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

Optional configuration:
```
MAX_POSITION_PCT=0.10        # Max 10% of portfolio per position
MAX_DAILY_LOSS_PCT=0.02      # Max 2% daily loss
WATCHLIST=SPY,QQQ,AAPL,MSFT  # Symbols to trade
DATA_FEED=iex                # 'iex' (free) or 'sip' (paid)
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_strategy.py -v
```

### 5. Start Trading Bot

```bash
# Start the bot (will wait for market open)
python main.py

# The bot will:
# 1. Validate API credentials
# 2. Sync current positions
# 3. Wait for market open
# 4. Subscribe to real-time data streams
# 5. Execute trades based on strategy signals
# 6. Shutdown gracefully at market close
```

## Risk Management

The bot includes multiple safety features:

- **Position Sizing**: Max 10% of portfolio per position (configurable)
- **Daily Loss Limit**: Stops trading if down 2% for the day (configurable)
- **Stop Loss**: Automatic 2% stop loss on all positions
- **Take Profit**: Automatic 6% take profit (3:1 reward:risk ratio)
- **Market Hours Check**: Only trades during market hours
- **Buying Power Validation**: Prevents over-leveraging

## Development Status

- [x] Step 1: Dependencies & Configuration
- [x] Step 2: Market Data Cache
- [x] Step 3: Order Management System
- [x] Step 4: Utilities (Logging & Alerts)
- [x] Step 5: Trading Strategy Logic (Mean Reversion, Momentum, Hybrid)
- [x] Step 6: Main Trading Loop (Async WebSocket Event Handling)
- [x] Step 7: Unit Tests (40+ tests with >80% coverage)

## Available Strategies

### 1. Mean Reversion Strategy
- **Theory**: Prices oscillate around moving average
- **Entry**: Buy when price >2 std devs below mean (oversold)
- **Exit**: Sell when price >2 std devs above mean (overbought)
- **Best For**: Range-bound markets with low volatility

### 2. Momentum Breakout Strategy
- **Theory**: Breakouts above resistance continue upward
- **Entry**: Buy when price breaks >2% above 20-period high with 2x volume
- **Exit**: Sell on breakdown or stop loss trigger
- **Best For**: Trending markets with clear directional movement

### 3. Hybrid Strategy (Default)
- **Regime Detection**: Analyzes SPY volatility and trend
- **Trending Market**: Uses momentum breakout strategy
- **Ranging Market**: Uses mean reversion strategy
- **Volatile Market**: Reduces position sizes or goes to cash
- **Best For**: Adaptive to all market conditions

## Security Notes

- **NEVER** commit `.env` file to git (it's in `.gitignore`)
- Start with paper trading to test strategies
- Monitor the bot regularly, especially in early stages
- Set conservative risk parameters initially

## Optional: Telegram Alerts

To enable trade notifications via Telegram:

1. Create a Telegram bot with @BotFather
2. Get your bot token
3. Get your chat ID (message @userinfobot)
4. Add to `.env`:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## License

MIT License - Use at your own risk. This is educational software.

## Disclaimer

Trading involves risk. This bot is for educational purposes. Always test strategies thoroughly with paper trading before using real money.
