"""
Login handling dan fungsi authentication untuk platform merchant Pertamina
File ini menangani semua proses login, navigasi, dan ekstraksi data dari dashboard
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

# ========== KONFIGURASI URL ==========
LOGIN_URL = "https://subsiditepatlpg.mypertamina.id/merchant-login"  # URL login merchant portal
logger = logging.getLogger('automation')  # Logger untuk tracking error dan debug

from driver_setup import setup_driver

def login_direct(username, pin):
    """
    Login langsung dengan strategi yang sudah terbukti berhasil
    Fungsi ini melakukan login otomatis ke portal merchant dengan retry mechanism
    
    Args:
        username (str): Username berupa email atau nomor HP
        pin (str): PIN untuk authentication
        
    Returns:
        webdriver.Chrome: WebDriver object jika login berhasil, None jika gagal
    """
    print(f"\n🔐 === LOGIN LANGSUNG UNTUK {username} ===")
    
    driver = None
    try:
        # Setup driver
        driver = setup_driver(headless=False)
        driver.get(LOGIN_URL)
        
        # Tunggu halaman loading
        time.sleep(3)
        
        # Langsung cari dan isi email
        print("📧 Mencari dan mengisi field email...")
        email_inputs = driver.find_elements(By.TAG_NAME, "input")
        
        email_filled = False
        for input_field in email_inputs:
            try:
                input_type = input_field.get_attribute("type")
                if input_type != "password" and input_type != "submit" and input_type != "button":
                    if input_field.is_displayed() and input_field.is_enabled():
                        input_field.clear()
                        input_field.send_keys(username)
                        print(f"✅ Email berhasil diisi: {username}")
                        email_filled = True
                        break
            except:
                continue
        
        if not email_filled:
            print("❌ Gagal mengisi email")
            return None
        
        # Langsung cari dan isi PIN
        print("🔑 Mencari dan mengisi field PIN...")
        pin_inputs = driver.find_elements(By.TAG_NAME, "input")
        
        pin_filled = False
        for input_field in pin_inputs:
            try:
                input_type = input_field.get_attribute("type")
                if input_type == "password":
                    if input_field.is_displayed() and input_field.is_enabled():
                        input_field.clear()
                        input_field.send_keys(pin)
                        print(f"✅ PIN berhasil diisi: {pin}")
                        pin_filled = True
                        break
            except:
                continue
        
        if not pin_filled:
            print("❌ Gagal mengisi PIN")
            return None
        
        # Langsung cari dan klik tombol login
        print("🚀 Mencari dan mengklik tombol login...")
        login_buttons = driver.find_elements(By.TAG_NAME, "button")
        
        login_clicked = False
        for button in login_buttons:
            try:
                button_text = button.text.strip().upper()
                if "MASUK" in button_text or "LOGIN" in button_text:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        print("✅ Tombol login berhasil diklik")
                        login_clicked = True
                        break
            except:
                continue
        
        if not login_clicked:
            print("❌ Gagal mengklik tombol login")
            return None
        
        # Tunggu proses login
        time.sleep(3)
        
        # === DETEKSI CEPAT "GAGAL MASUK AKUN" ===
        print("🔍 Mencari pesan 'Gagal Masuk Akun' dengan class selector...")
        gagal_masuk_detected = False
        
        try:
            # Berdasarkan debug info: class='mantine-Text-root mantine-Title-root mantine-tvqdf2'
            elements = driver.find_elements(By.CLASS_NAME, "mantine-Title-root")
            
            for element in elements:
                text = element.text.strip()
                if "Gagal Masuk Akun" in text:
                    gagal_masuk_detected = True
                    print("❌ PESAN 'GAGAL MASUK AKUN' TERDETEKSI!")
                    print(f"📝 Text: '{text}'")
                    break
                    
            if not gagal_masuk_detected:
                print("✅ Tidak ada pesan 'Gagal Masuk Akun' ditemukan - LANJUT KE PROSES SELANJUTNYA")
                    
        except Exception as e:
            print(f"⚠️ Error mencari pesan 'Gagal Masuk Akun': {str(e)}")
            print("✅ Error dalam pencarian - LANJUT KE PROSES SELANJUTNYA")
        
        # === HANDLE GAGAL MASUK AKUN ===
        if gagal_masuk_detected:
            print("🔄 === PROSES RETRY LOGIN SETELAH GAGAL MASUK AKUN ===")
            
            # Tunggu 2 menit (120 detik)
            print("⏳ Menunggu 2 menit (120 detik)...")
            time.sleep(120)
            print("✅ Tunggu 2 menit selesai!")
            
            # Langsung klik tombol MASUK lagi tanpa reload
            print("🔄 Mengklik tombol MASUK lagi tanpa reload...")
            login_buttons = driver.find_elements(By.TAG_NAME, "button")
            
            retry_clicked = False
            for button in login_buttons:
                try:
                    button_text = button.text.strip().upper()
                    if "MASUK" in button_text or "LOGIN" in button_text:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            print("✅ Tombol MASUK berhasil diklik lagi!")
                            retry_clicked = True
                            break
                except:
                    continue
            
            if not retry_clicked:
                print("❌ Gagal mengklik tombol MASUK lagi")
                return None
            
            # Tunggu proses login kedua
            print("⏳ Menunggu proses login kedua...")
            time.sleep(3)
        
        # Cek apakah login berhasil (setelah retry jika ada)
        current_url = driver.current_url
        if "merchant-login" not in current_url:
            print("✅ Login berhasil!")
            return driver
        else:
            print("❌ Login gagal - masih di halaman login")
            return None
        
    except Exception as e:
        print(f"❌ Error dalam login: {str(e)}")
        if driver:
            driver.quit()
        return None

def get_stock_value_direct(driver):
    """Ambil nilai stok langsung menggunakan lokasi yang sudah diketahui - SUPER CEPAT"""
    print("\n📦 === AMBIL DATA STOK LANGSUNG ===")
    try:
        time.sleep(2)
        print("🚀 Mengambil stok langsung menggunakan class yang sudah diketahui...")
        
        # Langsung ambil dengan class yang sudah terbukti berhasil
        element = driver.find_element(By.CLASS_NAME, "styles_summaryProductCard__Uv3IK")
        text = element.text.strip()
        
        print(f"✅ Elemen stok ditemukan langsung!")
        print(f"📝 Text: '{text}'")
        
        # Langsung extract angka pertama tanpa validasi tambahan
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            stock_value = numbers[0]
            print(f"🔢 Angka: {numbers}")
            print(f"📊 Nilai Stok: {stock_value}")
            print(f"✅ Data stok berhasil diambil: {stock_value}")
            return stock_value
        else:
            print("❌ Tidak ada angka ditemukan dalam text")
            return None
            
    except Exception as e:
        print(f"❌ Error mengambil data stok: {str(e)}")
        return None

def click_laporan_penjualan_direct(driver):
    """Klik menu 'Laporan Penjualan' langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n📊 === KLIK LAPORAN PENJUALAN LANGSUNG ===")
    try:
        time.sleep(2)
        print("🚀 Mengklik Laporan Penjualan langsung menggunakan lokasi yang sudah diketahui...")
        try:
            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Laporan Penjualan')]")
            text = element.text.strip()
            if text and 'laporan' in text.lower() and 'penjualan' in text.lower():
                print(f"✅ Menu Laporan Penjualan ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"✅ Berhasil mengklik menu: '{text}'")
                    time.sleep(3)
                    print("✅ Navigasi ke Laporan Penjualan berhasil!")
                    return True
                else:
                    print("❌ Menu tidak dapat diklik")
                    return False
            else:
                print("❌ Elemen tidak mengandung 'Laporan Penjualan'")
                return False
        except Exception as e:
            print(f"⚠️ Error dengan XPath selector: {str(e)}")
            print("🔄 Mencoba dengan class fallback...")
            try:
                element = driver.find_element(By.CLASS_NAME, "mantine-Text-root")
                text = element.text.strip()
                if text and 'laporan' in text.lower() and 'penjualan' in text.lower():
                    print(f"✅ Menu Laporan Penjualan ditemukan dengan class fallback!")
                    print(f"📝 Text: '{text}'")
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"✅ Berhasil mengklik menu: '{text}'")
                        time.sleep(3)
                        print("✅ Navigasi ke Laporan Penjualan berhasil!")
                        return True
                    else:
                        print("❌ Menu tidak dapat diklik")
                        return False
            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")
        return False
    except Exception as e:
        print(f"❌ Error mengklik Laporan Penjualan: {str(e)}")
        return False

