# GitHub Copilot Instructions for Portfolio Repository

## Repository Overview

This is a personal portfolio website with two main components:
1. **Frontend Portfolio**: HTML/CSS/JavaScript static website
2. **Alpaca Trading Bot**: Python-based algorithmic trading application

## Build & Test Instructions

### Portfolio Website (Root Directory)

The portfolio website is a static HTML/CSS/JavaScript site with no build step required.

**Testing:**
```bash
# Open test.html in a web browser and click "Run Tests"
# Or run a simple local server:
python -m http.server 8000
# Then navigate to http://localhost:8000/test.html
```

**Files:**
- `index.html` - Main portfolio page
- `style.css` - Stylesheet
- `script.js` - JavaScript functionality
- `test.html` - Web-based test suite

### Alpaca Trading Bot (alpaca-trading-bot/)

**Setup:**
```bash
cd alpaca-trading-bot
pip install -r requirements.txt
```

**Testing:**
```bash
cd alpaca-trading-bot
pytest tests/ -v
```

**Test Coverage:**
```bash
cd alpaca-trading-bot
pytest tests/ -v --cov=. --cov-report=term-missing
```

## Coding Standards

### General Guidelines

- Make minimal, surgical changes to accomplish the task
- Preserve existing code style and formatting
- Don't modify working code unless necessary for the task
- Test all changes before committing

### HTML/CSS/JavaScript

- Use semantic HTML5 elements
- Maintain responsive design principles
- Keep CSS organized and readable
- Use vanilla JavaScript (no frameworks currently in use)
- Follow existing naming conventions (kebab-case for classes, camelCase for JavaScript)

### Python (Alpaca Trading Bot)

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write comprehensive docstrings for functions and classes
- Maintain test coverage for all new features
- Use pytest for all testing
- Keep configuration in `config.py` or `.env` files
- Never commit sensitive credentials (API keys, secrets)

## Project-Specific Guidelines

### Portfolio Website

- Ensure all changes maintain mobile responsiveness
- Keep the design clean and professional
- Test in multiple browsers if making CSS changes
- Verify navigation links work correctly

### Alpaca Trading Bot

- All trading strategies must have corresponding unit tests
- Order management changes require thorough testing
- Data cache operations should be validated
- Consider edge cases (market closed, API failures, invalid data)
- Follow existing patterns for strategy implementation
- Maintain backward compatibility with existing strategies

## File Structure

```
.
├── .github/                 # GitHub configuration (this file)
├── alpaca-trading-bot/     # Python trading bot
│   ├── tests/              # Pytest test files
│   ├── *.py                # Python modules
│   └── requirements.txt    # Python dependencies
├── index.html              # Portfolio homepage
├── style.css               # Styles
├── script.js               # JavaScript
├── test.html               # Test suite
├── README.md               # Project documentation
└── TESTING.md              # Testing documentation
```

## Do's and Don'ts

### DO:
- Read and follow TESTING.md for test instructions
- Run tests before and after making changes
- Verify changes don't break existing functionality
- Use existing libraries and dependencies when possible
- Keep changes focused and minimal
- Update documentation if behavior changes

### DON'T:
- Don't add new dependencies without justification
- Don't modify test files unless fixing or adding tests
- Don't remove or edit unrelated tests
- Don't commit build artifacts or dependencies
- Don't commit `.env` files or API credentials
- Don't make large-scale refactoring changes unless specifically requested
- Don't modify working code unnecessarily

## Security Considerations

- Never commit API keys, tokens, or credentials
- For the alpaca-trading-bot, use `.env.example` as template for environment variables
- Validate all user inputs
- Follow secure coding practices for financial data handling
- Be cautious with external API integrations

## Testing Requirements

- All new Python code should have corresponding pytest tests
- Test coverage should not decrease
- Frontend changes should pass the test.html test suite
- Manual testing is required for UI changes
- Take screenshots of UI changes for review

## Error Handling

- Use appropriate exception handling in Python code
- Provide meaningful error messages
- Log errors appropriately for debugging
- Handle API failures gracefully in the trading bot

## Documentation

- Update README.md if adding new features
- Update TESTING.md if changing test procedures
- Add inline comments for complex logic
- Keep documentation concise and accurate
