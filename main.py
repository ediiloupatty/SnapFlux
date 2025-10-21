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
        print("\n🚧 === FITUR BATALKAN INPUTAN ===")
        print("Program untuk fitur 'Batalkan Inputan' akan segera tersedia!")
        print("Fitur ini akan memungkinkan untuk:")
        print("- Membatalkan inputan yang sudah dilakukan")
        print("- Reset data tertentu") 
        print("- Dan fitur lainnya yang akan ditambahkan")
        print("\n👋 Program selesai. Terima kasih!")
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
        'error_lain': []       # Error lain yang tidak terduga
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
                    time.sleep(2)  # Kurangi dari 5 ke 2 detik, hanya untuk retry
                
                # ========== TAHAP 1: LOGIN AWAL (VALIDASI) ==========
                print(f"🔐 Memulai login validasi untuk akun {username}...")
                driver = login_direct(username, pin)  # Panggil fungsi login langsung
                
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
                
                # === TAHAP 2.5: AMBIL DATA STOK DARI DASHBOARD ===
                print(f"📦 Mengambil data stok dari dashboard untuk {username}...")
                stock_value = get_stock_value_direct(driver)
                
                if stock_value:
                    print(f"✅ Data stok berhasil diambil: {stock_value}")
                else:
                    print("⚠️ Data stok tidak ditemukan atau gagal diambil")
                
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
                
                # === TAHAP 4.5: DECISION REKAP PENJUALAN (DISABLED UNTUK SAAT INI) ===
                # print(f"🤔 Decision: Apakah perlu klik Rekap Penjualan untuk {username}?")
                # from src.login_handler import should_click_rekap_penjualan
                # need_rekap = should_click_rekap_penjualan(tabung_terjual)
                # 
                # if need_rekap:
                #     # === TAHAP 4.6: NAVIGASI KE REKAP PENJUALAN ===
                #     print(f"📈 Navigasi ke Rekap Penjualan untuk {username}...")
                #     from src.login_handler import click_rekap_penjualan_direct
                #     rekap_success = click_rekap_penjualan_direct(driver)
                #     
                #     if rekap_success:
                #         print("✅ Berhasil navigasi ke Rekap Penjualan!")
                #         
                #         # === TAHAP 4.7: AMBIL DATA LIST PEMBELI ===
                #         print(f"👥 Mengambil data list pembeli dari Rekap Penjualan untuk {username}...")
                #         from src.login_handler import get_customer_list_direct
                #         customer_list = get_customer_list_direct(driver)
                #         
                #         if customer_list:
                #             print(f"✅ Data list pembeli berhasil diambil: {len(customer_list)} pembeli")
                #         else:
                #             print("⚠️ Data list pembeli tidak ditemukan atau gagal diambil")
                #     else:
                #         print("⚠️ Gagal navigasi ke Rekap Penjualan, akan lanjut ke tahap berikutnya...")
                # else:
                #     print("⏭️ Skip Rekap Penjualan - tidak ada penjualan atau data tidak valid")
                
                print("⏭️ Fungsi Decision Rekap Penjualan dinonaktifkan untuk sementara")
                print("📊 Program berhenti di pengambilan data tabung terjual")
                
                # === TAHAP 7: SIMPAN DATA KE EXCEL ===
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
                    time.sleep(1)  # Kurangi dari 2 ke 1 detik
            
            finally:
                # Browser management akan dilakukan di bawah setelah logic delay
                pass
        
        akun_end = time.time()
        akun_duration = akun_end - akun_start
        akun_durations.append(akun_duration)
        print(f"⏱️ Waktu proses akun {username}: {akun_duration:.2f} detik\n")
        
        # ========== ANTI-RATE LIMITING DELAY ==========
        # Tambahkan delay kecil antar akun untuk menghindari rate limiting
        # Target: 19-20 detik per akun (termasuk delay ini)
        if account_index < len(accounts) - 1:  # Tidak delay setelah akun terakhir
            print("⏳ Menunggu sebentar untuk menghindari rate limiting...")
            time.sleep(2.5)  # Delay 2.5 detik antar akun
    
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