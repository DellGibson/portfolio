"""
Main trading loop - orchestrates data, strategy, and execution.

Architecture:
- Async event-driven model (handles 100+ ticks/second)
- WebSocket for real-time market data
- Periodic tasks for monitoring and reconciliation
- Graceful shutdown with position preservation

Flow:
1. Startup: Initialize components, sync state
2. Data streaming: Handle ticks, generate signals
3. Execution: Submit orders via OrderManager
4. Monitoring: Track P&L, positions, health
5. Shutdown: Clean up, save state
"""
import asyncio
import signal
import sys
from datetime import datetime, time as dt_time
from typing import Dict, Optional
import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream

from config import Config
from data_cache import MarketDataCache
from order_manager import OrderManager
from strategy import HybridStrategy, MeanReversionStrategy, MomentumBreakoutStrategy
from utils import log_info, log_error, log_warning, send_alert, format_currency


class TradingBot:
    """
    Main trading bot orchestrator.

    Responsibilities:
    - Manage WebSocket connections
    - Route market data to cache
    - Generate trading signals
    - Execute orders with risk checks
    - Monitor health and performance
    """

    def __init__(self):
        # API connection
        self.api = tradeapi.REST(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY,
            Config.ALPACA_BASE_URL
        )

        # Core components
        self.cache = MarketDataCache(window_size=1000)
        self.order_manager = OrderManager(self.api)

        # Strategy selection (can switch to MeanReversionStrategy or MomentumBreakoutStrategy)
        self.strategy = HybridStrategy(self.api)

        # WebSocket stream
        self.stream = Stream(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY,
            base_url=Config.ALPACA_BASE_URL,
            data_feed=Config.DATA_FEED
        )

        # State tracking
        self.running = False
        self.last_tick_time = datetime.now()
        self.ticks_processed = 0
        self.signals_evaluated = 0
        self.orders_submitted = 0

        # Shutdown flag
        self.shutdown_requested = False

    async def startup(self):
        """
        Phase 1: Initialization sequence

        Steps:
        1. Validate API credentials
        2. Check account status
        3. Sync positions
        4. Set start-of-day equity
        5. Send startup alert
        """
        log_info("=" * 60)
        log_info("TRADING BOT STARTUP")
        log_info("=" * 60)

        try:
            # Validate API access
            account = self.api.get_account()
            log_info(f"Account: {account.account_number}")
            log_info(f"Equity: {format_currency(float(account.equity))}")
            log_info(f"Buying Power: {format_currency(float(account.buying_power))}")

            # Check account status
            if account.trading_blocked:
                raise ValueError("Account is blocked from trading!")

            if account.pattern_day_trader and float(account.equity) < 25000:
                log_warning("Pattern Day Trader with <$25k equity - limited to 3 day trades/5 days")

            # Set start-of-day equity for P&L tracking
            self.order_manager.start_of_day_equity = float(account.equity)

            # Sync positions from broker
            self.order_manager._sync_positions()

            # Send startup alert
            send_alert(
                f"Trading bot started\n"
                f"Strategy: {self.strategy.get_name()}\n"
                f"Equity: {format_currency(float(account.equity))}\n"
                f"Positions: {len(self.order_manager.positions)}",
                priority='low'
            )

            log_info(f"Strategy: {self.strategy.get_name()}")
            log_info(f"Watchlist: {', '.join(Config.WATCHLIST)}")
            log_info("Startup complete")

            return True

        except Exception as e:
            log_error(f"Startup failed: {e}")
            send_alert(f"Startup failed: {e}", priority='critical')
            return False

    def is_market_hours(self) -> bool:
        """
        Check if currently in market hours.

        Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        """
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            log_error(f"Failed to check market hours: {e}")
            return False

    async def wait_for_market_open(self):
        """
        Phase 2: Wait for market to open

        Checks every 60 seconds until market opens
        """
        while not self.is_market_hours():
            try:
                clock = self.api.get_clock()
                next_open = clock.next_open.timestamp()
                next_close = clock.next_close.timestamp()
                current = clock.timestamp.timestamp()

                time_to_open = (next_open - current) / 60  # minutes

                log_info(f"Market closed. Opens in {time_to_open:.0f} minutes")

                # Sleep for 60 seconds
                await asyncio.sleep(60)

            except Exception as e:
                log_error(f"Error checking market status: {e}")
                await asyncio.sleep(60)

        log_info("Market is OPEN - starting trading")
        send_alert("Market opened - bot is active", priority='low')

    async def handle_trade(self, data):
        """
        Event handler: Incoming trade tick

        Steps:
        1. Update cache with trade data
        2. Evaluate strategy for signal
        3. Execute order if signal is strong
        4. Update metrics
        """
        try:
            symbol = data.symbol
            price = float(data.price)
            size = int(data.size)
            timestamp = data.timestamp

            # Update cache
            self.cache.add_trade(symbol, price, size, timestamp)

            # Update metrics
            self.ticks_processed += 1
            self.last_tick_time = datetime.now()

            # Evaluate strategy
            signal = self.strategy.evaluate(symbol, self.cache, self.cache)
            self.signals_evaluated += 1

            # Act on signal
            if signal['action'] in ['BUY', 'SELL']:
                await self.handle_signal(signal, price)

        except Exception as e:
            log_error(f"Error handling trade for {data.symbol}: {e}")

    async def handle_quote(self, data):
        """
        Event handler: Incoming quote tick

        Updates bid/ask spread data in cache
        """
        try:
            symbol = data.symbol
            bid = float(data.bid_price)
            ask = float(data.ask_price)
            bid_size = int(data.bid_size)
            ask_size = int(data.ask_size)
            timestamp = data.timestamp

            # Update cache
            self.cache.add_quote(symbol, bid, ask, bid_size, ask_size, timestamp)

            # Check for wide spreads (liquidity warning)
            quote = self.cache.get_last_quote(symbol)
            if quote and quote['bid'] > 0:
                spread_pct = (quote['spread'] / quote['bid']) * 100
                if spread_pct > 0.5:  # 0.5% spread
                    log_warning(f"{symbol} wide spread: {spread_pct:.2f}%")

        except Exception as e:
            log_error(f"Error handling quote for {data.symbol}: {e}")

    async def handle_signal(self, signal: Dict, current_price: float):
        """
        Process trading signal and execute order.

        Args:
            signal: Signal dictionary from strategy
            current_price: Current market price
        """
        try:
            symbol = signal['symbol']
            action = signal['action']
            confidence = signal['confidence']
            reason = signal['reason']

            # Check confidence threshold
            if confidence < 0.7:
                log_info(f"Signal ignored (low confidence {confidence:.2f}): {symbol} {action} - {reason}")
                return

            # Check if we already have a position
            current_position = self.order_manager.get_position(symbol)

            if action == 'BUY' and current_position > 0:
                log_info(f"BUY signal ignored - already long {current_position} shares of {symbol}")
                return

            if action == 'SELL' and current_position <= 0:
                log_info(f"SELL signal ignored - no position in {symbol}")
                return

            # Calculate position size
            account_equity = self.order_manager.get_account_equity()
            quantity = self.strategy.get_position_size(symbol, current_price, account_equity, self.cache)

            if quantity == 0:
                log_warning(f"Position size calculated as 0 for {symbol}")
                return

            # Submit order
            log_info(f"SIGNAL: {action} {quantity} {symbol} @ ${current_price:.2f} (confidence: {confidence:.2f})")
            log_info(f"Reason: {reason}")

            if action == 'BUY':
                order = self.order_manager.submit_bracket_order(
                    symbol=symbol,
                    qty=quantity,
                    side='buy',
                    entry_price=current_price
                )
            else:  # SELL
                # Close existing position
                order = self.order_manager.submit_order(
                    symbol=symbol,
                    qty=current_position,
                    side='sell',
                    order_type='limit'
                )

            if order:
                self.orders_submitted += 1
                log_info(f"Order submitted successfully: {order.id}")
            else:
                log_error(f"Order submission failed for {symbol}")

        except Exception as e:
            log_error(f"Error handling signal: {e}")

    async def periodic_position_sync(self):
        """
        Periodic task: Sync positions every 60 seconds

        Ensures local cache matches broker state
        """
        while self.running:
            try:
                await asyncio.sleep(60)  # Every 1 minute

                log_info("Running position sync...")
                self.order_manager._sync_positions()

                # Log current positions
                if self.order_manager.positions:
                    log_info(f"Current positions: {self.order_manager.positions}")

            except Exception as e:
                log_error(f"Position sync failed: {e}")

    async def periodic_pnl_update(self):
        """
        Periodic task: Update P&L every 5 minutes

        Checks daily loss limit and triggers circuit breaker if needed
        """
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                pnl = self.order_manager.update_daily_pnl()
                equity = self.order_manager.get_account_equity()

                log_info(f"Daily P&L: {format_currency(pnl)} ({(pnl/self.order_manager.start_of_day_equity)*100:.2f}%)")

                # Check daily loss limit
                loss_limit = -equity * Config.MAX_DAILY_LOSS_PCT

                if pnl < loss_limit:
                    log_error(f"CIRCUIT BREAKER: Daily loss limit hit ({format_currency(pnl)})")
                    send_alert(
                        f"CIRCUIT BREAKER TRIGGERED\n"
                        f"Daily P&L: {format_currency(pnl)}\n"
                        f"Limit: {format_currency(loss_limit)}\n"
                        f"Closing all positions...",
                        priority='critical'
                    )

                    # Emergency shutdown
                    await self.emergency_shutdown()

            except Exception as e:
                log_error(f"P&L update failed: {e}")

    async def periodic_health_check(self):
        """
        Periodic task: Health check every 2 minutes

        Monitors:
        - Data stream connectivity
        - API responsiveness
        - System metrics
        """
        while self.running:
            try:
                await asyncio.sleep(120)  # Every 2 minutes

                # Check data freshness
                time_since_tick = (datetime.now() - self.last_tick_time).total_seconds()

                if time_since_tick > 30:
                    log_warning(f"No data received for {time_since_tick:.0f} seconds - connection may be stale")

                # Log statistics
                stats = self.order_manager.get_stats()
                log_info(f"Health: Ticks={self.ticks_processed}, Signals={self.signals_evaluated}, "
                        f"Orders={self.orders_submitted}, Positions={stats['num_positions']}")

            except Exception as e:
                log_error(f"Health check failed: {e}")

    async def emergency_shutdown(self):
        """
        Emergency shutdown triggered by circuit breaker

        Actions:
        1. Cancel all pending orders
        2. Close all positions
        3. Stop trading
        """
        log_error("EMERGENCY SHUTDOWN INITIATED")

        try:
            # Cancel all orders
            self.order_manager.cancel_all_orders()

            # Close all positions
            self.order_manager.close_all_positions()

            # Stop bot
            self.shutdown_requested = True
            self.running = False

        except Exception as e:
            log_error(f"Emergency shutdown error: {e}")
            send_alert(f"Emergency shutdown error: {e}", priority='critical')

    async def graceful_shutdown(self):
        """
        Normal shutdown at market close or user request

        Actions:
        1. Stop accepting new signals
        2. Cancel pending orders
        3. Optionally close positions (based on strategy)
        4. Save state
        5. Send summary report
        """
        log_info("Graceful shutdown initiated...")

        try:
            # Stop processing
            self.running = False

            # Cancel pending orders
            self.order_manager.cancel_all_orders()

            # Generate daily summary
            pnl = self.order_manager.daily_pnl
            stats = self.order_manager.get_stats()

            summary = (
                f"DAILY SUMMARY\n"
                f"P&L: {format_currency(pnl)}\n"
                f"Ticks processed: {self.ticks_processed}\n"
                f"Signals evaluated: {self.signals_evaluated}\n"
                f"Orders submitted: {self.orders_submitted}\n"
                f"Open positions: {stats['num_positions']}\n"
                f"Final equity: {format_currency(stats['account_equity'])}"
            )

            log_info(summary)
            send_alert(summary, priority='medium')

        except Exception as e:
            log_error(f"Graceful shutdown error: {e}")

    async def run(self):
        """
        Main run loop

        Flow:
        1. Startup
        2. Wait for market open
        3. Subscribe to data streams
        4. Start periodic tasks
        5. Run until shutdown
        """
        # Phase 1: Startup
        if not await self.startup():
            log_error("Startup failed - exiting")
            return

        # Phase 2: Wait for market
        await self.wait_for_market_open()

        # Phase 3: Start trading
        self.running = True

        # Subscribe to data streams
        for symbol in Config.WATCHLIST:
            self.stream.subscribe_trades(self.handle_trade, symbol)
            self.stream.subscribe_quotes(self.handle_quote, symbol)

        log_info(f"Subscribed to {len(Config.WATCHLIST)} symbols")

        # Start periodic tasks
        tasks = [
            asyncio.create_task(self.periodic_position_sync()),
            asyncio.create_task(self.periodic_pnl_update()),
            asyncio.create_task(self.periodic_health_check()),
            asyncio.create_task(self.stream._run_forever())  # WebSocket connection
        ]

        log_info("Trading bot is RUNNING")

        # Run until shutdown requested
        try:
            while self.running and not self.shutdown_requested:
                # Check if market closed
                if not self.is_market_hours():
                    log_info("Market closed - initiating shutdown")
                    break

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            log_info("Keyboard interrupt received")

        finally:
            # Graceful shutdown
            await self.graceful_shutdown()

            # Cancel all tasks
            for task in tasks:
                task.cancel()

            log_info("Trading bot stopped")


async def main():
    """
    Entry point for trading bot

    Handles:
    - Signal handlers for graceful shutdown
    - Bot initialization and execution
    """
    bot = TradingBot()

    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        log_info(f"Signal {sig} received - requesting shutdown")
        bot.shutdown_requested = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run bot
    try:
        await bot.run()
    except Exception as e:
        log_error(f"Fatal error: {e}")
        send_alert(f"Fatal error: {e}", priority='critical')
        sys.exit(1)


if __name__ == "__main__":
    # Run async main loop
    asyncio.run(main())
