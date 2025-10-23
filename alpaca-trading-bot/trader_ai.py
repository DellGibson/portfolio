#!/usr/bin/env python3
# trader_ai.py — AI-driven Alpaca trading loop with Healthchecks.io + live market data

import os, time, schedule, requests, sys, logging
from dotenv import load_dotenv
from openai import OpenAI
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from flask import Flask, jsonify, redirect, url_for
from threading import Thread
from collections import deque

# === Global Status & Logging ===
bot_status = {
    "status": "Initializing",
    "last_run": "Never",
    "last_action": "None",
    "cash": 0.0,
    "live_price": 0.0
}
RUN_TRADE_NOW = False # Flag for manual trade trigger
log_messages = deque(maxlen=100) # Stores the last 100 log messages
logger = logging.getLogger(__name__)

# Custom logging handler to send logs to our deque
class DequeLogHandler(logging.Handler):
    def __init__(self, deque_instance):
        super().__init__()
        self.deque = deque_instance

    def emit(self, record):
        log_entry = self.format(record)
        self.deque.append(log_entry)

def setup_logging():
    """Configures the logger to output to console and the web UI deque."""
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    
    # 1. Console Handler (to see logs in your terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. Deque Handler (to see logs in the web UI)
    deque_handler = DequeLogHandler(log_messages)
    deque_handler.setFormatter(formatter)
    logger.addHandler(deque_handler)
    
    # Also capture Werkzeug's logs (Flask's web server)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(console_handler)
    werkzeug_logger.addHandler(deque_handler)
    werkzeug_logger.setLevel(logging.INFO)

# === Load keys and config ===
load_dotenv()
logger.info("Starting up...")
logger.info(".env loaded")

API_KEY     = os.getenv("ALPACA_API_KEY_ID")
API_SECRET  = os.getenv("ALPACA_SECRET_KEY")
OPENAI_KEY  = os.getenv("OPENAI_API_KEY")
PING_URL    = os.getenv("HEALTHCHECKS_IO_URL") # More secure to load from .env

if not all([API_KEY, API_SECRET, OPENAI_KEY, PING_URL]):
    logger.critical("Missing one or more environment variables. Exiting.")
    bot_status["status"] = "Error: Missing ENV vars"
    exit()

logger.info(f"Keys loaded: Alpaca={bool(API_KEY)} OpenAI={bool(OPENAI_KEY)} Healthchecks={bool(PING_URL)}")

# === Initialize Clients ===
client_ai = OpenAI(api_key=OPENAI_KEY)
trading   = TradingClient(API_KEY, API_SECRET, paper=True)
data      = StockHistoricalDataClient(API_KEY, API_SECRET)
SYMBOL    = "AAPL" # Define the symbol to trade
bot_status["symbol"] = SYMBOL

# === Web UI Server ===
app = Flask(__name__)