def navigate_to_atur_produk(driver):
    """Navigasi ke menu 'Atur Produk' setelah mengambil data stok"""
    print("\n🔧 === NAVIGASI KE ATUR PRODUK ===")
    try:
        time.sleep(2)
        print("🔍 Mencari menu 'Atur Produk' atau 'Atur Stok & Harga'...")
        menu_selectors = [
            "//button[contains(text(), 'Atur Produk')]",
            "//a[contains(text(), 'Atur Produk')]",
            "//div[contains(text(), 'Atur Produk')]",
            "//span[contains(text(), 'Atur Produk')]",
            "//button[contains(text(), 'Atur Stok')]",
            "//a[contains(text(), 'Atur Stok')]",
            "//div[contains(text(), 'Atur Stok')]",
            "//span[contains(text(), 'Atur Stok')]",
            "//*[contains(text(), 'Atur') and contains(text(), 'Harga')]"
        ]
        for selector in menu_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Ditemukan {len(elements)} elemen dengan selector: {selector}")
                    for idx, element in enumerate(elements):
                        try:
                            text = element.text.strip()
                            print(f"  🔧 Menu {idx+1}: '{text}'")
                            if text and ('atur' in text.lower() and ('produk' in text.lower() or 'stok' in text.lower())):
                                if element.is_displayed() and element.is_enabled():
                                    print(f"✅ Menu ditemukan dan dapat diklik: '{text}'")
                                    element.click()
                                    time.sleep(3)
                                    print("✅ Navigasi ke Atur Produk berhasil!")
                                    return True
                                else:
                                    print(f"⚠️ Menu tidak dapat diklik: '{text}'")
                        except Exception as e:
                            print(f"    ⚠️ Error mengklik menu {idx+1}: {str(e)}")
                            continue
            except Exception as e:
                print(f"⚠️ Error dengan selector {selector}: {str(e)}")
                continue
        print("❌ Menu 'Atur Produk' tidak ditemukan")
        return False
    except Exception as e:
        print(f"❌ Error navigasi ke Atur Produk: {str(e)}")
        return False

