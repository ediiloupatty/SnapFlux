"""
Unit tests untuk validator functions
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from validators import (
    is_valid_email, is_valid_phone, is_valid_pin,
    parse_stok_to_int, parse_inputan_to_int
)
from security import SecurityValidator

class TestValidators:
    """Test cases untuk validator functions"""
    
    def test_is_valid_email(self):
        """Test email validation"""
        # Valid emails
        assert is_valid_email("test@example.com") == True
        assert is_valid_email("user.name+tag@domain.co.uk") == True
        assert is_valid_email("user123@test-domain.com") == True
        
        # Invalid emails
        assert is_valid_email("invalid-email") == False
        assert is_valid_email("@domain.com") == False
        assert is_valid_email("user@") == False
        assert is_valid_email("") == False
        assert is_valid_email(None) == False
    
    def test_is_valid_phone(self):
        """Test phone number validation"""
        # Valid phone numbers
        assert is_valid_phone("081234567890") == True
        assert is_valid_phone("08123456789") == True
        assert is_valid_phone("6281234567890") == True
        
        # Invalid phone numbers
        assert is_valid_phone("123") == False  # Too short
        assert is_valid_phone("08123456789012345") == False  # Too long
        assert is_valid_phone("1234567890") == False  # Wrong format
        assert is_valid_phone("invalid") == False
        assert is_valid_phone("") == False
    
    def test_is_valid_pin(self):
        """Test PIN validation"""
        # Valid PINs
        assert is_valid_pin("1234") == True
        assert is_valid_pin("567890") == True
        assert is_valid_pin("12345678") == True
        
        # Invalid PINs
        assert is_valid_pin("123") == False  # Too short
        assert is_valid_pin("123456789") == False  # Too long
        assert is_valid_pin("abcd") == False  # Non-numeric
        assert is_valid_pin("") == False
    
    def test_parse_stok_to_int(self):
        """Test stok parsing"""
        # Valid inputs
        assert parse_stok_to_int("123") == 123
        assert parse_stok_to_int("0") == 0
        assert parse_stok_to_int("  456  ") == 456
        
        # Invalid inputs
        assert parse_stok_to_int("Tidak Ditemukan") == None
        assert parse_stok_to_int(None) == None
        assert parse_stok_to_int("") == None
        assert parse_stok_to_int("abc") == None
    
    def test_parse_inputan_to_int(self):
        """Test inputan parsing dari format '28 Tabung'"""
        # Valid inputs
        assert parse_inputan_to_int("28 Tabung") == 28
        assert parse_inputan_to_int("0 Tabung") == 0
        assert parse_inputan_to_int("123 tabung") == 123
        
        # Invalid inputs
        assert parse_inputan_to_int("Tidak Ditemukan") == None
        assert parse_inputan_to_int(None) == None
        assert parse_inputan_to_int("Tabung") == None  # No number

class TestSecurityValidator:
    """Test cases untuk security validator"""
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        validator = SecurityValidator()
        
        # Valid inputs
        assert validator.sanitize_input("normal input") == "normal input"
        assert validator.sanitize_input("  spaced  ") == "spaced"
        
        # Dangerous inputs (should be cleaned)
        assert validator.sanitize_input("input<script>alert('xss')</script>") == "inputalertxss"
        assert validator.sanitize_input("input\"quotes\"") == "inputquotes"
        assert validator.sanitize_input("input'; DROP TABLE") == "input DROP TABLE"
        
        # Non-string inputs
        assert validator.sanitize_input(None) == ""
        assert validator.sanitize_input(123) == ""
    
    def test_validate_and_encrypt_pin(self):
        """Test PIN validation dengan security checks"""
        validator = SecurityValidator()
        
        # Valid PINs
        assert validator.validate_and_encrypt_pin("1234") == True
        assert validator.validate_and_encrypt_pin("567890") == True
        
        # Invalid PINs - should raise ValidationError
        with pytest.raises(Exception):  # Should raise ValidationError
            validator.validate_and_encrypt_pin("123")  # Too short
        
        with pytest.raises(Exception):
            validator.validate_and_encrypt_pin("abcd")  # Non-numeric
        
        with pytest.raises(Exception):
            validator.validate_and_encrypt_pin("")  # Empty
