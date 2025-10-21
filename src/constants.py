"""
Constants dan konfigurasi untuk automation script SnapFlux
File ini berisi semua konstanta, URL, dan konfigurasi yang digunakan di seluruh aplikasi
"""
import os
from datetime import datetime

# Import config manager untuk enhanced configuration (backward compatible)
try:
    from .config_manager import config_manager
    USE_ENHANCED_CONFIG = True
except ImportError:
    USE_ENHANCED_CONFIG = False

# ========== KONFIGURASI URL ==========
LOGIN_URL = "https://subsiditepatlpg.mypertamina.id/merchant-login"

# Enhanced configuration dengan fallback ke hardcoded values
def get_config_value(key: str, fallback_value):
    """
    Get configuration value dari enhanced config manager atau fallback ke hardcoded value
    Maintains backward compatibility dengan existing code
    """
    if USE_ENHANCED_CONFIG:
        return config_manager.get(key, fallback_value)
    return fallback_value

# ========== KONFIGURASI PATH DIREKTORI ==========
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AKUN_DIR = os.path.join(BASE_DIR, 'akun')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'automation.log')

# ========== KONSTANTA BULAN INDONESIA ==========
BULAN_ID = [
    '', 'JANUARI', 'FEBRUARI', 'MARET', 'APRIL', 'MEI', 'JUNI',
    'JULI', 'AGUSTUS', 'SEPTEMBER', 'OKTOBER', 'NOVEMBER', 'DESEMBER'
]

BULAN_SINGKAT = [
    '', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
    'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'
]

# ========== KONFIGURASI CHROME ==========
CHROME_BINARY = r"D:\edi\Programing\Snapflux v2\chrome\Chromium\bin\chrome.exe"
CHROMEDRIVER_PATH = r"D:\edi\Programing\Snapflux v2\chrome\chromedriver.exe"

# ========== KONFIGURASI TIMING ==========
DEFAULT_DELAY = 2.0
RETRY_DELAY = 2.0
ERROR_DELAY = 1.0
INTER_ACCOUNT_DELAY = 2.5
MAX_RETRIES = 3

# ========== KONFIGURASI BROWSER ==========
HEADLESS_MODE = True
PAGE_LOAD_TIMEOUT = 20
IMPLICIT_WAIT = 5

# Enhanced configuration values dengan environment/fallback support
# Usage: get_config_value('config_key', fallback_value)
# Jika enhanced config tersedia, akan menggunakan environment variables atau config.yaml
# Jika tidak, tetap menggunakan hardcoded values di atas (backward compatibility)

# ========== FUNGSI GENERATE EXCEL DYNAMIC ==========
def get_excel_filename_dynamic(selected_date=None):
    """
    Generate nama file Excel dengan format: Data_Transaksi_Pangkalan_SnapFlux_tahun-bulan-tanggal.xlsx
    DEPRECATED - Gunakan get_master_filename() untuk sistem incremental
    """
    if selected_date:
        year = selected_date.year
        month = selected_date.month
        day = selected_date.day
    else:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
    
    return f"Data_Transaksi_Pangkalan_SnapFlux_{year}-{month:02d}-{day:02d}.xlsx"

def get_master_filename(selected_date=None):
    """
    Generate nama file Excel master dengan format: DATA_SNAPFLUX_MASTER_YYYY_BULAN.xlsx
    File master incremental untuk sistem harian yang optimal
    """
    if selected_date:
        year = selected_date.year
        month = selected_date.month
        month_name = BULAN_ID[month].upper()
    else:
        now = datetime.now()
        year = now.year
        month = now.month
        month_name = BULAN_ID[month].upper()
    
    return f"DATA_SNAPFLUX_MASTER_{year}_{month_name}.xlsx"

def get_sheet_name_dynamic(selected_date=None):
    """
    Generate nama sheet berdasarkan bulan saat ini
    """
    if selected_date:
        month = selected_date.month
        year = selected_date.year
    else:
        month = datetime.now().month
        year = datetime.now().year
    
    return f"{BULAN_ID[month].upper()}_{year}"

# ========== KONFIGURASI EXCEL (DEPRECATED - gunakan fungsi dynamic di atas) ==========
EXCEL_FILENAME_PIVOT = "DATA_TRANSAKSI_SNAPFLUX_HISTORIS_PIVOT.xlsx"
SHEET_NAME_PIVOT = "Pivot View"

# ========== KONFIGURASI WARNI HARI ==========
DAY_COLORS = {
    0: "FFE6B3",  # Senin - Jingga muda
    1: "FFFFB3",  # Selasa - Kuning muda  
    2: "FFB3B3",  # Rabu - Merah muda
    3: "B3FFB3",  # Kamis - Hijau muda
    4: "B3E6FF",  # Jumat - Biru muda
    5: "E6B3FF",  # Sabtu - Ungu muda
    6: "FFCCFF"   # Minggu - Pink muda
}
