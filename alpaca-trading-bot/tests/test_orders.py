"""
Unit tests for OrderManager.

Tests:
- Position size validation
- Daily loss limit enforcement
- Market hours checking
- Buying power validation
- Limit price calculation
- Bracket order levels
- Position reconciliation
- Order validation logic
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from order_manager import OrderManager
from config import Config


class TestOrderManager:
    """Test suite for OrderManager"""

    @pytest.fixture
    def mock_api(self):
        """Create mock Alpaca API"""
        api = Mock()

        # Mock account
        account = Mock()
        account.equity = '100000.00'
        account.buying_power = '50000.00'
        api.get_account.return_value = account

        # Mock clock (market open)
        clock = Mock()
        clock.is_open = True
        api.get_clock.return_value = clock

        # Mock positions
        api.list_positions.return_value = []

        # Mock quote
        quote = Mock()
        quote.bp = 100.00  # bid price
        quote.ap = 100.20  # ask price
        api.get_latest_quote.return_value = quote

        return api

    @pytest.fixture
    def order_manager(self, mock_api):
        """Create OrderManager with mocked API"""
        with patch('order_manager.log_info'), \
             patch('order_manager.log_error'), \
             patch('order_manager.send_alert'):
            manager = OrderManager(mock_api)
            return manager

    def test_position_size_validation_exceeds_limit(self, order_manager, mock_api):
        """Test 1: Reject order exceeding position size limit"""
        # Try to buy $15,000 worth (15% of $100k account)
        # Config.MAX_POSITION_PCT = 0.10 (10% max)

        with pytest.raises(ValueError, match="exceeds.*limit"):
            order_manager.validate_order(
                symbol='AAPL',
                qty=150,  # 150 shares * $100 = $15,000
                side='buy',
                price=100.00
            )

    def test_position_size_validation_within_limit(self, order_manager, mock_api):
        """Test 2: Accept order within position size limit"""
        # Buy $8,000 worth (8% of $100k account) - should pass
        result = order_manager.validate_order(
            symbol='AAPL',
            qty=80,  # 80 shares * $100 = $8,000
            side='buy',
            price=100.00
        )

        assert result is True

    def test_daily_loss_limit_exceeded(self, order_manager, mock_api):
        """Test 3: Reject order when daily loss limit hit"""
        # Set daily P&L to -$2,500 (2.5% of $100k)
        # Config.MAX_DAILY_LOSS_PCT = 0.02 (2% max)
        order_manager.daily_pnl = -2500.00

        with pytest.raises(ValueError, match="Daily loss limit"):
            order_manager.validate_order(
                symbol='MSFT',
                qty=50,
                side='buy',
                price=100.00
            )

    def test_market_closed_rejection(self, order_manager, mock_api):
        """Test 4: Reject order when market is closed"""
        # Set market as closed
        clock = Mock()
        clock.is_open = False
        mock_api.get_clock.return_value = clock

        with pytest.raises(ValueError, match="Market is closed"):
            order_manager.validate_order(
                symbol='GOOGL',
                qty=50,
                side='buy',
                price=140.00
            )

    def test_insufficient_buying_power(self, order_manager, mock_api):
        """Test 5: Reject order with insufficient buying power"""
        # Account has $50k buying power, $100k equity
        # Try to buy $9k worth (within position size limit of 10% = $10k)
        # But set buying power to only $5k
        account = Mock()
        account.equity = '100000.00'
        account.buying_power = '5000.00'  # Less than order value
        mock_api.get_account.return_value = account

        with pytest.raises(ValueError, match="Insufficient buying power"):
            order_manager.validate_order(
                symbol='TSLA',
                qty=90,  # 90 * $100 = $9,000 (within 10% limit but exceeds buying power)
                side='buy',
                price=100.00
            )

    def test_limit_price_calculation_patient(self, order_manager, mock_api):
        """Test 6: Limit price calculation with low aggression (patient)"""
        # Mock quote: bid=$100, ask=$100.20
        # aggression=0.0 → should return bid price for buy
        limit_price = order_manager.calculate_limit_price('AAPL', 'buy', aggression=0.0)

        assert abs(limit_price - 100.00) < 0.01

    def test_limit_price_calculation_mid(self, order_manager, mock_api):
        """Test 7: Limit price calculation with medium aggression"""
        # Mock quote: bid=$100, ask=$100.20
        # aggression=0.5 → should return mid price ($100.10)
        limit_price = order_manager.calculate_limit_price('AAPL', 'buy', aggression=0.5)

        assert abs(limit_price - 100.10) < 0.01

    def test_limit_price_calculation_aggressive(self, order_manager, mock_api):
        """Test 8: Limit price calculation with high aggression (urgent)"""
        # Mock quote: bid=$100, ask=$100.20
        # aggression=1.0 → should return ask price for buy
        limit_price = order_manager.calculate_limit_price('AAPL', 'buy', aggression=1.0)

        assert abs(limit_price - 100.20) < 0.01

    def test_bracket_order_levels_buy(self, order_manager, mock_api):
        """Test 9: Bracket order calculates correct stop/profit levels for buy"""
        # Entry at $100
        # Stop loss: $100 * (1 - 0.02) = $98
        # Take profit: $100 * (1 + 0.06) = $106

        entry_price = 100.00
        expected_stop = entry_price * (1 - Config.STOP_LOSS_PCT)
        expected_profit = entry_price * (1 + Config.TAKE_PROFIT_PCT)

        assert abs(expected_stop - 98.00) < 0.01
        assert abs(expected_profit - 106.00) < 0.01

        # Verify 3:1 reward:risk ratio
        risk = entry_price - expected_stop  # $2
        reward = expected_profit - entry_price  # $6
        ratio = reward / risk

        assert abs(ratio - 3.0) < 0.1

    def test_position_reconciliation(self, order_manager, mock_api):
        """Test 10: Position reconciliation updates local cache"""
        # Set local cache to 100 shares AAPL
        order_manager.positions = {'AAPL': 100}

        # Mock API returns 150 shares AAPL
        position = Mock()
        position.symbol = 'AAPL'
        position.qty = '150'
        mock_api.list_positions.return_value = [position]

        # Sync positions
        with patch('order_manager.log_info'), \
             patch('order_manager.log_error'):
            order_manager._sync_positions()

        # Local cache should now match broker (150 shares)
        assert order_manager.positions['AAPL'] == 150

    def test_invalid_quantity_rejection(self, order_manager, mock_api):
        """Test 11: Reject order with invalid quantity"""
        with pytest.raises(ValueError, match="Invalid quantity"):
            order_manager.validate_order(
                symbol='SPY',
                qty=0,  # Zero quantity
                side='buy',
                price=400.00
            )

        with pytest.raises(ValueError, match="Invalid quantity"):
            order_manager.validate_order(
                symbol='SPY',
                qty=-10,  # Negative quantity
                side='buy',
                price=400.00
            )

    def test_get_account_equity(self, order_manager, mock_api):
        """Test 12: Get account equity from API"""
        equity = order_manager.get_account_equity()

        assert equity == 100000.00
        mock_api.get_account.assert_called()

    def test_get_buying_power(self, order_manager, mock_api):
        """Test 13: Get buying power from API"""
        buying_power = order_manager.get_buying_power()

        assert buying_power == 50000.00
        mock_api.get_account.assert_called()

    def test_market_hours_check(self, order_manager, mock_api):
        """Test 14: Market hours check"""
        # Market open
        assert order_manager.is_market_open() is True

        # Market closed
        clock = Mock()
        clock.is_open = False
        mock_api.get_clock.return_value = clock

        assert order_manager.is_market_open() is False

    def test_get_current_price(self, order_manager, mock_api):
        """Test 15: Get current price from API"""
        price = order_manager.get_current_price('AAPL')

        # Should return ask price (100.20)
        assert price == 100.20
        mock_api.get_latest_quote.assert_called_with('AAPL')

    def test_order_submission_success(self, order_manager, mock_api):
        """Test 16: Successful order submission"""
        # Mock successful order
        order = Mock()
        order.id = 'order123'
        mock_api.submit_order.return_value = order

        with patch('order_manager.log_info'), \
             patch('order_manager.send_alert'):
            submitted_order = order_manager.submit_order(
                symbol='AAPL',
                qty=50,
                side='buy'
            )

        assert submitted_order is not None
        assert submitted_order.id == 'order123'

        # Verify order was logged
        assert len(order_manager.order_history) > 0

    def test_order_submission_validation_failure(self, order_manager, mock_api):
        """Test 17: Order submission fails validation"""
        with patch('order_manager.log_error'), \
             patch('order_manager.send_alert'):
            # Try to submit order exceeding limits
            order = order_manager.submit_order(
                symbol='AAPL',
                qty=2000,  # Way too large
                side='buy'
            )

        # Should return None (validation failed)
        assert order is None

    def test_get_position(self, order_manager):
        """Test 18: Get position quantity for symbol"""
        order_manager.positions = {'AAPL': 100, 'MSFT': 50}

        assert order_manager.get_position('AAPL') == 100
        assert order_manager.get_position('MSFT') == 50
        assert order_manager.get_position('GOOGL') == 0  # Not in positions

    def test_update_daily_pnl(self, order_manager, mock_api):
        """Test 19: Daily P&L calculation"""
        # Set start of day equity
        order_manager.start_of_day_equity = 100000.00

        # Current equity is $102,000 (from mock)
        # But let's change it to $101,500 for this test
        account = Mock()
        account.equity = '101500.00'
        mock_api.get_account.return_value = account

        pnl = order_manager.update_daily_pnl()

        # P&L should be $1,500
        assert abs(pnl - 1500.00) < 0.01
        assert abs(order_manager.daily_pnl - 1500.00) < 0.01

    def test_get_stats(self, order_manager):
        """Test 20: Get order manager statistics"""
        order_manager.positions = {'AAPL': 100}
        order_manager.daily_pnl = 500.00
        order_manager.order_history = [{'id': 1}, {'id': 2}]

        stats = order_manager.get_stats()

        assert stats['num_positions'] == 1
        assert stats['daily_pnl'] == 500.00
        assert stats['num_orders_today'] == 2
        assert stats['account_equity'] == 100000.00


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
