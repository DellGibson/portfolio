#!/usr/bin/env python
"""
Alpaca Trading Bot - Desktop GUI Application

Professional PyQt6 desktop interface with:
- Real-time dashboard
- System tray icon
- Desktop notifications
- Multi-window interface
- Keyboard shortcuts
- Live charts and metrics

Run: python gui_app.py
"""

import sys
import os
from datetime import datetime
from typing import Optional
import asyncio

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QSystemTrayIcon,
    QMenu, QTabWidget, QGroupBox, QGridLayout, QTextEdit, QSplitter,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette, QPixmap
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config
    from order_manager import OrderManager
    from data_cache import MarketDataCache
    from strategy import MeanReversionStrategy, MomentumBreakoutStrategy, HybridStrategy
    import alpaca_trade_api as tradeapi
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the alpaca-trading-bot directory")
    sys.exit(1)


class BotWorker(QThread):
    """Background thread that runs the trading bot"""

    status_update = pyqtSignal(dict)  # Emit status updates
    error_occurred = pyqtSignal(str)  # Emit errors

    def __init__(self):
        super().__init__()
        self.running = False
        self.api = None
        self.order_manager = None
        self.cache = None
        self.strategy = None

    def run(self):
        """Run the bot in background thread"""
        try:
            # Initialize components
            self.api = tradeapi.REST(
                Config.ALPACA_API_KEY,
                Config.ALPACA_SECRET_KEY,
                Config.ALPACA_BASE_URL
            )

            self.order_manager = OrderManager(self.api)
            self.cache = MarketDataCache()
            self.strategy = MeanReversionStrategy()

            self.running = True

            while self.running:
                # Get current stats
                try:
                    account = self.api.get_account()
                    positions = self.api.list_positions()

                    stats = {
                        'balance': float(account.equity),
                        'buying_power': float(account.buying_power),
                        'daily_pnl': self.order_manager.daily_pnl,
                        'positions_count': len(positions),
                        'positions': positions,
                        'timestamp': datetime.now()
                    }

                    self.status_update.emit(stats)

                except Exception as e:
                    self.error_occurred.emit(str(e))

                # Sleep before next update
                self.msleep(5000)  # 5 seconds

        except Exception as e:
            self.error_occurred.emit(f"Bot error: {e}")

    def stop(self):
        """Stop the bot"""
        self.running = False


