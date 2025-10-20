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
from utils import *
from driver_setup import setup_driver
from login_handler import login_direct

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
    
    # Minta input filter tanggal dari user (opsional)
    selected_date = get_date_input()
    
    # Tampilkan informasi mode operasi
    if selected_date:
        print(f"\n🚀 Memulai proses dengan filter tanggal: {selected_date.strftime('%d %B %Y')}")
    else:
        print(f"\n🚀 Memulai proses TANPA filter tanggal spesifik")
    
    print("🌐 Program akan berjalan dengan browser dalam mode headless")
    print("⚡ Mode headless memberikan performa lebih cepat tanpa GUI")
    
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
                print(f"🔄 Percobaan ke-{retry_count + 1} untuk akun {username}")
                time.sleep(5)  # Delay 5 detik sebelum percobaan berikutnya
                
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
        
        # ========== CATATAN: LOGIC JEDA DITIADAKAN ==========
        # Logic untuk jeda dan tutup browser setelah 3 akun telah dinonaktifkan
        # untuk performa maksimal dan proses yang lebih cepat
        # Browser akan tetap terbuka sepanjang proses untuk monitoring
        
        # Lanjut langsung ke akun berikutnya tanpa jeda
    
    # === REKAP AKHIR ===
    print_final_summary(rekap, accounts, akun_durations, total_start)

if __name__ == "__main__":
    main()