"""
Utility functions dan helper functions untuk automation script
File ini berisi fungsi-fungsi bantuan untuk file handling, validasi, dan logging
"""
import os
import time
import re
import pandas as pd
import logging
import queue
import threading
from datetime import datetime
from collections import Counter
from logging.handlers import RotatingFileHandler

from .constants import BASE_DIR, AKUN_DIR, RESULTS_DIR, LOGS_DIR, LOG_FILE
from .validators import is_valid_email, is_valid_phone, is_valid_pin

# Setup logger untuk tracking error dan informasi debugging
logger = logging.getLogger('automation')

def setup_logging():
    """
    ============================================
    FUNGSI SETUP LOGGING SYSTEM
    ============================================
    
    Fungsi ini mengatur konfigurasi logging untuk sistem automation dengan
    rotating file handler untuk mencegah file log menjadi terlalu besar.
    
    Proses yang dilakukan:
    1. Membuat direktori logs jika belum ada
    2. Set level logging ke DEBUG untuk detail maksimal
    3. Setup rotating file handler dengan batas 2MB per file
    4. Konfigurasi formatter untuk format timestamp dan level
    5. Menambahkan handler ke logger
    
    Konfigurasi logging:
    - Level: DEBUG (detail maksimal)
    - Max file size: 2MB per file
    - Backup count: 3 file backup
    - Encoding: UTF-8 untuk support karakter Indonesia
    - Format: Timestamp + Level + Message
    
    Args:
        None: Menggunakan konfigurasi default
    
    Returns:
        None: Setup logging system
    """
    os.makedirs(LOGS_DIR, exist_ok=True)  # Buat direktori logs jika belum ada
    
    logger.setLevel(logging.DEBUG)  # Set level logging ke DEBUG untuk detail maksimal
    
    # Setup rotating file handler - file log akan di-rotate setiap 2MB
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def load_accounts_from_excel(filename):
    """
    ============================================
    FUNGSI LOAD DATA AKUN DARI FILE EXCEL
    ============================================
    
    Fungsi ini membaca dan memvalidasi data akun merchant dari file Excel
    dengan validasi lengkap untuk memastikan data yang digunakan valid.
    
    Proses yang dilakukan:
    1. Membaca file Excel dengan pandas dengan tipe data string
    2. Loop setiap baris untuk validasi data:
       - Validasi username (harus email atau nomor HP yang valid)
       - Validasi PIN (harus angka 4-8 digit)
       - Strip whitespace dari semua field
    3. Tambahkan akun yang valid ke list
    4. Return list akun yang sudah divalidasi
    
    Format file Excel yang diharapkan:
    - Kolom "Nama": Nama pangkalan merchant
    - Kolom "Username": Email atau nomor HP merchant
    - Kolom "Password": PIN untuk login
    
    Validasi yang dilakukan:
    - Username: Email format atau nomor HP (10-15 digit, awalan 08/628)
    - PIN: Hanya angka, panjang 4-8 digit
    
    Args:
        filename (str): Path ke file Excel yang berisi data akun
    
    Returns:
        list: List tuple berisi (nama, username, pin) untuk akun yang valid
    
    Raises:
        ValueError: Jika tidak ada akun valid ditemukan di file Excel
    """
    # Baca file Excel dengan tipe data yang tepat untuk setiap kolom
    df = pd.read_excel(filename, dtype={"Nama": str, "Username": str, "Password": str})
    valid_accounts = []
    
    # Loop setiap baris dalam Excel untuk validasi dan ekstraksi data
    for _, row in df.iterrows():
        nama = str(row['Nama']).strip()      # Nama pangkalan (strip whitespace)
        username = str(row['Username']).strip()  # Username bisa email atau nomor HP
        pin = str(row['Password']).strip()       # PIN untuk login
        
        # Validasi username - harus berupa email atau nomor HP yang valid
        if not (is_valid_email(username) or is_valid_phone(username)):
            logger.warning(f"Invalid username (bukan email/HP): {username}")
            continue
            
        # Validasi PIN - harus berupa angka dengan panjang 4-8 digit
        if not is_valid_pin(pin):
            logger.warning(f"Invalid PIN: {pin} for {username}")
            continue
            
        # Jika semua validasi passed, tambahkan ke list akun valid
        valid_accounts.append((nama, username, pin))
    
    # Pastikan ada minimal satu akun valid
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

