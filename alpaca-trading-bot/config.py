"""
Configuration management with environment variables.
Why: Never hardcode API keys. Use .env file for security.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Alpaca API credentials (get from alpaca.markets dashboard)
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

    # Risk management parameters
    MAX_POSITION_PCT = float(os.getenv('MAX_POSITION_PCT', '0.10'))  # 10% max per position
    MAX_DAILY_LOSS_PCT = float(os.getenv('MAX_DAILY_LOSS_PCT', '0.02'))  # 2% max daily loss
    STOP_LOSS_PCT = float(os.getenv('STOP_LOSS_PCT', '0.02'))  # 2% stop loss
    TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT_PCT', '0.06'))  # 6% take profit (3:1 ratio)
    TRAIL_STOP_PCT = float(os.getenv('TRAIL_STOP_PCT', '0.015'))  # 1.5% trailing stop

    # Strategy parameters
    WATCHLIST = os.getenv('WATCHLIST', 'SPY,QQQ,AAPL,MSFT,TSLA').split(',')

    # Data feed
    DATA_FEED = os.getenv('DATA_FEED', 'iex')  # 'iex' (free, delayed) or 'sip' (paid, real-time)

    # Alerts (optional - leave empty to disable)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

    @classmethod
    def validate(cls):
        """Ensure required config is present. Call this explicitly in main.py before starting the bot."""
        if not cls.ALPACA_API_KEY or not cls.ALPACA_SECRET_KEY:
            raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in environment")
        return True

# Note: Validation is NOT called on import to allow testing with mocks.
# Call Config.validate() explicitly in main.py before starting the bot.
