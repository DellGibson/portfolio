# Trader AI Web Interface

## Overview
The `trader_ai.py` script includes a built-in Flask web interface accessible at `http://localhost:5000` (or `http://YOUR_PI_IP:5000` from other devices on the network).

## Features

### Main Dashboard (`/`)
The home page displays:
- **Status**: Current bot status (Scheduled, Running, Error, etc.)
- **Symbol**: Stock symbol being traded (default: AAPL)
- **Last Run**: Timestamp of the last trade check
- **Last Action**: Description of the last action taken (BUY, SELL, HOLD)
- **Account Cash**: Current cash balance in the Alpaca account
- **Live Price**: Current market price of the stock
- **Manual Trigger Button**: "Run Trade Check Now" button to trigger an immediate trade check
- **Live Log Viewer**: Scrollable log viewer showing the last 100 log messages (auto-refreshes every 3 seconds)

### API Endpoints

#### `/status` (JSON)
Returns raw status data in JSON format:
```json
{
  "status": "Scheduled",
  "last_run": "Wed Oct 23 06:00:00 2025",
  "last_action": "HOLD",
  "cash": 100000.00,
  "live_price": 175.43,
  "symbol": "AAPL"
}
```

#### `/logs` (JSON)
Returns the last 100 log messages as a JSON array:
```json
[
  "2025-10-23 06:00:00 - INFO - Running trade check...",
  "2025-10-23 06:00:01 - INFO - Account Cash: $100000.00",
  "2025-10-23 06:00:02 - INFO - Live AAPL price: $175.43",
  "2025-10-23 06:00:03 - INFO - AI Decision: HOLD"
]
```

#### `/run_trade` (POST)
Triggers an immediate trade check. Redirects back to the home page.

## Page Refresh
- The main page auto-refreshes every 30 seconds
- The log viewer auto-refreshes every 3 seconds via JavaScript

## Styling
The interface uses a clean, modern design with:
- Responsive layout centered on the page
- Color-coded status indicators (green for OK, red for errors)
- Dark-themed log viewer with monospace font
- Auto-scrolling log container
- Professional blue button styling with hover effects

## Monitoring
The log viewer provides real-time insight into:
- Trade check execution
- AI decision-making process
- API interactions
- Health check pings
- Errors and warnings

## Security Notes
- The web server binds to `0.0.0.0:5000` to allow network access
- No authentication is implemented (suitable for internal networks only)
- API keys are never displayed in the UI
- Logs are limited to the last 100 messages (no persistence)
