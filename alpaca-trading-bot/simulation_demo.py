"""
TRADING BOT SIMULATION: $100 PAPER TRADING WALKTHROUGH
Shows every layer in action, step-by-step

Starting Capital: $100.00
Stock: FORD (F) @ ~$10/share (affordable with $100)
"""
import sys
from datetime import datetime, timedelta
import numpy as np

# Add project to path
sys.path.insert(0, '/home/user/portfolio/alpaca-trading-bot')

from data_cache import MarketDataCache
from strategy import MeanReversionStrategy
from config import Config

print("=" * 80)
print("ALPACA TRADING BOT - COMPLETE $100 WALKTHROUGH")
print("Starting Capital: $100.00 (Paper Trading)")
print("=" * 80)
print()

# Set seed for reproducibility
np.random.seed(42)

# ============================================================================
# LAYER 1: CONFIGURATION
# ============================================================================
print("🔧 LAYER 1: CONFIGURATION & INITIALIZATION")
print("-" * 80)

print("\n📋 Step 1.1: Loading Environment Variables")
print("  ├─ ALPACA_API_KEY: test_key_***************")
print("  ├─ ALPACA_SECRET_KEY: test_secret_********")
print("  ├─ ALPACA_BASE_URL: https://paper-api.alpaca.markets")
print("  └─ DATA_FEED: iex (free, 15-minute delay)")

print("\n⚠️  Step 1.2: Loading Risk Parameters")
print(f"  ├─ MAX_POSITION_PCT: {Config.MAX_POSITION_PCT} → $10.00 max per position")
print(f"  ├─ MAX_DAILY_LOSS_PCT: {Config.MAX_DAILY_LOSS_PCT} → $2.00 max daily loss")
print(f"  ├─ STOP_LOSS_PCT: {Config.STOP_LOSS_PCT} → 2% automatic stop")
print(f"  ├─ TAKE_PROFIT_PCT: {Config.TAKE_PROFIT_PCT} → 6% automatic profit")
print(f"  └─ WATCHLIST: {', '.join(Config.WATCHLIST[:3])}...")

print("\n💰 Step 1.3: Calculating Account Limits")
account_equity = 100.00
max_position_value = account_equity * Config.MAX_POSITION_PCT
max_daily_loss = account_equity * Config.MAX_DAILY_LOSS_PCT

print(f"  ├─ Account Equity: ${account_equity:.2f}")
print(f"  ├─ Max Position Size: ${max_position_value:.2f} (10%)")
print(f"  ├─ Max Daily Loss: ${max_daily_loss:.2f} (-2% circuit breaker)")
print(f"  └─ Buying Power: ${account_equity:.2f}")

print("\n✅ Configuration loaded\n")

# ============================================================================
# LAYER 2: MARKET DATA CACHE
# ============================================================================
print("📊 LAYER 2: MARKET DATA CACHE")
print("-" * 80)

print("\n🔌 Step 2.1: Initializing Cache")
cache = MarketDataCache(window_size=1000)
print("  ├─ Window Size: 1000 trades/symbol (deque)")
print("  ├─ Complexity: O(1) append, FIFO eviction")
print("  └─ Status: READY")

symbol = "F"  # Ford Motor - affordable at ~$10/share
base_price = 10.00

print(f"\n📡 Step 2.2: Streaming Live Data for {symbol} (Ford Motor)")
print("  WebSocket connected... receiving ticks:")

now = datetime.now()

# Build 20-trade history
for i in range(20):
    timestamp = now - timedelta(seconds=120-i*5)
    price = base_price + np.random.uniform(-0.10, 0.10)
    size = int(np.random.uniform(500, 2000))
    
    cache.add_trade(symbol, price, size, timestamp)
    
    if i in [0, 9, 19]:
        print(f"  ├─ Tick #{i+1:02d}: {symbol} @ ${price:6.2f} | Vol: {size:4d} | {timestamp.strftime('%H:%M:%S')}")

print(f"  └─ Cached: {len(cache.trades[symbol])} trades")

print("\n💱 Step 2.3: Current Market Quote")
cache.add_quote(symbol, 9.98, 10.02, 5000, 4000, now)
quote = cache.get_last_quote(symbol)

print(f"  ├─ Bid: ${quote['bid']:.2f} × {quote['bid_size']}")
print(f"  ├─ Ask: ${quote['ask']:.2f} × {quote['ask_size']}")
print(f"  ├─ Spread: ${quote['spread']:.2f}")

spread_bps = cache.get_spread_bps(symbol)
print(f"  └─ Spread: {spread_bps:.1f} bps {'✅' if spread_bps < 20 else '⚠️'}")

