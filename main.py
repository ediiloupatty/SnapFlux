#!/usr/bin/env python3
"""
Main entry point untuk automation script SnapFlux
Script ini mengotomatisasi pengambilan data transaksi dari platform merchant Pertamina
"""
import os
import sys
import time
import random
from datetime import datetime

# Tambahkan direktori src ke path Python agar bisa import module
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import modul yang diperlukan
from src.utils import (
    setup_logging, load_accounts_from_excel, print_account_stats,
    get_main_menu_input, get_date_input, print_final_summary
)
import logging

# Import enhanced configuration (backward compatible)
try:
    from src.config_manager import config_manager
    USE_ENHANCED_CONFIG = True
except ImportError:
    USE_ENHANCED_CONFIG = False

# Setup logger untuk tracking error
logger = logging.getLogger('automation')
from src.driver_setup import setup_driver
from src.login_handler import login_direct
from src.data_extractor import get_stock_value_direct, get_tabung_terjual_direct
from src.navigation_handler import (
    click_laporan_penjualan_direct, find_and_click_laporan_penjualan,
    navigate_to_atur_produk, click_date_elements_direct
)
from src.excel_handler import save_to_excel_pivot_format

def run_batalkan_inputan(accounts, selected_date):
    """
    Fungsi untuk menjalankan fitur Batalkan Inputan
    Melakukan login, navigasi ke Laporan Penjualan, lalu ke Rekap Penjualan,
    dan menampilkan list pembeli di terminal
    """
    print(f"\n🚀 Memulai proses Batalkan Inputan...")
    
    # Tampilkan informasi mode operasi
    if selected_date:
        print(f"📅 Mode: Dengan filter tanggal {selected_date.strftime('%d %B %Y')}")
    else:
        print(f"📅 Mode: TANPA filter tanggal spesifik")
    
    # Check headless mode configuration
    if USE_ENHANCED_CONFIG:
        headless_mode = config_manager.get('headless_mode', True)
    else:
        headless_mode = True  # Default fallback
    
    if headless_mode:
        print("🌐 Browser akan berjalan dalam mode headless")
    else:
        print("🖥️ Browser akan berjalan dengan GUI visible")
    
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
            time.sleep(2.0)  # Delay untuk stabilitas
            
            # === TAHAP 2: NAVIGASI KE LAPORAN PENJUALAN ===
            print(f"📊 Navigasi ke Laporan Penjualan untuk {username}...")
            
            # Coba metode langsung terlebih dahulu
            laporan_success = click_laporan_penjualan_direct(driver)
            
            # Jika gagal, coba metode fallback
            if not laporan_success:
                print("🔄 Mencoba metode fallback navigasi ke Laporan Penjualan...")
                laporan_success = find_and_click_laporan_penjualan(driver)
            
            if not laporan_success:
                print(f"❌ Gagal navigasi ke Laporan Penjualan untuk {username}")
                rekap['gagal_navigasi'].append((username, "Gagal navigasi ke Laporan Penjualan"))
                continue
            
            print("✅ Berhasil navigasi ke Laporan Penjualan!")
            
            # === TAHAP 3: KLIK ELEMEN TANGGAL (Jika User Input Tanggal) ===
            if selected_date:
                print(f"📅 Mengklik elemen tanggal: {selected_date.strftime('%d %B %Y')}")
                date_elements_success = click_date_elements_direct(driver, selected_date)
                
                if date_elements_success:
                    print("✅ Berhasil mengklik elemen tanggal!")
                else:
                    print("⚠️ Gagal mengklik elemen tanggal, lanjut ke tahap berikutnya...")
            
            # === TAHAP 4: NAVIGASI KE REKAP PENJUALAN ===
            print(f"📈 Navigasi ke Rekap Penjualan untuk {username}...")
            
            # Import fungsi yang diperlukan untuk rekap penjualan
            from src.login_handler import click_rekap_penjualan_direct
            rekap_success = click_rekap_penjualan_direct(driver)
            
            if not rekap_success:
                print(f"❌ Gagal navigasi ke Rekap Penjualan untuk {username}")
                rekap['gagal_navigasi'].append((username, "Gagal navigasi ke Rekap Penjualan"))
                continue
            
            print("✅ Berhasil navigasi ke Rekap Penjualan!")
            
            # === TAHAP 5: AMBIL DATA LIST PEMBELI ===
            print(f"👥 Mengambil data list pembeli dari Rekap Penjualan untuk {username}...")
            
            from src.login_handler import get_customer_list_direct
            customer_list = get_customer_list_direct(driver, pin)
            
            if customer_list:
                print(f"\n📋 === LIST PEMBELI UNTUK {username} ({nama}) ===")
                print(f"📊 Total pembeli: {len(customer_list)}")
                print("-" * 50)
                
                for i, customer in enumerate(customer_list, 1):
                    print(f"{i:2d}. {customer}")
                
                print("-" * 50)
                print(f"✅ Data list pembeli berhasil diambil: {len(customer_list)} pembeli")
                rekap['sukses'].append(username)
            else:
                print("⚠️ Data list pembeli tidak ditemukan atau gagal diambil")
                rekap['gagal_navigasi'].append((username, "Gagal ambil data list pembeli"))
            
            time.sleep(1.5)  # Delay untuk stabilitas
            
        except Exception as e:
            print(f"❌ Error dalam proses untuk akun {username}: {str(e)}")
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
    
    # === REKAP AKHIR BATALKAN INPUTAN ===
    total_end = time.time()
    total_duration = total_end - total_start
    
    print(f"\n{'='*60}")
    print(f"📊 === REKAP AKHIR BATALKAN INPUTAN ===")
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
    
    print(f"\n🎉 Proses Batalkan Inputan selesai!")
    print(f"👋 Terima kasih!")

