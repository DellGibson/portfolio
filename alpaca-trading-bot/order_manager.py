"""
Order execution with pre-trade risk checks and position tracking.
Why: Raw API calls = disaster. Need validation layer to prevent account blowup.
Edge cases handled:
- Insufficient buying power
- Position size limits exceeded
- Daily loss limits hit
- Market closed
- Duplicate orders
"""
import alpaca_trade_api as tradeapi
from datetime import datetime
from typing import Optional, Dict
from config import Config
from utils import log_info, log_error, send_alert

class OrderManager:
    def __init__(self, api: tradeapi.REST):
        self.api = api
        self.positions: Dict[str, int] = {}  # symbol -> quantity (positive=long, negative=short)
        self.daily_pnl = 0.0
        self.start_of_day_equity = 0.0
        self.order_history = []

        # Load current positions from broker
        self._sync_positions()

    def _sync_positions(self):
        """
        Sync local position cache with broker state.
        Why: API can fail, need single source of truth.
        """
        try:
            broker_positions = self.api.list_positions()
            self.positions = {
                p.symbol: int(p.qty)
                for p in broker_positions
            }
            log_info(f"Synced {len(self.positions)} positions from broker")
        except Exception as e:
            log_error(f"Failed to sync positions: {e}")
            send_alert(f"Position sync failed: {e}", priority='high')

    def get_account_equity(self) -> float:
        """Get current account value"""
        try:
            account = self.api.get_account()
            return float(account.equity)
        except Exception as e:
            log_error(f"Failed to get account equity: {e}")
            return 0.0

    def get_buying_power(self) -> float:
        """Get available buying power"""
        try:
            account = self.api.get_account()
            return float(account.buying_power)
        except Exception as e:
            log_error(f"Failed to get buying power: {e}")
            return 0.0

    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            log_error(f"Failed to check market status: {e}")
            return False

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get latest trade price from API"""
        try:
            quote = self.api.get_latest_quote(symbol)
            return float(quote.ap)  # Ask price for buying
        except Exception as e:
            log_error(f"Failed to get price for {symbol}: {e}")
            return None

    def validate_order(self, symbol: str, qty: int, side: str, price: Optional[float] = None) -> bool:
        """
        Pre-flight risk checks before order submission.
        Returns: True if order passes all checks, raises ValueError otherwise.
        """
        # Get current price if not provided
        if price is None:
            price = self.get_current_price(symbol)
            if price is None:
                raise ValueError(f"Cannot get current price for {symbol}")

        equity = self.get_account_equity()
        buying_power = self.get_buying_power()

        # Check 1: Market hours
        if not self.is_market_open():
            raise ValueError("Market is closed - cannot place orders")

        # Check 2: Position size limit (% of portfolio)
        position_value = qty * price
        max_position_value = equity * Config.MAX_POSITION_PCT

        if position_value > max_position_value:
            raise ValueError(
                f"Position size ${position_value:.2f} exceeds "
                f"{Config.MAX_POSITION_PCT*100}% limit (${max_position_value:.2f})"
            )

        # Check 3: Daily loss limit
        if self.daily_pnl < -equity * Config.MAX_DAILY_LOSS_PCT:
            raise ValueError(
                f"Daily loss limit hit: ${self.daily_pnl:.2f} "
                f"({Config.MAX_DAILY_LOSS_PCT*100}% of account)"
            )

        # Check 4: Buying power
        if buying_power < position_value:
            raise ValueError(
                f"Insufficient buying power: ${buying_power:.2f} "
                f"< ${position_value:.2f} required"
            )

        # Check 5: Quantity must be positive
        if qty <= 0:
            raise ValueError(f"Invalid quantity: {qty}")

        return True

    def calculate_limit_price(self, symbol: str, side: str, aggression: float = 0.3) -> float:
        """
        Calculate smart limit price to balance fill probability vs execution quality.
        Args:
            aggression: 0.0 = post at bid/ask (patient), 1.0 = cross spread (urgent)
        Why: Market orders = slippage. Limit orders = control but risk no fill.
        """
        try:
            quote = self.api.get_latest_quote(symbol)
            bid = float(quote.bp)
            ask = float(quote.ap)
            spread = ask - bid

            if side == 'buy':
                # Start at bid, move toward ask based on aggression
                return bid + spread * aggression
            else:  # sell
                return ask - spread * aggression

        except Exception as e:
            log_error(f"Failed to calculate limit price for {symbol}: {e}")
            # Fallback to market order behavior
            return None

    def submit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = 'limit',
        time_in_force: str = 'day'
    ) -> Optional[object]:
        """
        Submit order with validation and error handling.
        Returns: Order object if successful, None if failed.
        """
        try:
            # Pre-trade validation
            current_price = self.get_current_price(symbol)
            self.validate_order(symbol, qty, side, current_price)

            # Calculate limit price if using limit order
            limit_price = None
            if order_type == 'limit':
                limit_price = self.calculate_limit_price(symbol, side)
                if limit_price is None:
                    log_error(f"Could not calculate limit price, falling back to market order")
                    order_type = 'market'

            # Submit order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                client_order_id=f"{symbol}_{side}_{int(datetime.now().timestamp())}"
            )

            # Log and track
            self.order_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': order_type,
                'limit_price': limit_price,
                'order_id': order.id
            })

            log_info(
                f"Order submitted: {side} {qty} {symbol} @ "
                f"${limit_price:.2f}" if limit_price else "market"
            )

            send_alert(
                f"Order: {side} {qty} {symbol} @ ${current_price:.2f}",
                priority='low'
            )

            return order

        except ValueError as e:
            log_error(f"Order validation failed: {e}")
            send_alert(f"Order rejected: {e}", priority='medium')
            return None

        except Exception as e:
            log_error(f"Order submission failed: {e}")
            send_alert(f"Order error: {e}", priority='high')
            return None

    def submit_bracket_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        entry_price: float
    ) -> Optional[object]:
        """
        Submit order with automatic stop-loss and take-profit.
        Why: Risk management on every trade. 3:1 reward:risk ratio.
        """
        try:
            self.validate_order(symbol, qty, side, entry_price)

            # Calculate protection levels
            if side == 'buy':
                stop_loss = entry_price * (1 - Config.STOP_LOSS_PCT)
                take_profit = entry_price * (1 + Config.TAKE_PROFIT_PCT)
            else:  # sell/short
                stop_loss = entry_price * (1 + Config.STOP_LOSS_PCT)
                take_profit = entry_price * (1 - Config.TAKE_PROFIT_PCT)

            # Submit bracket order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='limit',
                time_in_force='day',
                limit_price=entry_price,
                order_class='bracket',
                stop_loss={'stop_price': stop_loss},
                take_profit={'limit_price': take_profit}
            )

            log_info(
                f"Bracket order: {side} {qty} {symbol} @ ${entry_price:.2f} "
                f"[SL: ${stop_loss:.2f}, TP: ${take_profit:.2f}]"
            )

            send_alert(
                f"Bracket: {side} {qty} {symbol}\n"
                f"Entry: ${entry_price:.2f}\n"
                f"Stop: ${stop_loss:.2f}\n"
                f"Target: ${take_profit:.2f}",
                priority='low'
            )

            return order

        except Exception as e:
            log_error(f"Bracket order failed: {e}")
            send_alert(f"Bracket order error: {e}", priority='high')
            return None

    def cancel_all_orders(self, symbol: Optional[str] = None):
        """
        Emergency cancel all pending orders.
        Args:
            symbol: If specified, only cancel orders for that symbol
        """
        try:
            orders = self.api.list_orders(status='open')

            for order in orders:
                if symbol is None or order.symbol == symbol:
                    self.api.cancel_order(order.id)
                    log_info(f"Cancelled order: {order.symbol} {order.side} {order.qty}")

            log_info(f"Cancelled {len(orders)} open orders")
            send_alert(f"Cancelled {len(orders)} orders", priority='medium')

        except Exception as e:
            log_error(f"Failed to cancel orders: {e}")

    def close_all_positions(self):
        """
        Emergency liquidation of all positions.
        Use case: Circuit breaker triggered, need to go flat.
        """
        try:
            positions = self.api.list_positions()

            for position in positions:
                self.api.close_position(position.symbol)
                log_info(f"Closed position: {position.symbol} {position.qty} shares")

            log_info(f"Closed {len(positions)} positions")
            send_alert(f"Liquidated {len(positions)} positions", priority='high')

            self.positions = {}

        except Exception as e:
            log_error(f"Failed to close positions: {e}")
            send_alert(f"Liquidation error: {e}", priority='critical')

    def update_daily_pnl(self):
        """
        Calculate unrealized P&L for the day.
        Why: Track performance and enforce daily loss limits.
        """
        try:
            account = self.api.get_account()
            current_equity = float(account.equity)

            if self.start_of_day_equity == 0:
                self.start_of_day_equity = current_equity

            self.daily_pnl = current_equity - self.start_of_day_equity

            return self.daily_pnl

        except Exception as e:
            log_error(f"Failed to update P&L: {e}")
            return 0.0

    def get_position(self, symbol: str) -> int:
        """Get current position quantity for symbol"""
        return self.positions.get(symbol, 0)

    def get_stats(self) -> dict:
        """Get current order manager statistics"""
        return {
            'num_positions': len(self.positions),
            'positions': self.positions.copy(),
            'daily_pnl': self.daily_pnl,
            'account_equity': self.get_account_equity(),
            'buying_power': self.get_buying_power(),
            'num_orders_today': len(self.order_history),
            'market_open': self.is_market_open()
        }