@app.route('/')
def home():
    """Serves the simple HTML status page."""
    
    # Prepare variables for formatting
    status = bot_status.get('status', 'Unknown')
    status_class = 'status-err' if 'Error' in status else 'status-ok'
    symbol = bot_status.get('symbol', 'Unknown')
    cash = bot_status.get('cash', 0.0)
    live_price = bot_status.get('live_price', 0.0)

    html_template = """
    <html>
        <head>
            <title>Trader AI Status</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f4f7f6; color: #333; padding: 20px; }}
                div.container {{ background: #ffffff; border-radius: 10px; padding: 25px; max-width: 900px; margin: 40px auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                h1 {{ color: #222; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                p {{ font-size: 1.1em; line-height: 1.6; }}
                strong {{ color: #00529B; min-width: 150px; display: inline-block; }}
                span.status-ok {{ color: #2E7D32; font-weight: bold; }}
                span.status-err {{ color: #C62828; font-weight: bold; }}
                small {{ color: #777; }}
                button {{ background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; transition: background-color 0.2s; }}
                button:hover {{ background-color: #0056b3; }}
                
                /* New Log Viewer Styles */
                h2 {{ margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 5px; }}
                pre#log-container {{
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 15px;
                    height: 400px;
                    overflow-y: scroll;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 0.9em;
                    white-space: pre-wrap; /* Wrap long lines */
                    word-wrap: break-word; /* Break words if needed */
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Trader AI Status</h1>
                <p><strong>Status:</strong> 
                    <span class="{status_class}">
                        {status}
                    </span>
                </p>
                <p><strong>Symbol:</strong> {symbol}</p>
                <p><strong>Last Run:</strong> {last_run}</p>
                <p><strong>Last Action:</strong> {last_action}</p>
                <p><strong>Account Cash:</strong> ${cash:.2f}</p>
                <p><strong>{symbol} Price:</strong> ${live_price:.2f}</p>
                
                <!-- Manual Trigger Form -->
                <form action="/run_trade" method="POST" style="margin-top: 20px;">
                    <button type="submit">Run Trade Check Now</button>
                </form>

                <!-- New Log Viewer -->
                <h2>Live Log</h2>
                <pre id="log-container">Loading logs...</pre>

                <p style="margin-top: 20px;"><small>Page auto-refreshes every 30 seconds. Logs refresh every 3 seconds.</small></p>
            </div>

            <!-- New JavaScript for logs -->
            <script>
                // Function to fetch and update logs
                function fetchLogs() {{
                    fetch('/logs')
                        .then(response => response.json())
                        .then(data => {{
                            const logContainer = document.getElementById('log-container');
                            // Join log lines with a newline and set as text
                            logContainer.textContent = data.join('\\n'); // Use double-backslash for Python
                            // Auto-scroll to the bottom
                            logContainer.scrollTop = logContainer.scrollHeight;
                        }})
                        .catch(error => {{
                            console.error('Error fetching logs:', error);
                            const logContainer = document.getElementById('log-container');
                            logContainer.textContent = 'Error fetching logs. Check console.';
                        }});
                }}
                
                // Fetch logs immediately on page load
                document.addEventListener('DOMContentLoaded', (event) => {{
                    fetchLogs();
                }});
                
                // Refresh logs every 3 seconds
                setInterval(fetchLogs, 3000);
            </script>
        </body>
    </html>
    """
    
    # Use .format() to safely build the HTML
    return html_template.format(
        status_class=status_class,
        status=status,
        symbol=symbol,
        last_run=bot_status.get('last_run', 'Unknown'),
        last_action=bot_status.get('last_action', 'Unknown'),
        cash=cash,
        live_price=live_price
    )

@app.route('/status')
def status_json():
    """Serves the raw status data as JSON."""
    return jsonify(bot_status)

@app.route('/logs')
def get_logs():
    """Serves the last 100 log messages as JSON."""
    return jsonify(list(log_messages))

@app.route('/run_trade', methods=['POST'])
def trigger_trade():
    """Sets a flag to trigger the trade() function from the UI."""
    global RUN_TRADE_NOW
    RUN_TRADE_NOW = True
    bot_status["status"] = "Manual run requested..."
    logger.info("Manual run requested by user via WebUI.")
    return redirect(url_for('home'))