def main():
    """
    Fungsi utama untuk menjalankan automation batch processing
    Memproses multiple akun dengan retry mechanism dan tracking hasil
    """
    
    # Buat direktori yang diperlukan jika belum ada
    os.makedirs('akun', exist_ok=True)      # Direktori untuk file akun
    os.makedirs('results', exist_ok=True)   # Direktori untuk hasil Excel
    os.makedirs('logs', exist_ok=True)      # Direktori untuk file log
    
    # Setup system logging untuk tracking error dan debug
    setup_logging()
    
    # Load data akun dari file Excel
    try:
        accounts = load_accounts_from_excel(os.path.join('akun', 'akun.xlsx'))
        if not accounts:
            print("❌ Tidak ada akun valid ditemukan di akun/akun.xlsx")
            return
    except Exception as e:
        print(f"❌ Error membaca file akun: {str(e)}")
        return
    
    # Tampilkan statistik akun yang akan diproses
    print_account_stats(accounts)
    
    # Minta input menu utama dari user
    menu_choice = get_main_menu_input()
    
    # Handle menu choice
    if menu_choice == 2:
        print("\n📋 === FITUR BATALKAN INPUTAN ===")
        print("Memulai proses Batalkan Inputan...")
        
        # Minta input filter tanggal dari user (opsional)
        selected_date = get_date_input()
        
        # Jalankan fitur batalkan inputan
        run_batalkan_inputan(accounts, selected_date)
        return
    
    # Jika menu_choice == 1 (Check Stok), lanjutkan ke proses normal
    print("\n📊 Memulai proses Check Stok...")
    
    # Minta input filter tanggal dari user (opsional)
    selected_date = get_date_input()
    
    # Tampilkan informasi mode operasi
    if selected_date:
        print(f"\n🚀 Memulai proses dengan filter tanggal: {selected_date.strftime('%d %B %Y')}")
    else:
        print(f"\n🚀 Memulai proses TANPA filter tanggal spesifik")
    
    # Check headless mode configuration
    if USE_ENHANCED_CONFIG:
        headless_mode = config_manager.get('headless_mode', True)
    else:
        headless_mode = True  # Default fallback
    
    if headless_mode:
        print("🌐 Program akan berjalan dengan browser dalam mode headless")
        print("⚡ Mode headless memberikan performa lebih cepat tanpa GUI")
    else:
        print("🖥️ Program akan berjalan dengan browser visible (mode GUI)")
        print("👀 Anda dapat melihat aktivitas browser secara real-time")
    
    # Inisialisasi tracking waktu dan status
    total_start = time.time()  # Waktu mulai proses keseluruhan
    akun_durations = []        # Array untuk menyimpan durasi setiap akun
    
    # Dictionary untuk tracking status hasil pemrosesan setiap akun
    rekap = {
        'sukses': [],          # Akun yang berhasil diproses
        'gagal_login': [],     # Akun yang gagal login
        'gagal_navigasi': [],  # Akun yang gagal navigasi
        'gagal_waktu': [],     # Akun yang timeout
        'gagal_stok': [],      # Akun yang gagal ambil data stok
        'error_lain': [],      # Error lain yang tidak terduga
        'gagal_masuk_akun': [], # Akun yang mengalami "Gagal Masuk Akun" (dengan retry)
        'gagal_masuk_akun_count': 0  # Counter total "Gagal Masuk Akun" yang terjadi
    }
    
    # Loop utama: proses setiap akun satu per satu
    for account_index, (nama, username, pin) in enumerate(accounts):
        # Inisialisasi status dan variabel untuk akun saat ini
        akun_status = 'sukses'      # Status default: sukses
        akun_error = ''             # Pesan error jika ada masalah
        driver = None               # WebDriver object untuk browser automation
        akun_start = time.time()    # Waktu mulai pemrosesan akun ini
        
        # Retry mechanism: jika gagal, coba ulang maksimal 3 kali
        max_retries = 3             # Jumlah maksimal percobaan
        retry_count = 1             # Counter percobaan (mulai dari 1)
        account_success = False     # Flag untuk menandai apakah akun berhasil diproses
        
        # Loop retry: coba lagi jika gagal sampai maksimal percobaan
        while retry_count < max_retries and not account_success:
            try:
                print(f"🔄 Percobaan ke-{retry_count} untuk akun {username}")
                # Optimasi: Hanya delay jika ini retry (bukan percobaan pertama)
                if retry_count > 1:  # retry_count dimulai dari 1, jadi >1 berarti retry
                    time.sleep(3)  # Naik dari 2 ke 3 detik untuk retry
                
                # ========== TAHAP 1: LOGIN AWAL (VALIDASI) ==========
                print(f"🔐 Memulai login validasi untuk akun {username}...")
                login_result = login_direct(username, pin)  # Panggil fungsi login langsung
                driver = login_result[0]  # WebDriver object
                login_info = login_result[1]  # Info gagal masuk akun
                
                # Track gagal masuk akun
                if login_info['gagal_masuk_akun']:
                    rekap['gagal_masuk_akun'].append((username, f"Gagal Masuk Akun (retry berhasil)"))
                    rekap['gagal_masuk_akun_count'] += login_info['count']
                    print(f"📊 Gagal Masuk Akun terdeteksi untuk {username} - Total: {rekap['gagal_masuk_akun_count']}")
                
                if not driver:
                    alasan = f"Login gagal percobaan ke-{retry_count + 1}"
                    print(f"❌ Login gagal untuk akun {username} - percobaan {retry_count + 1}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        rekap['gagal_login'].append((username, alasan))
                        akun_status = 'gagal_login'
                        break
                    continue
                
                # === TAHAP 2: DRIVER SUDAH LOGIN ===
                print(f"✅ Login validasi berhasil untuk {username}. Driver sudah siap digunakan...")
                
                # Driver sudah berhasil login dari tahap sebelumnya
                # Tambahkan delay untuk stabilitas setelah login
                print("⏳ Menunggu stabilitas setelah login...")
                time.sleep(2.0)  # Delay 2 detik untuk stabilitas
                
                # === TAHAP 2.5: AMBIL DATA STOK DARI DASHBOARD ===
                print(f"📦 Mengambil data stok dari dashboard untuk {username}...")
                stock_value = get_stock_value_direct(driver)
                
                if stock_value:
                    print(f"✅ Data stok berhasil diambil: {stock_value}")
                else:
                    print("⚠️ Data stok tidak ditemukan atau gagal diambil")
                    # Track gagal ambil stok
                    rekap['gagal_stok'].append((username, "Gagal ambil data stok dari dashboard"))
                
                # === TAHAP 2.6: NAVIGASI KE LAPORAN PENJUALAN (TERPADU) ===
                print(f"📊 Navigasi ke Laporan Penjualan untuk {username}...")
                
                # Coba metode langsung terlebih dahulu
                laporan_success = click_laporan_penjualan_direct(driver)
                
                # Jika gagal, coba metode fallback tanpa fallback ke Atur Produk
                if not laporan_success:
                    print("🔄 Mencoba metode fallback navigasi ke Laporan Penjualan...")
                    laporan_success = find_and_click_laporan_penjualan(driver)
                
                if laporan_success:
                    print("✅ Berhasil navigasi ke Laporan Penjualan!")
                    navigation_success = True
                else:
                    print("⚠️ Gagal navigasi ke Laporan Penjualan, akan lanjut ke Atur Produk...")
                    
                    # Fallback: coba ke Atur Produk jika Laporan Penjualan gagal
                    print(f"🔧 Fallback: Navigasi ke Atur Produk untuk {username}...")
                    atur_produk_success = navigate_to_atur_produk(driver)
                    
                    if atur_produk_success:
                        print("✅ Berhasil navigasi ke Atur Produk!")
                        navigation_success = False  # Tetap False karena bukan ke laporan penjualan
                    else:
                        print("⚠️ Gagal navigasi ke Atur Produk juga...")
                        navigation_success = False
                        # Track gagal navigasi
                        rekap['gagal_navigasi'].append((username, "Gagal navigasi ke Laporan Penjualan dan Atur Produk"))
                
                # === TAHAP 3.5: KLIK ELEMEN TANGGAL DI LAPORAN PENJUALAN (HANYA JIKA USER INPUT TANGGAL) ===
                if navigation_success:
                    if selected_date:
                        print(f"📅 User telah input tanggal: {selected_date.strftime('%d %B %Y')}")
                        print(f"📅 Mengklik elemen tanggal di Laporan Penjualan untuk {username}...")
                        date_elements_success = click_date_elements_direct(driver, selected_date)
                        
                        if date_elements_success:
                            print("✅ Berhasil mengklik semua elemen tanggal!")
                        else:
                            print("⚠️ Gagal mengklik elemen tanggal, akan lanjut ke tahap berikutnya...")
                    else:
                        print("⏭️ User tidak input tanggal - LEWATI fungsi klik tanggal")
                        print("📅 Langsung ke tahap ambil data tabung terjual...")
                        date_elements_success = True  # Set True agar lanjut ke tahap berikutnya
                else:
                    print("⚠️ Gagal navigasi ke laporan penjualan, akan lanjut dengan halaman saat ini...")
                
                # === TAHAP 4: AMBIL DATA TABUNG TERJUAL ===
                print(f"📊 Mengambil data tabung terjual dari laporan penjualan...")
                tabung_terjual = get_tabung_terjual_direct(driver)
                
                if tabung_terjual:
                    print(f"✅ Data tabung terjual berhasil diambil: {tabung_terjual}")
                else:
                    print("⚠️ Data tabung terjual tidak ditemukan atau gagal diambil")
                    # Track gagal ambil data tabung terjual
                    rekap['gagal_navigasi'].append((username, "Gagal ambil data tabung terjual"))
                
                # Tambahkan delay setelah pengambilan data untuk stabilitas
                print("⏳ Menunggu stabilitas setelah pengambilan data...")
                time.sleep(1.5)  # Delay 1.5 detik untuk stabilitas
                
                # === TAHAP 5: SIMPAN DATA KE EXCEL ===
                print(f"💾 Menyimpan data ke Excel untuk {username}...")
                try:
                    # Siapkan data untuk Excel
                    nama_pangkalan = nama
                    
                    # Tentukan tanggal check
                    if selected_date:
                        tanggal_check = selected_date.strftime("%d/%m/%Y")
                    else:
                        tanggal_check = "TANPA FILTER TANGGAL"
                    
                    # Tentukan status berdasarkan total inputan
                    if tabung_terjual:
                        # Extract angka dari "28 Tabung" atau "0 Tabung"
                        import re
                        numbers = re.findall(r'\d+', tabung_terjual)
                        if numbers:
                            total_inputan_angka = int(numbers[0])
                            if total_inputan_angka > 0:
                                status = "Ada Penjualan"
                            else:
                                status = "Tidak Ada Penjualan"
                        else:
                            status = "Data Tidak Valid"
                    else:
                        tabung_terjual = "Tidak Ditemukan"
                        status = "Error Ambil Data"
                    
                    # Simpan ke Excel dengan format pivot baru (FORMAT UTAMA)
                    save_to_excel_pivot_format(
                        pangkalan_id=username,  # Gunakan username sebagai PANGKALAN_ID
                        nama_pangkalan=nama_pangkalan, 
                        tanggal_check=tanggal_check, 
                        stok_awal=stock_value, 
                        total_inputan=tabung_terjual, 
                        status=status, 
                        selected_date=selected_date
                    )
                    
                    print(f"✅ Data berhasil disimpan ke Excel!")
                    print(f"   📝 Nama Pangkalan: {nama_pangkalan}")
                    print(f"   🆔 Pangkalan ID: {username}")
                    print(f"   📅 Tanggal Check: {tanggal_check}")
                    print(f"   📦 Stok Awal: {stock_value}")
                    print(f"   📊 Total Inputan: {tabung_terjual}")
                    print(f"   🎯 Status: {status}")
                    
                    # Set account_success = True agar keluar dari loop while
                    account_success = True
                    
                except Exception as e:
                    alasan = f"Error simpan data Excel percobaan ke-{retry_count + 1}: {str(e)}"
                    print(f"❌ Error simpan data Excel: {str(e)}")
                    # Track error simpan Excel
                    rekap['error_lain'].append((username, f"Error simpan Excel: {str(e)}"))
                    retry_count += 1
                    if retry_count >= max_retries:
                        rekap['gagal_navigasi'].append((username, alasan))
                        akun_status = 'gagal_navigasi'
                        break
                    continue
                
                print(f"\n🎉 Selesai untuk akun {username}!")
                
                if akun_status == 'sukses':
                    rekap['sukses'].append(username)
                
                account_success = True
                
            except KeyboardInterrupt:
                print(f"\n⏹️ Program dihentikan saat memproses akun {username}")
                print("🧹 Membersihkan resource...")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                return  # Exit dari function main
            except Exception as e:
                alasan = f"Error dalam program percobaan ke-{retry_count + 1}: {str(e)}"
                print(f"❌ Error dalam program untuk akun {username}: {str(e)}")
                logger.error(f"Error untuk akun {username}: {str(e)}", exc_info=True)
                
                retry_count += 1
                if retry_count >= max_retries:
                    akun_status = 'error_lain'
                    rekap['error_lain'].append((username, alasan))
                    break
                else:
                    print(f"🔄 Akan mencoba ulang untuk akun {username}...")
                    time.sleep(2)  # Naik dari 1 ke 2 detik untuk error retry
            
            finally:
                # Browser management akan dilakukan di bawah setelah logic delay
                pass
        
        akun_end = time.time()
        akun_duration = akun_end - akun_start
        akun_durations.append(akun_duration)
        print(f"⏱️ Waktu proses akun {username}: {akun_duration:.2f} detik")
        
        # Track timeout jika proses terlalu lama (>60 detik)
        if akun_duration > 60:
            rekap['gagal_waktu'].append((username, f"Timeout - proses terlalu lama ({akun_duration:.1f} detik)"))
            print(f"⚠️ Timeout terdeteksi untuk {username}: {akun_duration:.1f} detik")
        
        print()  # Baris kosong untuk pemisahan
        
        # ========== ANTI-RATE LIMITING DELAY ==========
        # Tambahkan delay antar akun untuk menghindari rate limiting
        # Target: 20-25 detik per akun (termasuk delay ini)
        if account_index < len(accounts) - 1:  # Tidak delay setelah akun terakhir
            print("⏳ Menunggu sebentar untuk menghindari rate limiting...")
            
            # Delay khusus setiap 5 akun untuk menghindari web limiter
            if (account_index + 1) % 5 == 0:  # Setiap 5 akun (akun ke-5, 10, 15, dst)
                print("🚨 Delay ekstra setiap 5 akun untuk menghindari web limiter...")
                time.sleep(8.0)  # Delay ekstra 8 detik setiap 5 akun
            else:
                time.sleep(4.0)  # Delay normal 4.0 detik antar akun
    
    # === REKAP AKHIR ===
    print_final_summary(rekap, accounts, akun_durations, total_start)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Program dihentikan oleh user (Ctrl+C)")
        print("🧹 Membersihkan resource...")
        
        # Cleanup any remaining browser instances
        try:
            import psutil
            import subprocess
            
            # Kill any remaining chrome processes if needed
            for proc in psutil.process_iter(['pid', 'name']):
                if 'chrome' in proc.info['name'].lower() and 'selenium' in str(proc.cmdline()):
                    try:
                        proc.terminate()
                    except:
                        pass
        except ImportError:
            print("💡 Install psutil untuk cleanup otomatis: pip install psutil")
        except Exception:
            pass
            
        print("✅ Program berhasil dihentikan dengan bersih")
        print("👋 Terima kasih!")
    except Exception as e:
        print(f"\n❌ Error tidak terduga: {str(e)}")
        print("🧹 Membersihkan resource...")