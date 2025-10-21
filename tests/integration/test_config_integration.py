"""
Integration tests untuk configuration system
"""
import pytest
import os
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from config_manager import config_manager

class TestConfigIntegration:
    """Integration tests untuk configuration system"""
    
    def test_config_manager_available(self):
        """Test bahwa global config manager tersedia"""
        assert config_manager is not None
        assert hasattr(config_manager, 'config')
    
    def test_config_values_loaded(self):
        """Test bahwa semua config values sudah loaded"""
        required_configs = [
            'chrome_binary', 'chromedriver_path', 'login_url',
            'default_delay', 'max_retries', 'headless_mode'
        ]
        
        for config_key in required_configs:
            assert config_key in config_manager.config
            assert config_manager.get(config_key) is not None
    
    def test_config_type_casting(self):
        """Test bahwa config values sudah di-cast ke tipe yang benar"""
        # Numeric values
        assert isinstance(config_manager.get('default_delay'), float)
        assert isinstance(config_manager.get('max_retries'), int)
        assert isinstance(config_manager.get('page_load_timeout'), int)
        
        # Boolean values
        assert isinstance(config_manager.get('headless_mode'), bool)
        
        # String values
        assert isinstance(config_manager.get('login_url'), str)
        assert isinstance(config_manager.get('chrome_binary'), str)
