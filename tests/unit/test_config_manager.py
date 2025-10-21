"""
Unit tests untuk config manager
"""
import pytest
import os
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from config_manager import ConfigManager

class TestConfigManager:
    """Test cases untuk ConfigManager"""
    
    def test_init_without_env_file(self, temp_dir):
        """Test ConfigManager initialization tanpa .env file"""
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config = ConfigManager()
            assert config is not None
            assert isinstance(config.config, dict)
        finally:
            os.chdir(original_cwd)
    
    def test_environment_variable_fallback(self):
        """Test environment variable loading dengan fallback"""
        config = ConfigManager()
        
        # Test fallback values
        assert config.config['default_delay'] == 2.0
        assert config.config['max_retries'] == 3
        assert config.config['headless_mode'] == True
    
    def test_get_required_key(self):
        """Test get_required method"""
        config = ConfigManager()
        
        # Should not raise exception for existing keys
        chrome_binary = config.get_required('chrome_binary')
        assert chrome_binary is not None
    
    def test_get_required_missing_key(self):
        """Test get_required method dengan missing key"""
        config = ConfigManager()
        
        # Should raise ConfigurationError for missing required key
        with pytest.raises(Exception):  # Should raise ConfigurationError
            config.get_required('nonexistent_key')
    
    def test_get_with_default(self):
        """Test get method dengan default value"""
        config = ConfigManager()
        
        # Should return default value untuk missing key
        default_value = config.get('nonexistent_key', 'default_value')
        assert default_value == 'default_value'
    
    def test_validate_config(self):
        """Test configuration validation"""
        config = ConfigManager()
        
        # Should pass validation karena required keys sudah ada
        is_valid = config.validate_config()
        assert is_valid == True
