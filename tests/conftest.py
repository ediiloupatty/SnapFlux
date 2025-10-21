"""
Pytest configuration dan fixtures
"""
import pytest
import os
import tempfile
import sys
from pathlib import Path

# Add src to path untuk testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def temp_dir():
    """Create temporary directory untuk testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def test_config():
    """Test configuration dengan environment variables"""
    # Set test environment variables
    test_env = {
        'CHROME_BINARY_PATH': '/fake/chrome/path',
        'CHROMEDRIVER_PATH': '/fake/chromedriver/path',
        'LOGIN_URL': 'https://test.example.com/login',
        'DEFAULT_DELAY': '1.0',
        'HEADLESS_MODE': 'true',
        'MAX_RETRIES': '2'
    }
    
    # Backup existing env vars
    backup = {}
    for key, value in test_env.items():
        backup[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_env
    
    # Restore original env vars
    for key, original_value in backup.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value

@pytest.fixture
def sample_accounts():
    """Sample account data untuk testing"""
    return [
        ("Test Account 1", "test1@example.com", "1234"),
        ("Test Account 2", "08123456789", "5678"),
        ("Test Account 3", "test3@example.com", "0000"),  # Weak PIN untuk testing
    ]
