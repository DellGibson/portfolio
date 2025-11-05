"""
Test suite for trader_ai.py module structure and basic functionality.

These tests validate the code structure without requiring API keys or external services.
"""
import ast
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_trader_ai_syntax():
    """Test that trader_ai.py has valid Python syntax."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        code = f.read()
    
    # This will raise SyntaxError if the code is invalid
    ast.parse(code)


def test_trader_ai_has_main_function():
    """Test that trader_ai.py has a main() function."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        tree = ast.parse(f.read())
    
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert 'main' in functions, "main() function not found in trader_ai.py"


def test_trader_ai_has_required_functions():
    """Test that trader_ai.py has all required functions."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        tree = ast.parse(f.read())
    
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    required_functions = [
        'setup_logging',
        'home',
        'status_json',
        'get_logs',
        'trigger_trade',
        'run_server',
        'ping_healthchecks',
        'get_live_price',
        'ai_decision',
        'trade',
        'main'
    ]
    
    for func in required_functions:
        assert func in functions, f"Required function '{func}' not found in trader_ai.py"


def test_trader_ai_has_flask_routes():
    """Test that trader_ai.py has Flask route decorators."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        content = f.read()
    
    # Check for Flask routes
    assert "@app.route('/')" in content, "Home route not found"
    assert "@app.route('/status')" in content, "Status route not found"
    assert "@app.route('/logs')" in content, "Logs route not found"
    assert "@app.route('/run_trade', methods=['POST'])" in content, "Run trade route not found"


def test_trader_ai_has_global_variables():
    """Test that trader_ai.py defines required global variables."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        content = f.read()
    
    # Check for global variables
    assert "bot_status = {" in content, "bot_status dict not found"
    assert "RUN_TRADE_NOW = False" in content, "RUN_TRADE_NOW flag not found"
    assert "log_messages = deque(maxlen=100)" in content, "log_messages deque not found"


def test_trader_ai_has_required_imports():
    """Test that trader_ai.py has all required imports."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        tree = ast.parse(f.read())
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
    
    required_imports = [
        'os', 'time', 'schedule', 'requests', 'sys', 'logging',
        'dotenv', 'openai', 'flask', 'threading', 'collections'
    ]
    
    for imp in required_imports:
        assert imp in imports, f"Required import '{imp}' not found in trader_ai.py"


def test_trader_ai_has_deque_log_handler_class():
    """Test that trader_ai.py has DequeLogHandler class."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert 'DequeLogHandler' in classes, "DequeLogHandler class not found in trader_ai.py"


def test_trader_ai_executable():
    """Test that trader_ai.py has a shebang line."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        first_line = f.readline()
    
    assert first_line.startswith('#!'), "trader_ai.py should have a shebang line"
    assert 'python' in first_line.lower(), "Shebang should reference python"


def test_get_live_price_handles_single_symbol_correctly():
    """Test that get_live_price accesses trade.price directly for single symbol requests."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        content = f.read()
    
    # Parse the code to find the get_live_price function
    tree = ast.parse(content)
    
    # Find the get_live_price function
    get_live_price_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'get_live_price':
            get_live_price_func = node
            break
    
    assert get_live_price_func is not None, "get_live_price function not found"
    
    # Convert the function back to source code for inspection
    func_source = ast.unparse(get_live_price_func)
    
    # Verify that the function uses trade.price (correct) instead of trade[symbol].price (incorrect)
    assert 'trade.price' in func_source, \
        "get_live_price should access trade.price directly for single symbol"
    
    # Verify that the old dictionary-style access is NOT present
    assert 'trade[symbol]' not in func_source and 'trade[' not in func_source, \
        "get_live_price should not use dictionary-style access (trade[symbol])"
    
    # Verify that the old check "symbol not in trade" is NOT present
    assert 'not in trade' not in func_source, \
        "get_live_price should not check 'symbol not in trade' for single symbol requests"


def test_get_live_price_has_correct_comment():
    """Test that get_live_price has a comment explaining the LatestTrade object handling."""
    trader_ai_path = os.path.join(os.path.dirname(__file__), '..', 'trader_ai.py')
    with open(trader_ai_path, 'r') as f:
        lines = f.readlines()
    
    # Find the get_live_price function
    func_start = None
    func_end = None
    for i, line in enumerate(lines):
        if 'def get_live_price' in line:
            func_start = i
        if func_start is not None and line.strip().startswith('def ') and i > func_start:
            func_end = i
            break
    
    if func_end is None:
        func_end = len(lines)
    
    assert func_start is not None, "get_live_price function not found"
    
    # Get the function content
    func_content = ''.join(lines[func_start:func_end])
    
    # Verify that there's a comment about LatestTrade object
    assert 'LatestTrade' in func_content or 'latest trade' in func_content.lower(), \
        "get_live_price should have a comment explaining LatestTrade object handling"
