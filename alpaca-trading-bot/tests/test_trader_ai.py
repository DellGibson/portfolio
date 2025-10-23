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