def find_and_click_laporan_penjualan(driver):
    """Fallback function untuk mencari dan mengklik laporan penjualan"""
    print("\n📊 === FALLBACK: CARI LAPORAN PENJUALAN ===")
    try:
        time.sleep(2)
        print("🔍 Mencari menu 'Laporan Penjualan'...")
        menu_selectors = [
            "//button[contains(text(), 'Laporan Penjualan')]",
            "//a[contains(text(), 'Laporan Penjualan')]",
            "//div[contains(text(), 'Laporan Penjualan')]",
            "//span[contains(text(), 'Laporan Penjualan')]",
            "//*[contains(text(), 'Laporan') and contains(text(), 'Penjualan')]"
        ]
        for selector in menu_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"✅ Ditemukan {len(elements)} elemen dengan selector: {selector}")
                    for idx, element in enumerate(elements):
                        try:
                            text = element.text.strip()
                            print(f"  📊 Menu {idx+1}: '{text}'")
                            if text and ('laporan' in text.lower() and 'penjualan' in text.lower()):
                                if element.is_displayed() and element.is_enabled():
                                    print(f"✅ Menu ditemukan dan dapat diklik: '{text}'")
                                    element.click()
                                    time.sleep(3)
                                    print("✅ Navigasi ke Laporan Penjualan berhasil!")
                                    return True
                                else:
                                    print(f"⚠️ Menu tidak dapat diklik: '{text}'")
                        except Exception as e:
                            print(f"    ⚠️ Error mengklik menu {idx+1}: {str(e)}")
                            continue
            except Exception as e:
                print(f"⚠️ Error dengan selector {selector}: {str(e)}")
                continue
        print("❌ Menu 'Laporan Penjualan' tidak ditemukan")
        return False
    except Exception as e:
        print(f"❌ Error navigasi ke Laporan Penjualan: {str(e)}")
        return False

