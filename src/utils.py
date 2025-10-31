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
            print("\n🎯 === MENU UTAMA SNAPFLUX V2.0 ====")
            print("Silakan pilih fitur yang ingin digunakan:")
            print("1. Check Stok")
            print("2. Batalkan Inputan")
            print("3. Catat Penjualan")
            print("(Otomatis pilih 1 jika tidak ada input dalam 15 detik)")
            
            menu_input = input_with_timeout("Pilihan Anda (1/2/3): ", 15).strip()
            
            if not menu_input:
                print("⏭️ User tidak input menu - akan menggunakan Check Stok (default)")
                return 1
            
            if menu_input not in ['1', '2', '3']:
                print("❌ Pilihan tidak valid! Silakan masukkan 1, 2, atau 3")
                continue
            
            choice = int(menu_input)
            
            if choice == 1:
                print("✅ Dipilih: Check Stok")
                return 1
            elif choice == 2:
                print("✅ Dipilih: Batalkan Inputan")
                return 2
            elif choice == 3:
                print("✅ Dipilih: Catat Penjualan")
                return 3
                
        except Exception as e:
            print(f"❌ Error input menu: {str(e)}")
            continue

def run_catat_penjualan(accounts, selected_date=None):
    """
    ============================================
    FUNGSI CATAT PENJUALAN - PHASE 1
    ============================================
    
    Fungsi untuk menjalankan fitur Catat Penjualan yang melakukan:
    1. Login otomatis ke setiap akun merchant
    2. Navigasi ke menu "Catat Penjualan" (bukan Laporan Penjualan)
    3. Mengambil data penjualan untuk dicatat
    4. Menampilkan hasil di terminal
    
    Args:
        accounts (list): List akun merchant (nama, username, pin)
        selected_date (datetime): Tanggal yang dipilih user untuk filter (optional)
    
    Returns:
        None: Menampilkan hasil langsung di terminal
    """
    print(f"\n🚀 Memulai proses Catat Penjualan...")
    
    # Tampilkan informasi mode operasi
    if selected_date:
        print(f"📅 Mode: Dengan filter tanggal {selected_date.strftime('%d %B %Y')}")
    else:
        print(f"📅 Mode: TANPA filter tanggal spesifik")
    
    # Untuk Catat Penjualan, paksa GUI (headless False) agar captcha & UI interaktif
    try:
        from .config_manager import config_manager
        config_manager.config['headless_mode'] = False
        headless_mode = False
    except ImportError:
        headless_mode = False
    
    print("🖥️ Browser akan berjalan dengan GUI visible (dipaksa untuk Catat Penjualan)")
    
    # Inisialisasi tracking
    total_start = time.time()
    rekap = {
        'sukses': [],
        'gagal_login': [],
        'gagal_navigasi': [],
        'gagal_waktu': [],
        'gagal_masuk_akun': [],
        'gagal_masuk_akun_count': 0
    }
    
    # Loop pemrosesan setiap akun
    for account_index, (nama, username, pin) in enumerate(accounts):
        print(f"\n{'='*60}")
        print(f"🔄 Memproses akun: {username} ({nama})")
        print(f"{'='*60}")
        
        akun_start = time.time()
        driver = None
        
        try:
            # === TAHAP 1: LOGIN ===
            print(f"🔐 Login untuk akun {username}...")
            from .login_handler import login_direct
            login_result = login_direct(username, pin)
            driver = login_result[0]
            login_info = login_result[1]
            
            # Track gagal masuk akun
            if login_info['gagal_masuk_akun']:
                rekap['gagal_masuk_akun'].append((username, f"Gagal Masuk Akun (retry berhasil)"))
                rekap['gagal_masuk_akun_count'] += login_info['count']
                print(f"📊 Gagal Masuk Akun terdeteksi untuk {username}")
            
            if not driver:
                print(f"❌ Login gagal untuk akun {username}")
                rekap['gagal_login'].append((username, "Login gagal"))
                continue
            
            print(f"✅ Login berhasil untuk {username}")
            time.sleep(0.5)  # Delay untuk stabilitas
            

            # === TAHAP 2: NAVIGASI KE CATAT PENJUALAN ===
            print(f"📝 Navigasi ke Catat Penjualan untuk {username}...")
            
            # Import fungsi navigasi
            from .navigation_handler import click_catat_penjualan_direct
            catat_success = click_catat_penjualan_direct(driver)
            
            if not catat_success:
                print(f"❌ Gagal navigasi ke Catat Penjualan untuk {username}")
                rekap['gagal_navigasi'].append((username, "Gagal navigasi ke Catat Penjualan"))
                continue
            
            print("✅ Berhasil navigasi ke Catat Penjualan!")
            
            # === TAHAP 3: BACA NIK DAN ISI FORM ===
            print(f"📋 Membaca daftar NIK dari Excel...")
            
            from .data_extractor import read_nik_from_excel, fill_nik_form_and_continue
            nik_list = read_nik_from_excel()
            
            if not nik_list:
                print(f"❌ Gagal membaca NIK dari Excel untuk {username}")
                rekap['gagal_navigasi'].append((username, "Gagal membaca NIK dari Excel"))
                continue
            
            print(f"✅ Berhasil membaca {len(nik_list)} NIK dari Excel")
            
            # === TAHAP 4-6: LOOP SEMUA NIK (UNIQUE, TANPA LIMIT) ===
            print(f"📝 Mengisi form NIK untuk {username} (loop semua NIK)...")
            
            # === DEBUG SELECTOR PADA CATAT PENJUALAN ===
            print("\n🧭 === DEBUG SELECTOR PADA CATAT PENJUALAN ===")
            try:
                from selenium.webdriver.common.by import By as _By
                try:
                    _el = driver.find_element(_By.XPATH, "//*[contains(text(), 'Catat Penjualan')]")
                    _text = (_el.text or '').strip()
                    print(f"✅ Ditemukan 'Catat Penjualan' | Text='{_text}' | Tag={_el.tag_name} | Class='{_el.get_attribute('class')}' | ID='{_el.get_attribute('id')}'")
                    try:
                        _xpath = driver.execute_script("""
                            function absoluteXPath(el){ if(el.id) return '//*[@id="'+el.id+'"]';
                              const parts=[]; while(el && el.nodeType===1){ let ix=0, sib=el.previousSibling; while(sib){ if(sib.nodeType===1 && sib.nodeName===el.nodeName) ix++; sib=sib.previousSibling; }
                              parts.unshift(el.nodeName.toLowerCase()+'['+(ix+1)+']'); el=el.parentNode; } return '//'+parts.join('/'); }
                            return absoluteXPath(arguments[0]);
                        """, _el)
                        _css = driver.execute_script("""
                            function cssPath(el){ if (!(el instanceof Element)) return; const path=[]; while (el.nodeType===1){ let selector=el.nodeName.toLowerCase(); if (el.id){ selector+='#'+el.id; path.unshift(selector); break; } else { let sib=el, nth=1; while (sib=sib.previousElementSibling){ if (sib.nodeName.toLowerCase()==selector) nth++; } selector += ':nth-of-type('+nth+')'; path.unshift(selector); el=el.parentNode; } } return path.join(' > '); }
                            return cssPath(arguments[0]);
                        """, _el)
                        print(f"🔗 Suggested XPath [Catat Penjualan]: {_xpath}")
                        print(f"🔗 Suggested CSS   [Catat Penjualan]: {_css}")
                    except Exception:
                        pass
                except Exception:
                    print("❌ Elemen 'Catat Penjualan' belum ditemukan saat debug")
            except Exception as _e_dbg:
                print(f"⚠️ Gagal mencetak debug selector: {str(_e_dbg)}")
            
            # Persistent pointer start (per username)
            try:
                from .state_manager import get_next_index, advance_next_index
                start_index = get_next_index(username, len(nik_list))
                print(f"🧭 Start index persisten untuk {username}: {start_index}")
            except Exception:
                start_index = account_index % len(nik_list)
                advance_next_index = None
                print(f"🧭 Start index fallback untuk {username}: {start_index}")

            used_indices = set()
            current_index = start_index
            tx_done = 0
            
            from .data_extractor import click_cek_pesanan, click_proses_penjualan
            from .data_extractor import wait_for_captcha_and_success, click_kembali_ke_halaman_utama
            from .navigation_handler import click_catat_penjualan_direct as _reopen_catat
            
            while len(used_indices) < len(nik_list):
                # Cari index NIK yang belum dipakai
                while current_index in used_indices:
                    current_index = (current_index + 1) % len(nik_list)
                nik_index = current_index
                used_indices.add(nik_index)
                
                print(f"🧾 Transaksi ke-{tx_done+1} dari {len(nik_list)} | NIK index: {nik_index} | NIK: {nik_list[nik_index]}")
                
                # Isi form NIK
                form_result = fill_nik_form_and_continue(driver, nik_list, nik_index)
                # Advance persistent pointer after each attempt
                try:
                    if advance_next_index:
                        advance_next_index(username, len(nik_list), 1)
                except Exception:
                    pass
                if form_result in ("RETRY_NEXT_NIK", "REOPENED_AFTER_TUTUP"):
                    # Kasus tertangani (popup TUTUP / batas kewajaran + Ganti Pelanggan) — jangan tandai gagal
                    current_index = (current_index + 1) % len(nik_list)
                    continue
                if not form_result:
                    print(f"❌ Gagal mengisi form NIK (index {nik_index}) untuk {username}")
                    rekap['gagal_navigasi'].append((username, f"Gagal isi NIK idx {nik_index}"))
                    current_index = (current_index + 1) % len(nik_list)
                    continue
                
                # CEK PESANAN
                print("🧾 Melanjutkan: klik CEK PESANAN...")
                if not click_cek_pesanan(driver):
                    print(f"❌ Gagal klik CEK PESANAN untuk {username}")
                    rekap['gagal_navigasi'].append((username, "Gagal klik CEK PESANAN"))
                    current_index = (current_index + 1) % len(nik_list)
                    continue
                
                # PROSES PENJUALAN
                print("🧾 Di halaman Cek Penjualan: klik PROSES PENJUALAN...")
                if not click_proses_penjualan(driver):
                    print(f"❌ Gagal klik PROSES PENJUALAN untuk {username}")
                    rekap['gagal_navigasi'].append((username, "Gagal klik PROSES PENJUALAN"))
                    current_index = (current_index + 1) % len(nik_list)
                    continue
                
                # CAPTCHA & SUCCESS
                print("🧩 Menunggu user menyelesaikan captcha dan halaman sukses...")
                if not wait_for_captcha_and_success(driver, max_wait_seconds=180):
                    print(f"❌ Tidak terdeteksi halaman sukses untuk {username} (mungkin captcha belum selesai)")
                    rekap['gagal_navigasi'].append((username, "Captcha/sukses tidak terdeteksi"))
                    current_index = (current_index + 1) % len(nik_list)
                    continue
                
                # Kembali ke halaman utama dan buka lagi Catat Penjualan
                if not click_kembali_ke_halaman_utama(driver):
                    print(f"⚠️ Tidak dapat kembali ke halaman utama untuk {username}")
                    break
                
                print("🏠 Berhasil kembali ke halaman utama. Membuka Catat Penjualan lagi...")
                _reopen_catat(driver)
                
                tx_done += 1
                current_index = (current_index + 1) % len(nik_list)
            
            print(f"✅ Loop transaksi selesai untuk {username}: {tx_done}/{len(nik_list)} transaksi")
            rekap['sukses'].append(username)
            
            time.sleep(0.5)  # Delay untuk stabilitas
            
        except Exception as e:
            print(f"❌ Error dalam proses untuk akun {username}: {str(e)}")
            import logging
            logger = logging.getLogger('automation')
            logger.error(f"Error untuk akun {username}: {str(e)}", exc_info=True)
            rekap['gagal_navigasi'].append((username, f"Error: {str(e)}"))
        
        finally:
            # Cleanup driver
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        akun_end = time.time()
        akun_duration = akun_end - akun_start
        print(f"⏱️ Waktu proses akun {username}: {akun_duration:.2f} detik")
        
        # Track timeout jika proses terlalu lama (>60 detik)
        if akun_duration > 60:
            rekap['gagal_waktu'].append((username, f"Timeout - proses terlalu lama ({akun_duration:.1f} detik)"))
            print(f"⚠️ Timeout terdeteksi untuk {username}: {akun_duration:.1f} detik")
        
        # Delay antar akun untuk menghindari rate limiting
        if account_index < len(accounts) - 1:
            print("⏳ Menunggu sebentar untuk menghindari rate limiting...")
            if (account_index + 1) % 5 == 0:
                print("🚨 Delay ekstra setiap 5 akun...")
                time.sleep(8.0)
            else:
                time.sleep(4.0)
    
    # === REKAP AKHIR CATAT PENJUALAN ===
    total_end = time.time()
    total_duration = total_end - total_start
    
    print(f"\n{'='*60}")
    print(f"📊 === REKAP AKHIR CATAT PENJUALAN ===")
    print(f"{'='*60}")
    print(f"⏱️ Total waktu proses: {total_duration:.2f} detik")
    print(f"📈 Total akun diproses: {len(accounts)}")
    print(f"✅ Berhasil: {len(rekap['sukses'])} akun")
    print(f"❌ Gagal Login: {len(rekap['gagal_login'])} akun")
    print(f"❌ Gagal Navigasi: {len(rekap['gagal_navigasi'])} akun")
    print(f"❌ Timeout: {len(rekap['gagal_waktu'])} akun")
    print(f"🔄 Gagal Masuk Akun (retry): {len(rekap['gagal_masuk_akun'])} akun")
    
    if rekap['sukses']:
        print(f"\n✅ Akun yang berhasil:")
        for username in rekap['sukses']:
            print(f"   - {username}")
    
    if rekap['gagal_login']:
        print(f"\n❌ Akun yang gagal login:")
        for username, reason in rekap['gagal_login']:
            print(f"   - {username}: {reason}")
    
    if rekap['gagal_navigasi']:
        print(f"\n❌ Akun yang gagal navigasi:")
        for username, reason in rekap['gagal_navigasi']:
            print(f"   - {username}: {reason}")
    
    if rekap['gagal_waktu']:
        print(f"\n⚠️ Akun yang timeout:")
        for username, reason in rekap['gagal_waktu']:
            print(f"   - {username}: {reason}")
    
    if rekap['gagal_masuk_akun']:
        print(f"\n🔄 Akun dengan retry berhasil:")
        for username, reason in rekap['gagal_masuk_akun']:
            print(f"   - {username}: {reason}")
    
    print(f"\n🎉 Proses Catat Penjualan selesai!")
    print(f"👋 Terima kasih!")