class DashboardWidget(QWidget):
    """Main dashboard widget showing account overview"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Account metrics group
        metrics_group = QGroupBox("Account Overview")
        metrics_layout = QGridLayout()

        # Balance
        self.balance_label = QLabel("$0.00")
        self.balance_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        metrics_layout.addWidget(QLabel("Balance:"), 0, 0)
        metrics_layout.addWidget(self.balance_label, 0, 1)

        # Daily P&L
        self.pnl_label = QLabel("$0.00")
        self.pnl_label.setFont(QFont("Arial", 18))
        metrics_layout.addWidget(QLabel("Daily P&L:"), 1, 0)
        metrics_layout.addWidget(self.pnl_label, 1, 1)

        # Buying Power
        self.buying_power_label = QLabel("$0.00")
        metrics_layout.addWidget(QLabel("Buying Power:"), 2, 0)
        metrics_layout.addWidget(self.buying_power_label, 2, 1)

        # Position Count
        self.positions_label = QLabel("0")
        metrics_layout.addWidget(QLabel("Open Positions:"), 3, 0)
        metrics_layout.addWidget(self.positions_label, 3, 1)

        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # Chart placeholder
        chart_group = QGroupBox("Equity Curve")
        chart_layout = QVBoxLayout()

        self.chart = QChart()
        self.chart.setTitle("Account Balance Over Time")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.series = QLineSeries()
        self.series.setName("Balance")
        self.chart.addSeries(self.series)

        # Create axes
        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("hh:mm:ss")
        self.axis_x.setTitleText("Time")
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Balance ($)")
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axis_y)

        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(chart_view.RenderHint.Antialiasing)
        chart_layout.addWidget(chart_view)

        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group)

        self.setLayout(layout)

    def update_stats(self, stats: dict):
        """Update dashboard with new stats"""
        # Update labels
        balance = stats.get('balance', 0)
        self.balance_label.setText(f"${balance:,.2f}")

        pnl = stats.get('daily_pnl', 0)
        self.pnl_label.setText(f"${pnl:,.2f}")

        # Color P&L based on positive/negative
        if pnl >= 0:
            self.pnl_label.setStyleSheet("color: green;")
        else:
            self.pnl_label.setStyleSheet("color: red;")

        buying_power = stats.get('buying_power', 0)
        self.buying_power_label.setText(f"${buying_power:,.2f}")

        positions_count = stats.get('positions_count', 0)
        self.positions_label.setText(str(positions_count))

        # Update chart
        timestamp = stats.get('timestamp', datetime.now())
        self.series.append(timestamp.timestamp() * 1000, balance)

        # Keep only last 100 points
        if self.series.count() > 100:
            self.series.remove(0)


class PositionsWidget(QWidget):
    """Widget showing current positions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Positions table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'Symbol', 'Quantity', 'Entry Price', 'Current Price', 'P&L $', 'P&L %'
        ])
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_positions(self, positions):
        """Update positions table"""
        self.table.setRowCount(len(positions))

        for i, pos in enumerate(positions):
            self.table.setItem(i, 0, QTableWidgetItem(pos.symbol))
            self.table.setItem(i, 1, QTableWidgetItem(str(pos.qty)))
            self.table.setItem(i, 2, QTableWidgetItem(f"${float(pos.avg_entry_price):.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"${float(pos.current_price):.2f}"))

            pnl = float(pos.unrealized_pl)
            pnl_pct = float(pos.unrealized_plpc) * 100

            pnl_item = QTableWidgetItem(f"${pnl:.2f}")
            pnl_pct_item = QTableWidgetItem(f"{pnl_pct:+.2f}%")

            # Color based on profit/loss
            color = QColor(0, 150, 0) if pnl >= 0 else QColor(200, 0, 0)
            pnl_item.setForeground(color)
            pnl_pct_item.setForeground(color)

            self.table.setItem(i, 4, pnl_item)
            self.table.setItem(i, 5, pnl_pct_item)


class LogWidget(QWidget):
    """Widget showing bot logs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier", 10))

        layout.addWidget(self.text_edit)

        # Clear button
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.text_edit.clear)
        layout.addWidget(clear_btn)

        self.setLayout(layout)

    def add_log(self, message: str):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.bot_worker = None
        self.init_ui()
        self.create_system_tray()
        self.setup_shortcuts()

    def init_ui(self):
        self.setWindowTitle("Alpaca Trading Bot - Desktop GUI")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget with tabs
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Control buttons
        controls_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Start Bot")
        self.start_btn.clicked.connect(self.start_bot)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-size: 14px;")
        controls_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹ Stop Bot")
        self.stop_btn.clicked.connect(self.stop_bot)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-size: 14px;")
        controls_layout.addWidget(self.stop_btn)

        self.emergency_btn = QPushButton("🚨 Emergency Stop")
        self.emergency_btn.clicked.connect(self.emergency_stop)
        self.emergency_btn.setStyleSheet("background-color: #ff9800; color: white; padding: 10px; font-size: 14px;")
        controls_layout.addWidget(self.emergency_btn)

        controls_layout.addStretch()

        # Status label
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        controls_layout.addWidget(self.status_label)

        layout.addLayout(controls_layout)

        # Tabs
        tabs = QTabWidget()

        # Dashboard tab
        self.dashboard = DashboardWidget()
        tabs.addTab(self.dashboard, "📊 Dashboard")

        # Positions tab
        self.positions = PositionsWidget()
        tabs.addTab(self.positions, "📈 Positions")

        # Logs tab
        self.logs = LogWidget()
        tabs.addTab(self.logs, "📝 Logs")

        layout.addWidget(tabs)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+S")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_system_tray(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)

        # Create icon (using a simple colored square as placeholder)
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(76, 175, 80))  # Green
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        start_action = QAction("Start Bot", self)
        start_action.triggered.connect(self.start_bot)
        tray_menu.addAction(start_action)

        stop_action = QAction("Stop Bot", self)
        stop_action.triggered.connect(self.stop_bot)
        tray_menu.addAction(stop_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Handle tray icon activation
        self.tray_icon.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        """Handle system tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Ctrl+R to refresh
        refresh_shortcut = QAction(self)
        refresh_shortcut.setShortcut("Ctrl+R")
        refresh_shortcut.triggered.connect(self.refresh_data)
        self.addAction(refresh_shortcut)

    def start_bot(self):
        """Start the trading bot"""
        if self.bot_worker and self.bot_worker.isRunning():
            return

        self.logs.add_log("Starting trading bot...")
        self.status_label.setText("Status: Starting...")
        self.status_label.setStyleSheet("color: orange;")

        # Create and start worker thread
        self.bot_worker = BotWorker()
        self.bot_worker.status_update.connect(self.on_status_update)
        self.bot_worker.error_occurred.connect(self.on_error)
        self.bot_worker.start()

        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Status: Running")
        self.status_label.setStyleSheet("color: green;")

        # Show notification
        self.show_notification("Bot Started", "Trading bot is now running")
        self.logs.add_log("Bot started successfully")

    def stop_bot(self):
        """Stop the trading bot"""
        if not self.bot_worker or not self.bot_worker.isRunning():
            return

        self.logs.add_log("Stopping trading bot...")
        self.bot_worker.stop()
        self.bot_worker.wait()

        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: red;")

        self.show_notification("Bot Stopped", "Trading bot has been stopped")
        self.logs.add_log("Bot stopped")

    def emergency_stop(self):
        """Emergency stop with confirmation"""
        reply = QMessageBox.question(
            self,
            "Emergency Stop",
            "This will:\n• Stop the bot\n• Cancel all pending orders\n• Close all positions\n\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logs.add_log("EMERGENCY STOP initiated!")

            try:
                # Cancel all orders
                if self.bot_worker and self.bot_worker.api:
                    self.bot_worker.api.cancel_all_orders()
                    self.logs.add_log("All orders cancelled")

                    # Close all positions
                    positions = self.bot_worker.api.list_positions()
                    for pos in positions:
                        self.bot_worker.api.close_position(pos.symbol)
                        self.logs.add_log(f"Closed position: {pos.symbol}")

                self.show_notification("Emergency Stop", "All positions closed, bot stopped", urgent=True)

            except Exception as e:
                self.logs.add_log(f"Emergency stop error: {e}")

            finally:
                self.stop_bot()

    def on_status_update(self, stats: dict):
        """Handle status update from bot worker"""
        # Update dashboard
        self.dashboard.update_stats(stats)

        # Update positions
        positions = stats.get('positions', [])
        self.positions.update_positions(positions)

    def on_error(self, error_msg: str):
        """Handle error from bot worker"""
        self.logs.add_log(f"ERROR: {error_msg}")
        self.show_notification("Bot Error", error_msg, urgent=True)

    def show_notification(self, title: str, message: str, urgent: bool = False):
        """Show desktop notification"""
        icon = QSystemTrayIcon.MessageIcon.Critical if urgent else QSystemTrayIcon.MessageIcon.Information
        self.tray_icon.showMessage(title, message, icon, 3000)

    def refresh_data(self):
        """Manually refresh data"""
        self.logs.add_log("Refreshing data...")
        # Trigger immediate update from worker

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Alpaca Trading Bot",
            "Alpaca Trading Bot - Desktop GUI\n\n"
            "Version: 1.0.0\n"
            "A professional algorithmic trading system\n\n"
            "Features:\n"
            "• Real-time monitoring\n"
            "• System tray integration\n"
            "• Desktop notifications\n"
            "• Multi-window interface\n"
            "• Keyboard shortcuts\n\n"
            "Built with PyQt6"
        )

    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to quit?\n\nThe bot will stop running.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.bot_worker:
                self.bot_worker.stop()
                self.bot_worker.wait()
            event.accept()
        else:
            event.ignore()


class SettingsDialog(QDialog):
    """Settings dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Risk settings
        self.max_position = QDoubleSpinBox()
        self.max_position.setRange(0.01, 1.0)
        self.max_position.setSingleStep(0.01)
        self.max_position.setValue(Config.MAX_POSITION_PCT)
        self.max_position.setSuffix("%")
        layout.addRow("Max Position Size:", self.max_position)

        self.max_loss = QDoubleSpinBox()
        self.max_loss.setRange(0.01, 0.1)
        self.max_loss.setSingleStep(0.01)
        self.max_loss.setValue(Config.MAX_DAILY_LOSS_PCT)
        self.max_loss.setSuffix("%")
        layout.addRow("Max Daily Loss:", self.max_loss)

        # Buttons
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addRow(buttons_layout)

        self.setLayout(layout)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Alpaca Trading Bot")
    app.setOrganizationName("Alpaca Trading")

    # Set application-wide style
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
