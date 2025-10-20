"""
Validation functions untuk data dan input
File ini berisi semua fungsi validasi yang diperlukan
"""
import re

def is_valid_email(username):
    """Validasi email sederhana"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", username) is not None

def is_valid_phone(username):
    """Validasi nomor HP: hanya angka, panjang 10-15 digit, boleh leading zero"""
    return username.isdigit() and 10 <= len(username) <= 15 and (username.startswith('08') or username.startswith('628'))

def is_valid_pin(pin):
    """Validasi PIN"""
    return pin.isdigit() and 4 <= len(pin) <= 8

def parse_stok_to_int(stok_str):
    """Convert stok to integer"""
    if stok_str in ["Tidak Ditemukan", None, ""]:
        return None
    try:
        return int(re.findall(r'\d+', str(stok_str))[0])
    except:
        return None

def parse_inputan_to_int(inputan_str):
    """Convert inputan to integer (extract from '28 Tabung')"""
    if inputan_str in ["Tidak Ditemukan", None, ""]:
        return None
    try:
        return int(re.findall(r'\d+', str(inputan_str))[0])
    except:
        return None
