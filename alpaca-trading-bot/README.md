# Alpaca Trading Bot

Automated trading bot built with Alpaca API featuring real-time market data caching, comprehensive risk management, and intelligent order execution.

## Features

- Real-time market data caching with VWAP calculations
- Pre-trade risk validation (position sizing, daily loss limits, buying power)
- Smart limit order pricing to minimize slippage
- Bracket orders with automatic stop-loss and take-profit
- Telegram alerts for trade notifications
- Comprehensive logging and error handling

## Project Structure

```
alpaca-trading-bot/
├── config.py           # API keys and configuration
├── data_cache.py       # Real-time market data storage
├── order_manager.py    # Order execution and risk management
├── strategy.py         # Trading strategy logic (coming in Step 5)
├── main.py            # Main trading loop (coming in Step 6)
├── utils.py           # Logging and alerting utilities
├── requirements.txt   # Dependencies
└── tests/             # Unit tests (coming in Step 7)
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

### 4. Run Tests (after Step 7)

```bash
pytest tests/ -v
```

### 5. Start Trading Bot (after Step 6)

```bash
python main.py
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
- [ ] Step 5: Trading Strategy Logic
- [ ] Step 6: Main Trading Loop
- [ ] Step 7: Unit Tests

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