def click_date_elements_direct(driver, selected_date=None):
    """Klik elemen tanggal di halaman Laporan Penjualan langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n📅 === KLIK ELEMEN TANGGAL LANGSUNG ===")
    
    try:
        # Tunggu halaman selesai loading
        time.sleep(3)
        
        print("🚀 Mengklik elemen tanggal langsung menggunakan lokasi yang sudah diketahui...")
        
        # === STEP 1: Klik "Atur Rentang Waktu" langsung ===
        print("\n📅 === STEP 1: KLIK 'ATUR RENTANG WAKTU' LANGSUNG ===")
        try:
            # Gunakan XPath yang sudah terbukti berhasil dari debugging:
            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Atur Rentang Waktu')]")
            text = element.text.strip()
            
            if text and 'atur' in text.lower() and 'rentang' in text.lower():
                print(f"✅ Elemen 'Atur Rentang Waktu' ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"✅ Berhasil mengklik: '{text}'")
                else:
                    print("❌ Elemen tidak dapat diklik")
                    return False
            else:
                print("❌ Elemen tidak mengandung 'Atur Rentang Waktu'")
                return False
        except Exception as e:
            print(f"❌ Error dengan XPath selector: {str(e)}")
            return False

        # Tunggu dropdown terbuka
        time.sleep(2)
                                
        # === STEP 2: Klik bulan tahun sesuai input user ===
        print("\n📅 === STEP 2: KLIK BULAN TAHUN SESUAI INPUT USER ===")
        
        # Tentukan bulan dan tahun berdasarkan input user
        if selected_date:
            # Konversi bulan angka ke nama bulan Indonesia
            bulan_names = [
                '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            bulan_name = bulan_names[selected_date.month]
            tahun = selected_date.year
            bulan_tahun_text = f"{bulan_name} {tahun}"
            
            print(f"📅 Menggunakan tanggal input user: {selected_date.strftime('%d %B %Y')}")
            print(f"🎯 Mencari elemen: '{bulan_tahun_text}'")
        else:
            # Fallback ke tanggal hari ini jika tidak ada input
            from datetime import datetime
            today = datetime.now()
            bulan_names = [
                '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            bulan_name = bulan_names[today.month]
            tahun = today.year
            bulan_tahun_text = f"{bulan_name} {tahun}"
            
            print(f"📅 Menggunakan tanggal hari ini: {today.strftime('%d %B %Y')}")
            print(f"🎯 Mencari elemen: '{bulan_tahun_text}'")
        
        try:
            # Gunakan informasi yang sudah diketahui dari debugging:
            # Tag: button, Class: 'mantine-UnstyledButton-root'
            element = driver.find_element(By.XPATH, f"//*[contains(text(), '{bulan_tahun_text}')]")
            text = element.text.strip()
            
            if text and bulan_name.lower() in text.lower() and str(tahun) in text:
                print(f"✅ Elemen bulan tahun ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"✅ Berhasil mengklik bulan tahun: '{text}'")
                else:
                    print("❌ Elemen tidak dapat diklik")
                    return False
            else:
                print(f"❌ Elemen tidak mengandung '{bulan_tahun_text}'")
                return False

        except Exception as e:
            print(f"⚠️ Error dengan XPath selector: {str(e)}")
            
            # Fallback: gunakan class yang sudah diketahui
            print("🔄 Mencoba dengan class fallback...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-UnstyledButton-root")
                
                for element in elements:
                    text = element.text.strip()
                    if text and bulan_name.lower() in text.lower() and str(tahun) in text:
                        print(f"✅ Elemen bulan tahun ditemukan dengan class fallback!")
                        print(f"📝 Text: '{text}'")
                        
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            print(f"✅ Berhasil mengklik bulan tahun: '{text}'")
                            break
                        else:
                            print("❌ Elemen tidak dapat diklik")
                            return False
                    else:
                        print(f"❌ Elemen bulan tahun tidak ditemukan dengan class fallback")
                        return False

            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")
                return False

        # Tunggu dropdown bulan terbuka
        time.sleep(2)
        
        # === STEP 3: Klik bulan singkat sesuai input user ===
        print("\n📅 === STEP 3: KLIK BULAN SINGKAT LANGSUNG ===")
        
        # Tentukan bulan singkat berdasarkan input user
        if selected_date:
            bulan_singkat_list = [
                '', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'
            ]
            bulan_singkat = bulan_singkat_list[selected_date.month]
            print(f"🎯 Mengklik bulan singkat langsung: '{bulan_singkat}'")
        else:
            # Fallback ke bulan saat ini
            from datetime import datetime
            today = datetime.now()
            bulan_singkat_list = [
                '', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
                'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'
            ]
            bulan_singkat = bulan_singkat_list[today.month]
            print(f"🎯 Mengklik bulan singkat langsung: '{bulan_singkat}'")
        
        # Langsung klik menggunakan XPath yang sudah terbukti berhasil
        try:
            element = driver.find_element(By.XPATH, f"//*[text()='{bulan_singkat}']")
            text = element.text.strip()
            
            if text and text == bulan_singkat:
                print(f"✅ Elemen bulan singkat ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"✅ Berhasil mengklik bulan singkat: '{text}'")
                else:
                    print("❌ Elemen tidak dapat diklik")
                    return False
            else:
                print(f"❌ Elemen tidak mengandung '{bulan_singkat}'")
                return False

        except Exception as e:
            print(f"❌ Error mengklik bulan singkat: {str(e)}")
            return False

        # Tunggu dropdown tanggal terbuka
        time.sleep(2)
        
        # === STEP 4: Klik tanggal spesifik sesuai input user ===
        print("\n📅 === STEP 4: KLIK TANGGAL SPESIFIK LANGSUNG ===")
        
        # Tentukan tanggal berdasarkan input user
        if selected_date:
            tanggal_hari = selected_date.day
            print(f"🎯 Mengklik tanggal langsung: '{tanggal_hari}'")
        else:
            # Fallback ke tanggal hari ini
            from datetime import datetime
            today = datetime.now()
            tanggal_hari = today.day
            print(f"🎯 Mengklik tanggal langsung: '{tanggal_hari}'")
        
        # Klik tanggal sebanyak 2x langsung
        for klik_ke in range(1, 3):  # Klik 2x
            print(f"🖱️ Klik tanggal ke-{klik_ke}: '{tanggal_hari}'")
            
            try:
                # Langsung klik menggunakan XPath yang sudah terbukti berhasil
                element = driver.find_element(By.XPATH, f"//*[text()='{tanggal_hari}']")
                text = element.text.strip()
                
                if text and text == str(tanggal_hari):
                    print(f"✅ Elemen tanggal ditemukan langsung!")
                    print(f"📝 Text: '{text}'")
                    
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"✅ Berhasil mengklik tanggal ke-{klik_ke}: '{text}'")
                    else:
                        print(f"❌ Elemen tanggal tidak dapat diklik (klik ke-{klik_ke})")
                        return False
                else:
                    print(f"❌ Elemen tidak mengandung tanggal '{tanggal_hari}' (klik ke-{klik_ke})")
                    return False
            
            except Exception as e:
                print(f"❌ Error mengklik tanggal '{tanggal_hari}' (klik ke-{klik_ke}): {str(e)}")
            return False
        
            # Tunggu sebentar antara klik
            if klik_ke < 2:  # Tidak perlu tunggu setelah klik terakhir
                print("⏳ Tunggu 1 detik sebelum klik berikutnya...")
                time.sleep(1)
        
        print("✅ Semua elemen tanggal berhasil diklik!")
        return True
        
    except Exception as e:
        print(f"❌ Error mengklik elemen tanggal: {str(e)}")
        return False

def get_tabung_terjual_direct(driver):
    """Ambil data 'xxx Tabung' langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n📊 === AMBIL DATA TABUNG TERJUAL LANGSUNG ===")
    
    try:
        # Tunggu halaman selesai loading
        time.sleep(2)
        
        print("🚀 Mengambil data tabung terjual langsung menggunakan lokasi yang sudah diketahui...")
        
        # Gunakan informasi yang sudah diketahui dari debugging:
        # Tag: div, Class: 'mantine-Text-root mantine-1pqbi01', Text: '0 Tabung'
        try:
            # Coba dengan class yang sudah diketahui
            elements = driver.find_elements(By.CLASS_NAME, "mantine-Text-root")
            
            for element in elements:
                text = element.text.strip()
                if text and 'tabung' in text.lower() and any(char.isdigit() for char in text):
                    # Skip jika ini adalah text "Total Tabung LPG 3 Kg Terjual"
                    if 'total' in text.lower() and 'terjual' in text.lower():
                        continue
                    
                    print(f"✅ Data tabung terjual ditemukan langsung!")
                    print(f"📝 Text: '{text}'")
                    
                    # Ekstrak angka langsung
                    import re
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        tabung_value = numbers[0]
                        clean_text = f"{tabung_value} Tabung"
                        print(f"🔢 Angka: {numbers}")
                        print(f"📊 Jumlah Tabung Terjual: {tabung_value}")
                        print(f"📝 Text Bersih: '{clean_text}'")
                        print(f"✅ Data tabung terjual berhasil diambil: {clean_text}")
                        return clean_text
            
            print("❌ Data tabung terjual tidak ditemukan dengan class selector")
            return None
                
        except Exception as e:
            print(f"⚠️ Error dengan class selector: {str(e)}")
            
            # Fallback: gunakan XPath berdasarkan text
            print("🔄 Mencoba dengan XPath fallback...")
            try:
                all_elements = driver.find_elements(By.XPATH, "//*")
                
                for element in all_elements:
                    text = element.text.strip()
                    if text and len(text) < 50:  # Batasi panjang text
                        if ('tabung' in text.lower() and 
                            any(char.isdigit() for char in text) and 
                            'total' not in text.lower()):
                            
                            print(f"✅ Data tabung terjual ditemukan dengan XPath fallback!")
                            print(f"📝 Text: '{text}'")
                            
                            import re
                            numbers = re.findall(r'\d+', text)
                            if numbers:
                                tabung_value = numbers[0]
                                clean_text = f"{tabung_value} Tabung"
                                print(f"🔢 Angka: {numbers}")
                                print(f"📊 Jumlah Tabung Terjual: {tabung_value}")
                                print(f"📝 Text Bersih: '{clean_text}'")
                                print(f"✅ Data tabung terjual berhasil diambil: {clean_text}")
                                return clean_text
                                
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return None
            
    except Exception as e:
        print(f"❌ Error mengambil data tabung terjual: {str(e)}")
        return None