vwap = cache.get_vwap(symbol, 120)
print(f"\n📈 Step 2.4: VWAP = ${vwap:.2f}")
print("  Formula: Σ(price × volume) / Σ(volume)")

print("\n✅ Market data ready\n")

# ============================================================================
# LAYER 3: TRADING STRATEGY  
# ============================================================================
print("🧠 LAYER 3: TRADING STRATEGY")
print("-" * 80)

strategy = MeanReversionStrategy()
print(f"\n⚙️  Step 3.1: Strategy = {strategy.get_name()}")
print(f"  ├─ Lookback: 20 trades")
print(f"  ├─ Threshold: ±2σ (standard deviations)")
print(f"  └─ Max Spread: 20 bps")

print("\n📊 Step 3.2: Statistical Analysis")
recent_trades = list(cache.trades[symbol])[-20:]
prices = np.array([t['price'] for t in recent_trades])

mean_price = np.mean(prices)
std_price = np.std(prices)

print(f"  ├─ Mean: ${mean_price:.2f}")
print(f"  ├─ Std Dev: ${std_price:.2f}")
print(f"  ├─ Upper Band (+2σ): ${mean_price + 2*std_price:.2f}")
print(f"  └─ Lower Band (-2σ): ${mean_price - 2*std_price:.2f}")

print("\n🎯 Step 3.3: Creating OVERSOLD Condition")
oversold_price = mean_price - 2.3 * std_price
cache.add_trade(symbol, oversold_price, 1500, now)

current_price = cache.get_last_price(symbol)
z_score = (current_price - mean_price) / std_price

print(f"  ├─ NEW TICK: {symbol} @ ${current_price:.2f}")
print(f"  ├─ Z-Score: {z_score:.2f}σ")
print(f"  └─ Status: {'🔴 OVERSOLD' if z_score < -2 else '🟢 OVERBOUGHT' if z_score > 2 else '🟡 NORMAL'}")

print("\n🔍 Step 3.4: Generating Signal")
signal = strategy.evaluate(symbol, cache)

print(f"  ├─ Action: {signal['action']} {'✅' if signal['action'] != 'HOLD' else ''}")
print(f"  ├─ Confidence: {signal['confidence']:.1%}")
print(f"  ├─ Reason: {signal['reason']}")
print(f"  └─ Threshold: {'PASS ✅' if signal['confidence'] >= 0.7 else 'FAIL ❌'} (need ≥70%)")

print("\n✅ Signal generated\n")

# ============================================================================
# LAYER 4: POSITION SIZING
# ============================================================================
print("📐 LAYER 4: POSITION SIZING")
print("-" * 80)

entry_price = current_price
risk_per_trade = account_equity * 0.01

print(f"\n💵 Step 4.1: Risk Calculation")
print(f"  ├─ Entry Price: ${entry_price:.2f}")
print(f"  ├─ Account: ${account_equity:.2f}")
print(f"  └─ Risk/Trade: ${risk_per_trade:.2f} (1%)")

stop_loss_pct = Config.STOP_LOSS_PCT  
stop_loss_price = entry_price * (1 - stop_loss_pct)
stop_loss_distance = entry_price - stop_loss_price

print(f"\n🛑 Step 4.2: Stop Loss")
print(f"  ├─ Percentage: {stop_loss_pct:.0%}")
print(f"  ├─ Price: ${stop_loss_price:.2f}")
print(f"  └─ Distance: ${stop_loss_distance:.2f}/share")

shares_by_risk = int(risk_per_trade / stop_loss_distance)
max_shares = int(max_position_value / entry_price)
shares = min(shares_by_risk, max_shares, int(account_equity / entry_price))

position_value = shares * entry_price

print(f"\n🔢 Step 4.3: Share Calculation")
print(f"  ├─ By Risk: {shares_by_risk} shares (${risk_per_trade:.2f} / ${stop_loss_distance:.2f})")
print(f"  ├─ By Max Position: {max_shares} shares (${max_position_value:.2f} / ${entry_price:.2f})")  
print(f"  ├─ By Buying Power: {int(account_equity / entry_price)} shares")
print(f"  ├─ FINAL: {shares} shares")
print(f"  └─ Value: ${position_value:.2f} ({position_value/account_equity:.0%})")

print("\n✅ Position sized\n")

# ============================================================================
# LAYER 5: PRE-TRADE VALIDATION
# ============================================================================
print("✅ LAYER 5: PRE-TRADE VALIDATION")
print("-" * 80)

print("\n🔐 Step 5.1: Safety Checks")

checks = []

