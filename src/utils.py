"""
Utility functions and helpers
"""
import os
import time
import re
import pandas as pd
import requests
import logging
import queue
import threading
from datetime import datetime
from collections import Counter
from logging.handlers import RotatingFileHandler

# Config values (hardcoded to avoid import issues)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AKUN_DIR = os.path.join(BASE_DIR, 'akun')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'automation.log')

PROXY_CONFIG = {
    'host': '43.159.20.117',
    'port': '12233',
    'username': 'user-EdiFOSPr-region-sg',
    'password': 'FOS5610Proxy908',
    'auth_username': 'EdiFOSPr',
    'auth_password': 'FOS5610Proxy908'
}

BULAN_ID = [
    '', 'JANUARI', 'FEBRUARI', 'MARET', 'APRIL', 'MEI', 'JUNI',
    'JULI', 'AGUSTUS', 'SEPTEMBER', 'OKTOBER', 'NOVEMBER', 'DESEMBER'
]

logger = logging.getLogger('automation')

def setup_logging():
    """Setup logging configuration"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def check_bandwidth():
    """Cek bandwidth proxy di https://faeyzaofficialstore.com/bandwidth"""
    print("\n🌐 Mengecek bandwidth proxy...")
    url = "https://faeyzaofficialstore.com/bandwidth"
    proxy = {
        'http': f'http://{PROXY_CONFIG["username"]}:{PROXY_CONFIG["password"]}@{PROXY_CONFIG["host"]}:{PROXY_CONFIG["port"]}',
        'https': f'http://{PROXY_CONFIG["username"]}:{PROXY_CONFIG["password"]}@{PROXY_CONFIG["host"]}:{PROXY_CONFIG["port"]}',
    }
    try:
        resp = requests.get(url, proxies=proxy, timeout=15, 
                          auth=(PROXY_CONFIG["auth_username"], PROXY_CONFIG["auth_password"]))
        if resp.status_code == 200:
            print("✅ Bandwidth proxy terhubung!")
            print(resp.text[:500])
        else:
            print(f"❌ Gagal cek bandwidth, status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error cek bandwidth: {e}")

def is_valid_email(username):
    """Validasi email sederhana"""
    return re.match(r"[^@]+@[^@]+\.[^@]+", username) is not None

def is_valid_phone(username):
    """Validasi nomor HP: hanya angka, panjang 10-15 digit, boleh leading zero"""
    return username.isdigit() and 10 <= len(username) <= 15 and (username.startswith('08') or username.startswith('628'))

def is_valid_pin(pin):
    """Validasi PIN"""
    return pin.isdigit() and 4 <= len(pin) <= 8

def load_accounts_from_excel(filename):
    """Load accounts from Excel file with validation"""
    df = pd.read_excel(filename, dtype={"Nama": str, "Username": str, "Password": str})
    valid_accounts = []
    
    for _, row in df.iterrows():
        nama = str(row['Nama']).strip()
        username = str(row['Username']).strip()
        pin = str(row['Password']).strip()
        
        # Username valid jika email atau nomor HP
        if not (is_valid_email(username) or is_valid_phone(username)):
            logger.warning(f"Invalid username (bukan email/HP): {username}")
            continue
        if not is_valid_pin(pin):
            logger.warning(f"Invalid PIN: {pin} for {username}")
            continue
        valid_accounts.append((nama, username, pin))
    
    if not valid_accounts:
        raise ValueError("No valid accounts found in Excel file!")
    
    return valid_accounts

def print_account_stats(accounts):
    """Print account statistics"""
    usernames = [acc[1] for acc in accounts]
    total = len(usernames)
    unique = len(set(usernames))
    
    print(f"\nTotal akun: {total}")
    print(f"Akun unik: {unique}")
    
    if total != unique:
        dupe = [u for u, c in Counter(usernames).items() if c > 1]
        print(f"Username duplikat: {dupe}")
    else:
        print("Tidak ada username yang duplikat.")

def input_with_timeout(prompt, timeout):
    """Input with timeout functionality"""
    q = queue.Queue()
    
    def inner():
        try:
            q.put(input(prompt))
        except Exception:
            q.put('')
    
    t = threading.Thread(target=inner)
    t.daemon = True
    t.start()
    
    try:
        return q.get(timeout=timeout)
    except queue.Empty:
        return ''

def get_date_input():
    """Minta input tanggal dari user dengan validasi"""
    while True:
        try:
            print("\n📅 === FILTER TANGGAL LAPORAN PENJUALAN ===")
            print("Masukkan tanggal yang ingin diambil datanya (format: DD/MM/YYYY)")
            print("Contoh: 19/07/2025")
            print("Atau tekan Enter tanpa input untuk LEWATI filter tanggal")
            print("(Otomatis lewati filter tanggal jika tidak ada input dalam 15 detik)")
            
            date_input = input_with_timeout("Tanggal: ", 15).strip()
            
            if not date_input:
                print("⏭️ User tidak input tanggal - akan lewati fungsi klik tanggal")
                print("📅 Data akan diambil tanpa filter tanggal spesifik")
                return None
            
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_input):
                print("❌ Format tanggal salah! Gunakan format DD/MM/YYYY")
                continue
            
            day, month, year = map(int, date_input.split('/'))
            
            if year < 2020 or year > 2030:
                print("❌ Tahun tidak valid! Gunakan tahun antara 2020-2030")
                continue
            if month < 1 or month > 12:
                print("❌ Bulan tidak valid!")
                continue
            if day < 1 or day > 31:
                print("❌ Hari tidak valid!")
                continue
            
            try:
                selected_date = datetime(year, month, day)
            except Exception:
                print("❌ Tanggal tidak valid!")
                continue
            
            print(f"✅ Menggunakan tanggal: {selected_date.strftime('%d %B %Y')}")
            return selected_date
            
        except Exception as e:
            print(f"❌ Error input tanggal: {str(e)}")