def get_main_menu_input():
    """Menu utama untuk memilih fitur program"""
    while True:
        try:
            print("\n🎯 === MENU UTAMA SNAPFLUX ====")
            print("Silakan pilih fitur yang ingin digunakan:")
            print("1. Check Stok")
            print("2. Batalkan Inputan")
            print("(Otomatis pilih 1 jika tidak ada input dalam 15 detik)")
            
            menu_input = input_with_timeout("Pilihan Anda (1/2): ", 15).strip()
            
            if not menu_input:
                print("⏭️ User tidak input menu - akan menggunakan Check Stok (default)")
                return 1
            
            if menu_input not in ['1', '2']:
                print("❌ Pilihan tidak valid! Silakan masukkan 1 atau 2")
                continue
            
            choice = int(menu_input)
            
            if choice == 1:
                print("✅ Dipilih: Check Stok")
                return 1
            elif choice == 2:
                print("✅ Dipilih: Batalkan Inputan")
                print("🚧 Fitur ini akan segera tersedia!")
                return 2
                
        except Exception as e:
            print(f"❌ Error input menu: {str(e)}")
            continue

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
    
    print(f"Gagal Masuk Akun (dengan retry): {len(rekap['gagal_masuk_akun'])} akun")
    if rekap['gagal_masuk_akun']:
        for uname, reason in rekap['gagal_masuk_akun']:
            print(f"  🔄 {uname}: {reason}")
    
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
    
    # Statistik khusus untuk Gagal Masuk Akun
    if 'gagal_masuk_akun_count' in rekap and rekap['gagal_masuk_akun_count'] > 0:
        print(f"\n🔄 STATISTIK GAGAL MASUK AKUN:")
        print(f"Total kejadian 'Gagal Masuk Akun': {rekap['gagal_masuk_akun_count']}")
        print(f"Akun yang mengalami 'Gagal Masuk Akun': {len(rekap['gagal_masuk_akun'])}")
        print(f"Rata-rata kejadian per akun: {rekap['gagal_masuk_akun_count'] / len(rekap['gagal_masuk_akun']):.1f}")
    
    # Summary error breakdown
    total_errors = (len(rekap['gagal_login']) + len(rekap['gagal_navigasi']) + 
                   len(rekap['gagal_waktu']) + len(rekap['gagal_stok']) + 
                   len(rekap['error_lain']))
    
    if total_errors > 0:
        print(f"\n📋 BREAKDOWN ERROR:")
        print(f"🔐 Gagal Login: {len(rekap['gagal_login'])}")
        print(f"🧭 Gagal Navigasi: {len(rekap['gagal_navigasi'])}")
        print(f"⏰ Timeout: {len(rekap['gagal_waktu'])}")
        print(f"📦 Gagal Ambil Stok: {len(rekap['gagal_stok'])}")
        print(f"❌ Error Lain: {len(rekap['error_lain'])}")
        print(f"🔄 Gagal Masuk Akun (retry): {len(rekap['gagal_masuk_akun'])}")
        
        if 'gagal_masuk_akun_count' in rekap and rekap['gagal_masuk_akun_count'] > 0:
            print(f"\n🔄 DETAIL GAGAL MASUK AKUN:")
            print(f"Total kejadian 'Gagal Masuk Akun': {rekap['gagal_masuk_akun_count']}")
            print(f"Akun yang mengalami 'Gagal Masuk Akun': {len(rekap['gagal_masuk_akun'])}")
            if len(rekap['gagal_masuk_akun']) > 0:
                print(f"Rata-rata kejadian per akun: {rekap['gagal_masuk_akun_count'] / len(rekap['gagal_masuk_akun']):.1f}")