# Check 1: Market hours
market_open = True
checks.append(market_open)
print(f"  [1/5] Market Hours: {'✅ OPEN' if market_open else '❌ CLOSED'}")

# Check 2: Position size
position_ok = position_value <= max_position_value  
checks.append(position_ok)
print(f"  [2/5] Position Size: ${position_value:.2f} ≤ ${max_position_value:.2f} {'✅' if position_ok else '❌'}")

# Check 3: Daily loss
daily_pnl = 0.00
loss_ok = daily_pnl > -max_daily_loss
checks.append(loss_ok)
print(f"  [3/5] Daily P&L: ${daily_pnl:.2f} > -${max_daily_loss:.2f} {'✅' if loss_ok else '❌'}")

# Check 4: Buying power
bp_ok = position_value <= account_equity
checks.append(bp_ok)
print(f"  [4/5] Buying Power: ${position_value:.2f} ≤ ${account_equity:.2f} {'✅' if bp_ok else '❌'}")

# Check 5: Quantity
qty_ok = shares > 0
checks.append(qty_ok)
print(f"  [5/5] Quantity: {shares} > 0 {'✅' if qty_ok else '❌'}")

all_passed = all(checks)
print(f"\n{'✅ ALL CHECKS PASSED' if all_passed else '❌ VALIDATION FAILED'}")
print()

if not all_passed:
    print("⚠️  Order REJECTED - Cannot proceed to execution\n")
    sys.exit(0)

# ============================================================================
# LAYER 6: ORDER EXECUTION
# ============================================================================
print("📤 LAYER 6: ORDER EXECUTION")
print("-" * 80)

print("\n💱 Step 6.1: Limit Price Calculation")
bid = quote['bid']
ask = quote['ask']
spread = ask - bid
aggression = 0.3

limit_price = bid + spread * aggression

print(f"  ├─ Bid: ${bid:.2f}")
print(f"  ├─ Ask: ${ask:.2f}")
print(f"  ├─ Spread: ${spread:.2f}")
print(f"  ├─ Aggression: {aggression:.0%}")
print(f"  └─ Limit: ${limit_price:.2f}")

print("\n📋 Step 6.2: Bracket Order Creation")

sl_level = entry_price * (1 - Config.STOP_LOSS_PCT)
tp_level = entry_price * (1 + Config.TAKE_PROFIT_PCT)

risk_per_share = entry_price - sl_level
reward_per_share = tp_level - entry_price
rr_ratio = reward_per_share / risk_per_share

print(f"\n  Entry:")
print(f"    ├─ Side: BUY")
print(f"    ├─ Qty: {shares} shares")
print(f"    ├─ Type: LIMIT")
print(f"    └─ Price: ${limit_price:.2f}")

print(f"\n  Stop Loss (Auto):")
print(f"    ├─ Trigger: ${sl_level:.2f}")
print(f"    └─ Max Loss: ${risk_per_share * shares:.2f}")

print(f"\n  Take Profit (Auto):")
print(f"    ├─ Trigger: ${tp_level:.2f}")
print(f"    └─ Max Gain: ${reward_per_share * shares:.2f}")

print(f"\n  Risk/Reward: {rr_ratio:.1f}:1 ✅")

print("\n📡 Step 6.3: Submitting to Broker")
order_id = f"ORD{int(now.timestamp())}"
print(f"  ├─ Order ID: {order_id}")
print(f"  ├─ Status: PENDING...")
print(f"  └─ Submitted: {now.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n⏱️  Step 6.4: Fill Simulation (30 seconds)")
fill_price = limit_price
fill_time = now + timedelta(seconds=30)

print(f"  ├─ Status: FILLED ✅")
print(f"  ├─ Price: ${fill_price:.2f}")
print(f"  ├─ Time: {fill_time.strftime('%H:%M:%S')}")
print(f"  ├─ Filled: {shares}/{shares}")
print(f"  └─ Cost: ${fill_price * shares:.2f}")

cash_remaining = account_equity - (fill_price * shares)
position_value_current = shares * fill_price

print("\n✅ Order executed\n")

# ============================================================================
# LAYER 7: POSITION MANAGEMENT
# ============================================================================
print("📊 LAYER 7: POSITION MANAGEMENT")
print("-" * 80)

print(f"\n🎯 Step 7.1: Position Update")
print(f"  ├─ Symbol: {symbol}")
print(f"  ├─ Side: LONG")
print(f"  ├─ Qty: {shares} shares")
print(f"  ├─ Entry: ${fill_price:.2f}")
print(f"  ├─ Value: ${position_value_current:.2f}")
print(f"  └─ P&L: $0.00 (just entered)")

