"""
Constants dan konfigurasi untuk automation script SnapFlux
File ini berisi semua konstanta, URL, dan konfigurasi yang digunakan di seluruh aplikasi
"""
import os

# ========== KONFIGURASI URL ==========
LOGIN_URL = "https://subsiditepatlpg.mypertamina.id/merchant-login"

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

# ========== KONFIGURASI EXCEL ==========
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