# ===== FUNGSI DECISION REKAP PENJUALAN (DISABLED UNTUK SAAT INI) =====
# Fungsi-fungsi di bawah ini dinonaktifkan untuk sementara tapi tetap ada untuk masa depan

def should_click_rekap_penjualan(tabung_terjual_text):
    """Decision function: apakah perlu klik Rekap Penjualan berdasarkan data tabung terjual"""
    print(f"\n🤔 === DECISION: APAKAH PERLU KLIK REKAP PENJUALAN? ===")
    
    try:
        if not tabung_terjual_text:
            print("❌ Data tabung terjual kosong - SKIP Rekap Penjualan")
            return False
        
        print(f"📊 Data tabung terjual: '{tabung_terjual_text}'")
        
        # Ekstrak angka dari text "28 Tabung" atau "0 Tabung"
        import re
        numbers = re.findall(r'\d+', tabung_terjual_text)
        
        if not numbers:
            print("❌ Tidak ada angka ditemukan - SKIP Rekap Penjualan")
            return False
        
        tabung_value = int(numbers[0])
        print(f"🔢 Nilai tabung terjual: {tabung_value}")
        
        if tabung_value == 0:
            print("❌ Tabung terjual = 0 - SKIP Rekap Penjualan")
            print("💡 Tidak ada penjualan, tidak perlu melihat rekap")
            return False
        elif tabung_value > 0:
            print(f"✅ Tabung terjual = {tabung_value} (> 0) - KLIK Rekap Penjualan")
            print(f"💡 Ada penjualan {tabung_value} tabung, perlu melihat rekap detail")
            return True
        else:
            print(f"⚠️ Nilai tabung tidak valid: {tabung_value} - SKIP Rekap Penjualan")
            return False
        
    except Exception as e:
        print(f"❌ Error dalam decision function: {str(e)}")
        print("⚠️ Error - SKIP Rekap Penjualan")
        return False

