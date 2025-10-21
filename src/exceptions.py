"""
Custom exceptions untuk Snapflux automation
File ini berisi semua custom exception classes untuk error handling yang lebih spesifik
"""

class SnapfluxBaseException(Exception):
    """Base exception untuk semua exception di aplikasi Snapflux"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

class AuthenticationError(SnapfluxBaseException):
    """Raised ketika proses login gagal"""
    def __init__(self, message: str, username: str = None, error_code: str = "AUTH_FAILED"):
        super().__init__(message, error_code)
        self.username = username

class NavigationError(SnapfluxBaseException):
    """Raised ketika navigasi halaman gagal"""
    def __init__(self, message: str, target_page: str = None, error_code: str = "NAV_FAILED"):
        super().__init__(message, error_code)
        self.target_page = target_page

class DataExtractionError(SnapfluxBaseException):
    """Raised ketika ekstraksi data gagal"""
    def __init__(self, message: str, data_type: str = None, error_code: str = "EXTRACT_FAILED"):
        super().__init__(message, error_code)
        self.data_type = data_type

class ConfigurationError(SnapfluxBaseException):
    """Raised ketika konfigurasi tidak valid"""
    def __init__(self, message: str, config_key: str = None, error_code: str = "CONFIG_ERROR"):
        super().__init__(message, error_code)
        self.config_key = config_key

class DriverSetupError(SnapfluxBaseException):
    """Raised ketika setup WebDriver gagal"""
    def __init__(self, message: str, error_code: str = "DRIVER_SETUP_FAILED"):
        super().__init__(message, error_code)

class ValidationError(SnapfluxBaseException):
    """Raised ketika validasi input gagal"""
    def __init__(self, message: str, field_name: str = None, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)
        self.field_name = field_name

class SecurityError(SnapfluxBaseException):
    """Raised ketika terjadi masalah keamanan"""
    def __init__(self, message: str, error_code: str = "SECURITY_ERROR"):
        super().__init__(message, error_code)