def run_server():
    """Runs the Flask server on port 5000, accessible from the network."""
    logger.info(f"Starting web server on http://0.0.0.0:5000")
    logger.info(f"Access from another machine via http://YOUR_PI_IP:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

# === Healthchecks.io ===
def ping_healthchecks(status="ok"):
    """Ping Healthchecks.io for status tracking."""
    url = PING_URL
    if status == "start":
        url += "/start"
    elif status == "fail":
        url += "/fail"

    try:
        requests.get(url, timeout=5)
        logger.info(f"Healthcheck ping {status.upper()} sent")
    except Exception as e:
        logger.warning(f"Healthcheck ping failed: {e}")

# === Live Price Fetch ===
def get_live_price(symbol=SYMBOL):
    """Return the most recent trade price for the given stock symbol."""
    try:
        request = StockLatestTradeRequest(symbol_or_symbols=symbol)
        trade = data.get_stock_latest_trade(request)
        
        if symbol not in trade:
             logger.warning(f"No trade data found for {symbol}")
             return 0.0

        price = float(trade[symbol].price)
        logger.info(f"Live {symbol} price: ${price}")
        bot_status["live_price"] = price # Update status
        return price
    except Exception as e:
        logger.error(f"Failed to fetch live price: {e}")
        return 0.0

# === AI Decision Logic ===
def ai_decision(symbol=SYMBOL, price=0):
    """Get a BUY, SELL, or HOLD decision from the AI."""
    prompt = f"You are a cautious trading AI. Given {symbol} current price {price}, respond with ONLY one word: BUY, SELL, or HOLD"
    msg = [{"role": "user", "content": prompt}]
    
    try:
        r = client_ai.chat.completions.create(model="gpt-4o-mini", messages=msg)
        decision = r.choices[0].message.content.strip().upper()
        
        if decision not in ["BUY", "SELL", "HOLD"]:
            logger.warning(f"AI Invalid response: '{decision}'. Defaulting to HOLD.")
            return "HOLD"
        
        return decision
    except Exception as e:
        logger.error(f"AI Decision error: {e}")
        ping_healthchecks("fail")
        return "HOLD"

# === Trade Logic ===
def trade():
    """Main trading logic function."""
    global bot_status
    bot_status["status"] = "Running"
    bot_status["last_run"] = time.ctime()
    ping_healthchecks("start")
    
    logger.info("="*30)
    logger.info(f"Running trade check... {time.ctime()}")
    
    try:
        account = trading.get_account()
        cash = float(account.cash)
        bot_status["cash"] = cash # Update status
        logger.info(f"Account Cash: ${cash:.2f}")

        latest_price = get_live_price(SYMBOL)
        if latest_price <= 0:
            raise ValueError("Invalid live price received.")

        decision = ai_decision(SYMBOL, latest_price)
        logger.info(f"AI Decision: {decision}")

        # --- Act on the decision ---
        if decision == "BUY":
            bot_status["last_action"] = f"BUY attempt at ${latest_price}"
            if cash > latest_price:
                order_data = MarketOrderRequest(
                    symbol=SYMBOL,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                order = trading.submit_order(order_data=order_data)
                logger.info(f"BUY order submitted for 1 {SYMBOL}.")
                logger.info(f"Order details: {order}")
                bot_status["last_action"] = f"BUY order submitted for 1 {SYMBOL}"
            else:
                logger.info("Not enough cash to BUY.")
                bot_status["last_action"] = "BUY attempt (Not enough cash)"
        
        elif decision == "SELL":
            bot_status["last_action"] = f"SELL attempt"
            try:
                position = trading.close_position(SYMBOL)
                logger.info(f"SELL order submitted to close {SYMBOL} position.")
                logger.info(f"Position details: {position}")
                bot_status["last_action"] = f"SELL order submitted for {SYMBOL}"
            except Exception as e:
                logger.info(f"No {SYMBOL} position to sell or other error: {e}")
                bot_status["last_action"] = f"SELL attempt (No position)"
        
        else:
            bot_status["last_action"] = "HOLD"
            logger.info("HOLD. No action taken.")
        
        ping_healthchecks("ok")
        bot_status["status"] = "Scheduled"

    except Exception as e:
        logger.critical(f"CRITICAL ERROR in trade loop: {e}", exc_info=True) # exc_info=True logs the full stack trace
        ping_healthchecks("fail")
        bot_status["status"] = f"Error: {e}"
    
    logger.info("="*30 + "\n")

# === Main Scheduler Loop ===
def main():
    """Main entry point for the trading bot."""
    global RUN_TRADE_NOW
    
    setup_logging() # Set up logging as the very first step
    logger.info("Script starting...")

    # Start the web server in a background thread
    web_thread = Thread(target=run_server, daemon=True)
    web_thread.start()

    logger.info("Running first trade job now.")
    trade() # Run once immediately
    
    logger.info(f"Scheduling job to run every 15 minutes.")
    schedule.every(15).minutes.do(trade)
    
    while True:
        # Check for manual trade trigger
        if RUN_TRADE_NOW:
            logger.info("Manual trade trigger activated!")
            trade()
            RUN_TRADE_NOW = False # Reset the flag
        
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