def click_rekap_penjualan_direct(driver):
    """Klik menu 'Rekap Penjualan' langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n📈 === KLIK REKAP PENJUALAN LANGSUNG ===")
    
    try:
        # Tunggu halaman selesai loading
        time.sleep(2)
        
        print("🚀 Mengklik Rekap Penjualan langsung menggunakan lokasi yang sudah diketahui...")
        
        # Gunakan informasi yang sudah diketahui dari debugging:
        # Tag: div, Class: 'mantine-Text-root mantine-f6lsr9', Text: 'Rekap Penjualan'
        try:
            # Coba dengan XPath berdasarkan text yang paling spesifik
            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Rekap Penjualan')]")
            text = element.text.strip()
            
            if text and 'rekap' in text.lower() and 'penjualan' in text.lower():
                print(f"✅ Menu Rekap Penjualan ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"✅ Berhasil mengklik menu: '{text}'")
                    
                    # Tunggu halaman loading
                    time.sleep(3)
                    print("✅ Navigasi ke Rekap Penjualan berhasil!")
                    return True
                else:
                    print("❌ Menu tidak dapat diklik")
                    return False
            else:
                print("❌ Elemen tidak mengandung 'Rekap Penjualan'")
                return False
                
        except Exception as e:
            print(f"⚠️ Error dengan XPath selector: {str(e)}")
            
            # Fallback: gunakan class yang sudah diketahui
            print("🔄 Mencoba dengan class fallback...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-Text-root")
                
                for element in elements:
                    text = element.text.strip()
                    if text and 'rekap' in text.lower() and 'penjualan' in text.lower():
                        print(f"✅ Menu Rekap Penjualan ditemukan dengan class fallback!")
                        print(f"📝 Text: '{text}'")
                        
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            print(f"✅ Berhasil mengklik menu: '{text}'")
                            
                            # Tunggu halaman loading
                            time.sleep(3)
                            print("✅ Navigasi ke Rekap Penjualan berhasil!")
                            return True
                        else:
                            print("❌ Menu tidak dapat diklik")
                            return False
            
            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")
                return False
        
    except Exception as e:
        print(f"❌ Error mengklik Rekap Penjualan: {str(e)}")
        return False

def get_customer_list_direct(driver):
    """Ambil data list pembeli langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n👥 === AMBIL DATA LIST PEMBELI LANGSUNG ===")
    
    try:
        # Tunggu halaman selesai loading
        time.sleep(3)
        
        print("🚀 Mengambil data list pembeli langsung menggunakan lokasi yang sudah diketahui...")
        
        # Gunakan informasi yang sudah diketahui dari debugging:
        # Class: 'styles_listTransactionRoot__pvz4r mantine-1uguyhf'
        try:
            # Coba dengan class yang sudah diketahui
            elements = driver.find_elements(By.CLASS_NAME, "styles_listTransactionRoot__pvz4r")
            
            if not elements:
                print("⚠️ Tidak ditemukan dengan class utama, coba fallback...")
                elements = driver.find_elements(By.CLASS_NAME, "mantine-1uguyhf")
            
            if elements:
                print(f"✅ Ditemukan {len(elements)} container pembeli langsung!")
                
                customer_data = []
                for idx, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        if text and ('tabung' in text.lower() and 'lpg' in text.lower()):
                            print(f"✅ Container pembeli {idx+1} ditemukan langsung!")
                            print(f"📝 Data: '{text[:50]}...'")  # Preview singkat
                            
                            customer_data.append({
                                'text': text,
                                'element': element,
                                'element_info': {
                                    'tag_name': element.tag_name,
                                    'id': element.get_attribute('id'),
                                    'class': element.get_attribute('class'),
                                    'index': idx
                                }
                            })
                    except Exception as e:
                        print(f"⚠️ Error membaca container {idx+1}: {str(e)}")
                    continue
            
                if customer_data:
                    print(f"\n✅ DATA LIST PEMBELI BERHASIL DIAMBIL LANGSUNG:")
                    print(f"   📊 Total pembeli: {len(customer_data)}")
                    
                    # Tampilkan preview beberapa pembeli pertama
                    for idx, customer in enumerate(customer_data[:3]):  # Tampilkan 3 pertama saja
                        print(f"\n👥 === PEMBELI {idx+1} (Preview) ===")
                        print(f"   📝 Data: '{customer['text'][:100]}...'")
                        print(f"   🏷️ Tag: {customer['element_info']['tag_name']}")
                        print(f"   🎨 Class: '{customer['element_info']['class'] or 'N/A'}'")
                    
                    if len(customer_data) > 3:
                        print(f"\n... dan {len(customer_data) - 3} pembeli lainnya")
                    
                    return customer_data
                else:
                    print("❌ Tidak ada data pembeli yang valid ditemukan")
                    return None
            else:
                print("❌ Container pembeli tidak ditemukan dengan class yang diketahui")
                return None
                
        except Exception as e:
            print(f"⚠️ Error dengan class selector: {str(e)}")
            
            # Fallback: gunakan XPath berdasarkan class yang sudah diketahui
            print("🔄 Mencoba dengan XPath fallback...")
            try:
                elements = driver.find_elements(By.XPATH, "//div[@class='styles_listTransactionRoot__pvz4r mantine-1uguyhf']")
                
                if not elements:
                    elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles_listTransactionRoot__pvz4r')]")
                
                if elements:
                    print(f"✅ Ditemukan {len(elements)} container pembeli dengan XPath fallback!")
                    
                    customer_data = []
                    for idx, element in enumerate(elements):
                        try:
                            text = element.text.strip()
                            if text and ('tabung' in text.lower() and 'lpg' in text.lower()):
                                customer_data.append({
                                    'text': text,
                                    'element': element,
                                    'element_info': {
                                        'tag_name': element.tag_name,
                                        'id': element.get_attribute('id'),
                                        'class': element.get_attribute('class'),
                                        'index': idx
                                    }
                                })
                        except Exception as e:
                            continue
                    
                    if customer_data:
                        print(f"✅ Data list pembeli berhasil diambil dengan XPath fallback: {len(customer_data)} pembeli")
                        return customer_data
                    else:
                        print("❌ Tidak ada data pembeli yang valid ditemukan dengan XPath fallback")
                        return None
                else:
                    print("❌ Container pembeli tidak ditemukan dengan XPath fallback")
                    return None
            
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return None
                    
    except Exception as e:
        print(f"❌ Error mengambil data list pembeli: {str(e)}")
        return None