def get_excel_filename(selected_date=None):
    """Generate nama file Excel sesuai format"""
    if selected_date:
        tgl = selected_date.day
        bln = BULAN_ID[selected_date.month]
        thn = selected_date.year
        return f"DATA TRANSAKSI SNAPFLUX PANGKALAN {tgl} {bln} {thn}.xlsx"
    else:
        now = datetime.now()
        return f"DATA TRANSAKSI SNAPFLUX PANGKALAN TANPA FILTER TANGGAL {now.strftime('%d %B %Y')}.xlsx"

def save_to_excel_new_format(nama_pangkalan, tanggal_check, stok_awal, total_inputan, status, selected_date=None):
    """Simpan data ke Excel dengan format baru"""
    filename = get_excel_filename(selected_date)
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        print(f"💾 Menyimpan data ke Excel ({filename})...")
        
        # Siapkan data dengan format baru
        data = {
            'NAMA PANGKALAN': [nama_pangkalan],
            'TANGGAL CHECK': [tanggal_check],
            'STOK AWAL': [stok_awal or "Tidak Ditemukan"],
            'TOTAL INPUTAN': [total_inputan or "Tidak Ditemukan"],
            'STATUS': [status]
        }
        df_new = pd.DataFrame(data)
        
        if os.path.exists(filepath):
            df_existing = pd.read_excel(filepath)
            
            # Tambahkan data baru ke DataFrame yang sudah ada
            df_existing = pd.concat([df_existing, df_new], ignore_index=True)
            
            df_existing.to_excel(filepath, index=False)
            print(f"✅ Data berhasil disimpan ke: {filepath}")
            print("\n📋 Hasil scraping:")
            print(df_new.to_string(index=False))
        else:
            df_new.to_excel(filepath, index=False)
            print(f"✅ Data berhasil disimpan ke: {filepath}")
            print("\n📋 Hasil scraping:")
            print(df_new.to_string(index=False))
    except Exception as e:
        print(f"❌ Error saat menyimpan: {str(e)}")
        logger.error(f"Error saving to Excel: {str(e)}", exc_info=True)

def print_final_summary(rekap, accounts, akun_durations, total_start):
    """Print final summary of the scraping process"""
    total_end = time.time()
    total_duration = total_end - total_start
    rata2 = (sum(akun_durations) / len(akun_durations)) if akun_durations else 0
    
    print(f"\n✅ Semua akun selesai diproses!")
    print(f"⏱️ Total waktu proses semua akun: {total_duration:.2f} detik")
    print(f"⏱️ Rata-rata waktu proses per akun: {rata2:.2f} detik")
    
    # Rekap hasil akhir
    print("\n===== REKAPITULASI HASIL AKHIR =====")
    print(f"Sukses: {len(rekap['sukses'])} akun")
    if rekap['sukses']:
        for uname in rekap['sukses']:
            print(f"  ✅ {uname}")
    
    print(f"Gagal Login: {len(rekap['gagal_login'])} akun")
    if rekap['gagal_login']:
        for uname, reason in rekap['gagal_login']:
            print(f"  ❌ {uname}: {reason}")
    
    print(f"Gagal Navigasi/Data Penjualan: {len(rekap['gagal_navigasi'])} akun")
    if rekap['gagal_navigasi']:
        for uname, reason in rekap['gagal_navigasi']:
            print(f"  ⚠️ {uname}: {reason}")
    
    print(f"Gagal Ambil Waktu/Customer: {len(rekap['gagal_waktu'])} akun")
    if rekap['gagal_waktu']:
        for uname, reason in rekap['gagal_waktu']:
            print(f"  ⚠️ {uname}: {reason}")
    
    print(f"Gagal Ambil Stok: {len(rekap['gagal_stok'])} akun")
    if rekap['gagal_stok']:
        for uname, reason in rekap['gagal_stok']:
            print(f"  ⚠️ {uname}: {reason}")
    
    print(f"Error Lain: {len(rekap['error_lain'])} akun")
    if rekap['error_lain']:
        for uname, reason in rekap['error_lain']:
            print(f"  ❌ {uname}: {reason}")
    
    print("===== END REKAP =====\n")
    
    # Summary statistik
    total_accounts = len(accounts)
    success_rate = (len(rekap['sukses']) / total_accounts) * 100 if total_accounts > 0 else 0
    print(f"📊 STATISTIK FINAL:")
    print(f"Total Akun: {total_accounts}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Akun yang berhasil diproses: {len(rekap['sukses'])}")
    print(f"Akun yang gagal: {total_accounts - len(rekap['sukses'])}")