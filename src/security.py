"""
Security utilities untuk credential management dan encryption
File ini mengelola enkripsi/dekripsi credentials dan validasi keamanan
"""
import os
import re
import hashlib
import base64
import logging
from typing import Optional

# Optional imports dengan fallback
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from .exceptions import SecurityError, ValidationError
    EXCEPTIONS_AVAILABLE = True
except ImportError:
    EXCEPTIONS_AVAILABLE = False
    class SecurityError(Exception):
        """Fallback SecurityError"""
        pass
    class ValidationError(Exception):
        """Fallback ValidationError"""
        pass

logger = logging.getLogger('security')

class CredentialManager:
    """Manager untuk enkripsi/dekripsi credentials"""
    
    def __init__(self):
        self.cipher = self._initialize_cipher()
    
    def _initialize_cipher(self):
        """Initialize encryption cipher dari environment variable"""
        if not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Cryptography not available, encryption features disabled")
            return None
            
        try:
            key_str = os.getenv('ENCRYPTION_KEY')
            if not key_str:
                # Generate key dan log untuk user
                key = Fernet.generate_key()
                key_str = key.decode()
                logger.warning(f"No ENCRYPTION_KEY found. Generated new key: {key_str}")
                logger.warning("Please set this key as environment variable: ENCRYPTION_KEY=" + key_str)
                return Fernet(key)
            
            # Convert string key to bytes
            if len(key_str) == 44:  # Base64 encoded key length
                key = key_str.encode()
            else:
                # Hash string input to create key
                key_hash = hashlib.sha256(key_str.encode()).digest()
                key = base64.urlsafe_b64encode(key_hash)
            
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")
            return None
    
    def encrypt_credential(self, credential: str) -> str:
        """Encrypt credential string"""
        if not self.cipher:
            raise SecurityError("Encryption not available - cipher not initialized")
        
        try:
            encrypted = self.cipher.encrypt(credential.encode())
            return encrypted.decode()
        except Exception as e:
            raise SecurityError(f"Failed to encrypt credential: {str(e)}")
    
    def decrypt_credential(self, encrypted_credential: str) -> str:
        """Decrypt credential string"""
        if not self.cipher:
            raise SecurityError("Encryption not available - cipher not initialized")
        
        try:
            decrypted = self.cipher.decrypt(encrypted_credential.encode())
            return decrypted.decode()
        except Exception as e:
            raise SecurityError(f"Failed to decrypt credential: {str(e)}")

class SecurityValidator:
    """Validasi security untuk berbagai input"""
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input untuk mencegah injection"""
        if not isinstance(input_str, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';]', '', input_str.strip())
        return sanitized
    
    @staticmethod
    def validate_and_encrypt_pin(pin: str) -> bool:
        """Enhanced PIN validation dengan security checks"""
        if not pin or len(pin) < 4 or len(pin) > 8:
            raise ValidationError("PIN must be between 4-8 digits", "PIN")
        
        if not pin.isdigit():
            raise ValidationError("PIN must contain only digits", "PIN")
        
        # Check for common weak PINs
        weak_pins = {'0000', '1111', '1234', '8888', '9999', '12345', '54321'}
        if pin in weak_pins:
            logger.warning(f"Weak PIN detected: {pin}")
            # Don't raise error, just warn
        
        return True
    
    @staticmethod
    def validate_username_security(username: str) -> bool:
        """Validate username untuk security risks"""
        sanitized = SecurityValidator.sanitize_input(username)
        if sanitized != username:
            logger.warning(f"Username contained potentially dangerous characters: {username}")
            return False
        
        return True

# Global instances
credential_manager = CredentialManager()
security_validator = SecurityValidator()
