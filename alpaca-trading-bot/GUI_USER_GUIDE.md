# Desktop GUI User Guide
## Alpaca Trading Bot - Professional Desktop Application

**Version:** 1.0.0
**Platform:** Windows, macOS, Linux
**Framework:** PyQt6

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [First Launch](#first-launch)
3. [Interface Overview](#interface-overview)
4. [Features](#features)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [System Tray](#system-tray)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### Step 1: Install Dependencies

```bash
# Make sure you're in the alpaca-trading-bot directory
cd alpaca-trading-bot

# Install PyQt6 and related packages
pip install PyQt6 PyQt6-Charts pyqtgraph qasync
```

**Or install from requirements.txt:**
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('✅ PyQt6 installed successfully')"
```

---

## 🎬 First Launch

### Quick Start

```bash
# Launch the desktop GUI
python gui_app.py
```

**What you'll see:**
1. Main window opens showing the dashboard
2. System tray icon appears (green square)
3. All controls are ready to use

### Initial Setup

Before starting the bot, make sure:
- ✅ `.env` file is configured with Alpaca API keys
- ✅ Config validation passes (shown in logs)
- ✅ Internet connection is active

---

## 🖥️ Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ File    View    Help                              Status: ●     │
├─────────────────────────────────────────────────────────────────┤
│  [▶ Start Bot]  [⏹ Stop Bot]  [🚨 Emergency Stop]              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ Dashboard Tab ──────────────────────────────────────────┐  │
│  │                                                           │  │
│  │  Account Overview                                         │  │
│  │  ┌───────────────────────────────────────────────────┐   │  │
│  │  │ Balance:          $102,450.00                     │   │  │
│  │  │ Daily P&L:        +$2,450.00                      │   │  │
│  │  │ Buying Power:     $98,500.00                      │   │  │
│  │  │ Open Positions:   2                               │   │  │
│  │  └───────────────────────────────────────────────────┘   │  │
│  │                                                           │  │
│  │  Equity Curve                                             │  │
│  │  ┌───────────────────────────────────────────────────┐   │  │
│  │  │                                            ╱       │   │  │
│  │  │                                        ╱╲╱        │   │  │
│  │  │                                    ╱╲╱           │   │  │
│  │  │  $100k ────────────────────────╱╲╱              │   │  │
│  │  │        9:30   10:00   10:30   11:00   11:30      │   │  │
│  │  └───────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [📊 Dashboard] [📈 Positions] [📝 Logs]                       │
└─────────────────────────────────────────────────────────────────┘
```

### Tabs

#### 1️⃣ **Dashboard Tab** (📊)

**What it shows:**
- **Account Balance** - Current total equity
- **Daily P&L** - Today's profit/loss (green if positive, red if negative)
- **Buying Power** - Available cash for trading
- **Open Positions** - Number of active trades
- **Equity Curve Chart** - Real-time graph of account balance

**Updates:** Every 5 seconds

#### 2️⃣ **Positions Tab** (📈)

**What it shows:**
Table with all open positions:

| Symbol | Quantity | Entry Price | Current Price | P&L $ | P&L % |
|--------|----------|-------------|---------------|-------|-------|
| AAPL   | 50       | $178.50     | $180.20       | +$85  | +0.95%|
| SPY    | 15       | $580.00     | $581.50       | +$22  | +0.26%|

**Features:**
- Color-coded P&L (green = profit, red = loss)
- Sortable columns
- Auto-refresh every 5 seconds

#### 3️⃣ **Logs Tab** (📝)

**What it shows:**
- Real-time log messages
- Bot status changes
- Errors and warnings
- Order executions
- System events

**Features:**
- Auto-scroll to latest message
- Timestamps on all entries
- Clear button to reset logs

---

## ⭐ Features

### 1. **Start/Stop Controls**

#### ▶️ **Start Bot**
- Click to begin trading
- Bot runs in background thread
- Dashboard updates automatically
- System tray shows green icon

#### ⏹️ **Stop Bot**
- Click to halt trading
- Gracefully stops all operations
- Positions remain open
- System tray shows red icon

#### 🚨 **Emergency Stop**
- **USE WITH CAUTION**
- Immediately stops bot
- Cancels ALL pending orders
- Closes ALL open positions
- Requires confirmation dialog

**When to use Emergency Stop:**
- Market crashes
- Bot malfunction detected
- Need to exit all positions immediately
- Testing/debugging

### 2. **Real-Time Updates**

**What updates automatically:**
- Account balance (every 5 seconds)
- Position values
- P&L calculations
- Chart data
- Log messages

**How it works:**
- Background thread polls Alpaca API
- Qt signals update UI
- No UI freezing or lag

### 3. **Desktop Notifications**

**You get notified when:**
- ✅ Bot starts successfully
- ⏹️ Bot stops
- 🚨 Emergency stop activated
- ❌ Errors occur
- 📊 Important events

**Notification types:**
- System tray pop-ups
- Sound alerts (optional)
- Visual indicators

### 4. **Live Charts**

**Equity Curve:**
- Shows account balance over time
- Auto-scales Y-axis
- Time-based X-axis
- Smooth animations
- Keeps last 100 data points

**Future charts (coming soon):**
- P&L by strategy
- Win rate over time
- Trade frequency

---

## ⌨️ Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Open Settings |
| `Ctrl+Q` | Quit Application |
| `Ctrl+R` | Refresh Data |
| `F5` | Refresh Data |

### Window Management

| Shortcut | Action |
|----------|--------|
| `Alt+1` | Switch to Dashboard Tab |
| `Alt+2` | Switch to Positions Tab |
| `Alt+3` | Switch to Logs Tab |

### Quick Actions

| Shortcut | Action |
|----------|--------|
| `Space` | Start/Stop Bot (toggle) |
| `Esc` | Minimize to Tray |

---

## 🎯 System Tray

### Tray Icon

**What it shows:**
- 🟢 **Green** = Bot running
- 🔴 **Red** = Bot stopped
- 🟡 **Yellow** = Bot starting/error

### Tray Menu

**Right-click the tray icon:**

```
┌──────────────────────┐
│ Show Window          │
├──────────────────────┤
│ Start Bot            │
│ Stop Bot             │
├──────────────────────┤
│ Quit                 │
└──────────────────────┘
```

**Double-click** tray icon = Show main window

### Minimize to Tray

**Options:**
1. Close window button → Minimizes to tray
2. Tray stays active even when window closed
3. Bot continues running in background

**To fully exit:**
- Right-click tray → Quit
- File → Exit (Ctrl+Q)

---

## 🛠️ Settings

### Access Settings

**Method 1:** Menu Bar → File → Settings (Ctrl+S)
**Method 2:** Right-click dashboard → Settings

### Available Settings

#### Risk Management

- **Max Position Size** - Percentage of account per trade
  - Range: 1% - 100%
  - Default: 10%
  - Recommended: 5-15%

- **Max Daily Loss** - Stop trading at this loss percentage
  - Range: 1% - 10%
  - Default: 2%
  - Recommended: 2-5%

#### Strategy Selection

- Mean Reversion
- Momentum Breakout
- Hybrid (Adaptive)

#### Display Options

- Refresh interval (1-60 seconds)
- Chart data points (50-500)
- Font size
- Theme (light/dark)

---

## 🔧 Troubleshooting

### Issue 1: GUI Won't Launch

**Error:**
```
ModuleNotFoundError: No module named 'PyQt6'
```

**Solution:**
```bash
pip install PyQt6 PyQt6-Charts
```

---

### Issue 2: Connection Error

**Error:**
```
ERROR: Failed to connect to Alpaca API
```

**Solution:**
1. Check `.env` file has correct API keys
2. Verify internet connection
3. Test API with: `python examples/example_2_api_connection.py`

---

### Issue 3: Blank Dashboard

**Symptom:** Dashboard shows $0.00 for everything

**Solution:**
1. Click "▶ Start Bot"
2. Wait 5-10 seconds for first update
3. Check logs tab for errors

---

### Issue 4: Tray Icon Not Showing

**Windows:** Check system tray overflow area
**macOS:** Check menu bar extras
**Linux:** Ensure tray support enabled in DE

---

### Issue 5: Chart Not Updating

**Solution:**
1. Check bot is running (status = green)
2. Verify market is open
3. Click "Refresh" (F5)
4. Restart application

---

## 💡 Tips & Best Practices

### 1. **Monitor Regularly**
- Check GUI at market open
- Review positions hourly
- Watch for error messages in logs

### 2. **Use Emergency Stop Wisely**
- Only for true emergencies
- Closes ALL positions immediately
- May result in slippage/bad fills

### 3. **Let It Run**
- Bot performs best when left alone
- Minimize window to tray
- Check periodically, don't micromanage

### 4. **Settings Changes**
- Stop bot before changing settings
- Test new settings on paper trading first
- Document what works for you

### 5. **Backup**
- Export performance reports regularly
- Screenshot winning trades
- Keep logs for analysis

---

## 📊 Performance Monitoring

### What to Watch

**Green Flags** (✅):
- Steady equity curve upward
- Win rate >55%
- P&L positive most days
- Low error count in logs

**Yellow Flags** (⚠️):
- Win rate 45-55%
- Choppy equity curve
- Occasional errors
- Slippage increasing

**Red Flags** (🚨):
- Win rate <45%
- Declining equity curve
- Frequent errors
- Bot keeps stopping

### Taking Action

**If green:**
- Keep running
- Consider increasing position sizes (gradually)
- Document successful parameters

**If yellow:**
- Review strategy settings
- Check market conditions
- Reduce position sizes
- Monitor more closely

**If red:**
- STOP THE BOT
- Review all logs
- Check for bugs
- Test in paper trading
- Adjust strategy

---

## 🎓 Advanced Features

### Multi-Instance Running

**Can you run multiple bots?**
- ✅ Yes, but not recommended
- Each instance needs separate API keys
- Risk of conflicting orders

**Better approach:**
- Run one GUI instance
- Use multi-strategy mode
- Let regime detection switch strategies

### Remote Access

**Can you access GUI remotely?**
- ❌ No, desktop GUI is local only
- Consider: VNC/RDP for remote desktop
- Alternative: Build web dashboard (Flask)

### Data Export

**Coming soon:**
- Export trades to CSV
- Generate PDF reports
- Save charts as images

---

## 🆘 Support

### Getting Help

1. **Check documentation:**
   - README.md
   - GETTING_STARTED.md
   - BUG_REPORT.md

2. **Review logs:**
   - Logs tab in GUI
   - `trading_bot.log` file

3. **Test components:**
   - Run `python examples/example_1_strategy_test.py`
   - Run `python examples/example_2_api_connection.py`

4. **Report issues:**
   - Include error messages
   - Attach log files
   - Describe steps to reproduce

---

## 📝 Version History

### Version 1.0.0 (Current)
- ✅ Initial release
- ✅ Dashboard with metrics
- ✅ Real-time charts
- ✅ Positions table
- ✅ Log viewer
- ✅ System tray integration
- ✅ Desktop notifications
- ✅ Keyboard shortcuts
- ✅ Settings dialog
- ✅ Emergency stop

### Planned Features (v1.1.0)
- Order history tab
- Strategy comparison charts
- Dark theme
- Sound alerts
- Trade journal
- Performance analytics
- Backtesting integration
- Mobile companion app

---

## 🎉 Quick Start Checklist

- [ ] Install PyQt6 dependencies
- [ ] Configure .env file with API keys
- [ ] Launch GUI: `python gui_app.py`
- [ ] Verify connection in logs
- [ ] Click "▶ Start Bot"
- [ ] Monitor dashboard
- [ ] Check system tray icon
- [ ] Test Emergency Stop (optional)
- [ ] Minimize to tray
- [ ] Let it run!

---

**🎯 You're ready to trade with a professional desktop interface!**

For more information, see:
- `SYSTEM_OVERVIEW.md` - Complete system documentation
- `GETTING_STARTED.md` - Setup and configuration guide
- `BUG_REPORT.md` - Known issues and fixes