print(f"\n💰 Step 7.2: Account Update")
print(f"  ├─ Cash: ${cash_remaining:.2f}")
print(f"  ├─ Position: ${position_value_current:.2f}")
print(f"  ├─ Total: ${cash_remaining + position_value_current:.2f}")
print(f"  └─ Daily P&L: $0.00")

print(f"\n🛡️  Step 7.3: Protection Orders Active")
print(f"  Stop Loss:")
print(f"    Sell {shares} @ ${sl_level:.2f} (max loss: ${risk_per_share * shares:.2f})")
print(f"  Take Profit:")
print(f"    Sell {shares} @ ${tp_level:.2f} (max gain: ${reward_per_share * shares:.2f})")

print("\n✅ Position active\n")

# ============================================================================
# LAYER 8: MONITORING & SCENARIOS
# ============================================================================
print("👁️  LAYER 8: REAL-TIME MONITORING")
print("-" * 80)

print("\n🔄 Step 8.1: Active Monitoring")
print("  ├─ Price updates (WebSocket)")
print("  ├─ Position reconciliation (60s)")
print("  ├─ P&L calculation (5min)")
print("  └─ Circuit breaker check (5min)")

print("\n📈 Step 8.2: SCENARIO 1 - Price Rises (+6%)")
tp_price = tp_level
profit = (tp_price - fill_price) * shares
new_equity_win = account_equity + profit

print(f"  ├─ {symbol} → ${tp_price:.2f}")
print(f"  ├─ Take Profit TRIGGERS")
print(f"  ├─ Sell @ ${tp_price:.2f}")
print(f"  ├─ Profit: +${profit:.2f} (+{(profit/account_equity)*100:.1f}%)")
print(f"  └─ New Equity: ${new_equity_win:.2f}")

print("\n📉 Step 8.3: SCENARIO 2 - Price Falls (-2%)")
sl_price = sl_level
loss = (fill_price - sl_price) * shares
new_equity_loss = account_equity - loss

print(f"  ├─ {symbol} → ${sl_price:.2f}")
print(f"  ├─ Stop Loss TRIGGERS")
print(f"  ├─ Sell @ ${sl_price:.2f}")
print(f"  ├─ Loss: -${loss:.2f} (-{(loss/account_equity)*100:.1f}%)")
print(f"  └─ New Equity: ${new_equity_loss:.2f}")

print("\n🔴 Step 8.4: SCENARIO 3 - Daily Loss Limit")
print(f"  ├─ Threshold: -${max_daily_loss:.2f} (-2%)")
print(f"  ├─ If Hit: 🚨 CIRCUIT BREAKER")
print(f"  ├─ Action: Cancel all orders")
print(f"  ├─ Action: Close all positions")
print(f"  └─ Action: Halt trading")

print("\n✅ All scenarios handled\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("SIMULATION COMPLETE - DETAILED SUMMARY")
print("=" * 80)

print(f"\n💰 STARTING: ${account_equity:.2f}")

print(f"\n📊 TRADE EXECUTED:")
print(f"  Symbol: {symbol} (Ford Motor)")
print(f"  Action: BUY {shares} shares @ ${fill_price:.2f}")
print(f"  Cost: ${shares * fill_price:.2f} ({(shares * fill_price / account_equity)*100:.0%} of account)")

print(f"\n🛡️  RISK MANAGEMENT:")
print(f"  Stop Loss: ${sl_level:.2f} (Max loss: ${risk_per_share * shares:.2f})")
print(f"  Take Profit: ${tp_level:.2f} (Max gain: ${reward_per_share * shares:.2f})")
print(f"  Risk/Reward: {rr_ratio:.1f}:1")

print(f"\n📈 POSSIBLE OUTCOMES:")
print(f"  Win (+6%): ${new_equity_win:.2f} (+{((new_equity_win - account_equity)/account_equity)*100:.1f}%)")
print(f"  Loss (-2%): ${new_equity_loss:.2f} (-{((account_equity - new_equity_loss)/account_equity)*100:.1f}%)")
print(f"  Expected Value: ${account_equity + (0.6 * profit - 0.4 * loss):.2f} (60% win rate)")

print(f"\n✅ ALL 8 LAYERS DEMONSTRATED:")
print("  [1] Configuration      ✅")
print("  [2] Market Data Cache  ✅")
print("  [3] Trading Strategy   ✅")
print("  [4] Position Sizing    ✅")
print("  [5] Risk Validation    ✅")
print("  [6] Order Execution    ✅")
print("  [7] Position Management✅")
print("  [8] Monitoring         ✅")

print("\n" + "=" * 80)
print("BOT READY FOR LIVE PAPER TRADING")
print("=" * 80)
