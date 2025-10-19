#!/usr/bin/env python3
"""
Main entry point untuk automation script
"""
import os
import sys
import time
import random
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils import *
from driver_setup import setup_driver
from login_handler import login_direct

def main():
    """Fungsi utama batch untuk banyak akun, dengan pengukuran waktu proses dan rekap hasil akhir."""
    
    # Create necessary directories
    os.makedirs('akun', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Setup logging
    setup_logging()
    
    
    # Load accounts from Excel
    try:
        accounts = load_accounts_from_excel(os.path.join('akun', 'akun.xlsx'))
        if not accounts:
            print("❌ Tidak ada akun valid ditemukan di akun/akun.xlsx")
            return
    except Exception as e:
        print(f"❌ Error membaca file akun: {str(e)}")
        return
    
    # Print account stats
    print_account_stats(accounts)
    
    # Minta input tanggal dari user
    selected_date = get_date_input()
    
    if selected_date:
        print(f"\n🚀 Memulai proses dengan filter tanggal: {selected_date.strftime('%d %B %Y')}")
    else:
        print(f"\n🚀 Memulai proses TANPA filter tanggal spesifik")
    
    print("🌐 Program akan berjalan dengan browser window yang terlihat")
    print("👀 Anda dapat melihat proses scraping secara realtime di browser")
    
    total_start = time.time()
    akun_durations = []
    
    # Status tracking
    rekap = {
        'sukses': [],
        'gagal_login': [],
        'gagal_navigasi': [],
        'gagal_waktu': [],
        'gagal_stok': [],
        'error_lain': []
    }
    
    # Track completed accounts for delay logic
    completed_accounts = 0
    
    for account_index, (nama, username, pin) in enumerate(accounts):
        akun_status = 'sukses'
        akun_error = ''
        driver = None
        akun_start = time.time()
        
        # Retry mechanism untuk setiap akun
        max_retries = 3
        retry_count = 1  # Mulai dari percobaan ke-2
        account_success = False
        
        while retry_count < max_retries and not account_success:
            try:
                print(f"🔄 Percobaan ke-{retry_count + 1} untuk akun {username}")
                time.sleep(5)
                
                # === TAHAP 1: LOGIN AWAL (VALIDASI) ===
                print(f"🔐 Memulai login validasi untuk akun {username}...")
                driver = login_direct(username, pin)
                
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
                from src.login_handler import get_stock_value_direct
                stock_value = get_stock_value_direct(driver)
                
                if stock_value:
                    print(f"✅ Data stok berhasil diambil: {stock_value}")
                else:
                    print("⚠️ Data stok tidak ditemukan atau gagal diambil")
                
                # === TAHAP 2.6: NAVIGASI KE LAPORAN PENJUALAN (TERPADU) ===
                print(f"📊 Navigasi ke Laporan Penjualan untuk {username}...")
                from src.login_handler import click_laporan_penjualan_direct, find_and_click_laporan_penjualan
                
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
                    from src.login_handler import navigate_to_atur_produk
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
                        from src.login_handler import click_date_elements_direct
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
                from src.login_handler import get_tabung_terjual_direct
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
                    
                    # Simpan ke Excel dengan format baru
                    from src.utils import save_to_excel_new_format
                    save_to_excel_new_format(nama_pangkalan, tanggal_check, stock_value, tabung_terjual, status, selected_date)
                    
                    print(f"✅ Data berhasil disimpan ke Excel!")
                    print(f"   📝 Nama Pangkalan: {nama_pangkalan}")
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
                    time.sleep(2)
            
            finally:
                # Browser management akan dilakukan di bawah setelah logic delay
                pass
        
        akun_end = time.time()
        akun_duration = akun_end - akun_start
        akun_durations.append(akun_duration)
        print(f"⏱️ Waktu proses akun {username}: {akun_duration:.2f} detik\n")
        
        # Increment completed accounts counter
        completed_accounts += 1
        
        # === LOGIC TUTUP TAB SETELAH AKUN KE-3 (DISABLED) ===
        # Jeda setelah 3 akun dinonaktifkan untuk performa maksimal
        # if completed_accounts % 3 == 0:
        #     print(f"🎯 === {completed_accounts} akun selesai - MENUTUP TAB BROWSER ===")
        #     
        #     # Tutup tab browser saat ini
        #     if driver:
        #         print(f"📑 Menutup tab browser untuk akun {username}...")
        #         try:
        #             driver.close()  # Tutup tab saat ini, bukan seluruh browser
        #             print("✅ Tab browser berhasil ditutup")
        #         except Exception as e:
        #             print(f"⚠️ Error menutup tab: {str(e)}")
        #             # Jika gagal close tab, coba quit seluruh browser
        #             try:
        #                 driver.quit()
        #                 print("✅ Browser berhasil ditutup sebagai fallback")
        #             except:
        #                 pass
        #         finally:
        #             driver = None
        #     
        #     # Beri delay random 25-30 detik
        #     delay_seconds = random.uniform(24, 26)
        #     print(f"⏳ Menunggu {delay_seconds:.1f} detik sebelum lanjut ke akun berikutnya...")
        #     time.sleep(delay_seconds)
        #     print("✅ Delay selesai, melanjutkan ke akun berikutnya...\n")
        # else:
        #     # Untuk akun selain kelipatan 3, browser tetap terbuka untuk monitoring
        #     # (behavior sama seperti sebelumnya)
        #     pass
        
        print("⚡ Jeda setelah 3 akun dinonaktifkan - melanjutkan langsung ke akun berikutnya")
    
    # === REKAP AKHIR ===
    print_final_summary(rekap, accounts, akun_durations, total_start)

if __name__ == "__main__":
    main()