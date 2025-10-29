# Portfolio Testing

This file describes how to run tests for the portfolio website.

## Web-Based Tests

A simple test page is available to verify the portfolio website structure and functionality.

### Running the Tests

1. Open `test.html` in a web browser
2. Click the "Run Tests" button
3. View the test results

The tests verify:
- HTML structure (navigation, hero section, projects, contact)
- Navigation links exist
- Project cards are present
- CSS stylesheet loads correctly
- JavaScript file loads correctly

## Alpaca Trading Bot Tests

The alpaca-trading-bot directory contains comprehensive pytest tests.

### Running Python Tests

```bash
cd alpaca-trading-bot
pip install -r requirements.txt
pytest tests/ -v
```

The test suite includes:
- Strategy tests (mean reversion, momentum breakout)
- Order manager tests (validation, position sizing, risk management)
- Data cache tests (VWAP, price change, spread calculations)
