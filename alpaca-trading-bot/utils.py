"""
Logging and alerting utilities.
Why: Need visibility into bot decisions without blocking execution.
"""
import logging
from datetime import datetime
from typing import Optional
import requests
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_info(message: str):
    """Log informational message"""
    logger.info(message)

def log_error(message: str):
    """Log error message"""
    logger.error(message)

def log_warning(message: str):
    """Log warning message"""
    logger.warning(message)

def send_alert(message: str, priority: str = 'low'):
    """
    Send alert via Telegram.
    Args:
        priority: 'low', 'medium', 'high', 'critical'
    Why: Need to know about important events without constantly monitoring.
    """
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        return  # Alerts disabled

    # Add emoji based on priority
    emoji_map = {
        'low': '',
        'medium': '',
        'high': '',
        'critical': ''
    }

    formatted_message = f"{emoji_map.get(priority, '')} {message}"

    try:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': Config.TELEGRAM_CHAT_ID,
            'text': formatted_message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload, timeout=5)

        if response.status_code != 200:
            log_error(f"Failed to send alert: {response.text}")

    except Exception as e:
        log_error(f"Alert sending error: {e}")

def format_currency(value: float) -> str:
    """Format number as USD currency"""
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    """Format number as percentage"""
    return f"{value*100:.2f}%"