def run_catat_penjualan_coming_soon():
    """
    ============================================
    FUNGSI CATAT PENJUALAN - COMING SOON (FALLBACK)
    ============================================
    
    Fungsi fallback jika fitur Catat Penjualan belum siap.
    """
    print("\n" + "="*60)
    print("🚀 === FITUR CATAT PENJUALAN - COMING SOON ===")
    print("="*60)
    
    print("\n📝 FITUR YANG AKAN TERSEDIA:")
    print("┌─────────────────────────────────────────────────────────┐")
    print("│ 1. 📊 Input Data Penjualan Manual                      │")
    print("│ 2. 📋 Form Input Penjualan Harian                      │")
    print("│ 3. 🔄 Sync Data dengan Sistem Pertamina                │")
    print("│ 4. 📈 Dashboard Penjualan Real-time                    │")
    print("│ 5. 📱 Mobile-friendly Interface                        │")
    print("│ 6. 🔔 Notifikasi Penjualan                             │")
    print("│ 7. 📊 Laporan Penjualan Otomatis                       │")
    print("│ 8. 💾 Backup Data Penjualan                            │")
    print("└─────────────────────────────────────────────────────────┘")
    
    print("\n🎯 MANFAAT FITUR CATAT PENJUALAN:")
    print("✅ Mencatat penjualan secara manual dan otomatis")
    print("✅ Monitoring penjualan real-time")
    print("✅ Integrasi dengan sistem Pertamina")
    print("✅ Laporan penjualan yang komprehensif")
    print("✅ Notifikasi untuk penjualan penting")
    print("✅ Backup data penjualan otomatis")
    
    print("\n⏰ TIMELINE PENGEMBANGAN:")
    print("📅 Phase 1: Form Input Manual (2 minggu)")
    print("📅 Phase 2: Dashboard Real-time (3 minggu)")
    print("📅 Phase 3: Mobile Interface (2 minggu)")
    print("📅 Phase 4: Integration & Testing (2 minggu)")
    print("📅 Phase 5: Release v2.1 (1 minggu)")
    
    print("\n🔔 NOTIFIKASI UPDATE:")
    print("📧 Email: admin@snapflux.com")
    print("📱 WhatsApp: +62-xxx-xxx-xxxx")
    print("🌐 Website: https://snapflux.com/updates")
    
    print("\n💡 FITUR SEMENTARA:")
    print("🔧 Gunakan fitur 'Check Stok' untuk monitoring penjualan")
    print("📊 Data tersimpan di folder 'results'")
    print("📋 Export data ke Excel untuk analisis")
    
    print("\n🎉 TERIMA KASIH!")
    print("Kami sedang bekerja keras untuk menghadirkan fitur terbaik")
    print("untuk kemudahan operasional bisnis Anda.")
    
    print("\n" + "="*60)
    print("🚀 Snapflux v2.0 - Coming Soon Features")
    print("="*60)
    
    # Tampilkan menu kembali
    print("\n🔄 Kembali ke menu utama...")
    input("Tekan Enter untuk kembali ke menu utama...")

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
            
            # Debug: Tampilkan hasil parsing
            print(f"🔍 Debug parsing: day={day}, month={month}, year={year}")
            
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
                # Validasi tambahan: pastikan tanggal yang dibuat sesuai dengan input
                if selected_date.day != day or selected_date.month != month or selected_date.year != year:
                    print(f"❌ Error: Tanggal yang dibuat tidak sesuai dengan input!")
                    print(f"   Input: day={day}, month={month}, year={year}")
                    print(f"   Hasil: day={selected_date.day}, month={selected_date.month}, year={selected_date.year}")
                    continue
            except ValueError as ve:
                print(f"❌ Tanggal tidak valid! {str(ve)}")
                continue
            except Exception as e:
                print(f"❌ Error membuat tanggal: {str(e)}")
                continue
            
            # Validasi final: tampilkan tanggal yang akan digunakan
            from .constants import BULAN_ID
            print(f"✅ Tanggal berhasil di-parse:")
            print(f"   📅 Format lengkap: {selected_date.strftime('%d %B %Y')}")
            print(f"   🔢 Day: {selected_date.day}, Month: {selected_date.month}, Year: {selected_date.year}")
            if 1 <= selected_date.month <= 12:
                bulan_indonesia = BULAN_ID[selected_date.month]
                print(f"   📝 Nama bulan (Indonesia): {bulan_indonesia}")
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