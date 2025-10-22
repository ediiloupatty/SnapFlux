"""
Configuration manager untuk environment dan YAML configuration
File ini mengelola semua konfigurasi aplikasi dengan fallback strategy
"""
import os
import logging
from pathlib import Path
from typing import Union, Any

# Optional imports dengan fallback
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from .exceptions import ConfigurationError
    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False
    class ConfigurationError(Exception):
        """Fallback ConfigurationError jika exceptions module tidak tersedia"""
        pass

logger = logging.getLogger('config_manager')

class ConfigManager:
    """Manager untuk semua konfigurasi aplikasi"""
    
    def __init__(self):
        self.config = {}
        self.load_env_file()
        self.load_yaml_config()
        self.load_environment_variables()
    
    def load_env_file(self):
        """Load configuration dari .env file jika ada"""
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            # Remove quotes if present and strip whitespace
                            key = key.strip()
                            value = value.strip('"\' \t\r\n')
                            os.environ[key] = value
                logger.info("Environment file loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load .env file: {str(e)}")
    
    def load_yaml_config(self):
        """Load configuration dari config.yaml"""
        if not YAML_AVAILABLE:
            logger.warning("YAML not available, skipping config.yaml loading")
            return
            
        config_file = Path('config.yaml')
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self.config.update(yaml_config)
                logger.info("YAML configuration loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load config.yaml: {str(e)}")
    
    def load_environment_variables(self):
        """Load configuration dari environment variables"""
        # Browser configuration
        self.config['chrome_binary'] = self.get_env_with_fallback(
            'CHROME_BINARY_PATH', 
            'D:\\edi\\Programing\\Snapflux v2\\chrome\\Chromium\\bin\\chrome.exe'
        )
        self.config['chromedriver_path'] = self.get_env_with_fallback(
            'CHROMEDRIVER_PATH',
            'D:\\edi\\Programing\\Snapflux v2\\chrome\\chromedriver.exe'
        )
        
        # URL configuration
        self.config['login_url'] = self.get_env_with_fallback(
            'LOGIN_URL',
            'https://subsiditepatlpg.mypertamina.id/merchant-login'
        )
        
        # Timing configuration
        self.config['default_delay'] = float(self.get_env_with_fallback('DEFAULT_DELAY', '3.0'))
        self.config['retry_delay'] = float(self.get_env_with_fallback('RETRY_DELAY', '3.0'))
        self.config['error_delay'] = float(self.get_env_with_fallback('ERROR_DELAY', '2.0'))
        self.config['inter_account_delay'] = float(self.get_env_with_fallback('INTER_ACCOUNT_DELAY', '4.0'))
        self.config['max_retries'] = self.get_env_int_with_fallback('MAX_RETRIES', 3)
        
        # Browser settings
        self.config['headless_mode'] = self.get_env_with_fallback('HEADLESS_MODE', 'true').strip().lower() == 'true'
        self.config['page_load_timeout'] = self.get_env_int_with_fallback('PAGE_LOAD_TIMEOUT', 20)
        self.config['implicit_wait'] = self.get_env_int_with_fallback('IMPLICIT_WAIT', 5)
        
        # Logging configuration
        self.config['log_level'] = self.get_env_with_fallback('LOG_LEVEL', 'DEBUG')
        self.config['log_file'] = self.get_env_with_fallback('LOG_FILE', 'automation.log')
        self.config['log_max_size'] = int(self.get_env_with_fallback('LOG_MAX_SIZE', '2097152'))
        self.config['log_backup_count'] = int(self.get_env_with_fallback('LOG_BACKUP_COUNT', '3'))
    
    def get_env_with_fallback(self, key: str, fallback: str) -> str:
        """Get environment variable dengan fallback value"""
        return os.getenv(key, fallback)
    
    def get_env_int_with_fallback(self, key: str, fallback: int) -> int:
        """Get environment variable sebagai integer dengan fallback value"""
        try:
            value = os.getenv(key, str(fallback))
            # Strip non-numeric characters from the end (like 'ss' in '5ss')
            import re
            numeric_value = re.match(r'^(\d+)', value.strip())
            if numeric_value:
                return int(numeric_value.group(1))
            return fallback
        except (ValueError, TypeError):
            return fallback
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value dengan default fallback"""
        return self.config.get(key, default)
    
    def get_required(self, key: str) -> Any:
        """Get required configuration value, raise error if not found"""
        value = self.config.get(key)
        if value is None:
            raise ConfigurationError(f"Required configuration key '{key}' not found")
        return value
    
    def validate_config(self) -> bool:
        """Validate semua required configuration"""
        required_keys = ['chrome_binary', 'chromedriver_path', 'login_url']
        
        for key in required_keys:
            try:
                self.get_required(key)
            except ConfigurationError as e:
                logger.error(f"Configuration validation failed: {str(e)}")
                return False
        
        return True

# Global config instance
config_manager = ConfigManager()
