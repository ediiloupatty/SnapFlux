"""
Login handling dan fungsi authentication untuk platform merchant Pertamina
File ini menangani proses login dan error handling
"""
import time
from selenium.webdriver.common.by import By
import logging

from .constants import LOGIN_URL, DEFAULT_DELAY
from .driver_setup import setup_driver

# Import enhanced configuration (backward compatible)
try:
    from .config_manager import config_manager
    USE_ENHANCED_CONFIG = True
except ImportError:
    USE_ENHANCED_CONFIG = False

logger = logging.getLogger('automation')

def login_direct(username, pin):
    """
    ============================================
    FUNGSI LOGIN OTOMATIS KE PORTAL MERCHANT
    ============================================
    
    Fungsi ini melakukan login otomatis ke portal merchant Pertamina dengan strategi
    yang sudah terbukti berhasil. Menggunakan direct selector untuk performa optimal.
    
    Proses yang dilakukan:
    1. Setup Chrome WebDriver dengan konfigurasi optimal
    2. Navigasi ke halaman login
    3. Mencari dan mengisi field email/username
    4. Mencari dan mengisi field PIN/password
    5. Mencari dan mengklik tombol login
    6. Deteksi pesan "Gagal Masuk Akun" jika ada
    7. Return WebDriver object jika berhasil
    
    Args:
        username (str): Username berupa email atau nomor HP merchant
        pin (str): PIN untuk authentication ke portal
    
    Returns:
        tuple: (webdriver.Chrome, dict) - WebDriver object dan info gagal masuk akun
               Jika login berhasil: (driver, {'gagal_masuk_akun': False, 'count': 0})
               Jika login gagal: (None, {'gagal_masuk_akun': False, 'count': 0})
               Jika ada gagal masuk akun: (driver, {'gagal_masuk_akun': True, 'count': 1})
    """
    print(f"\n🔐 === LOGIN LANGSUNG UNTUK {username} ===")
    
    driver = None
    try:
        # Setup driver dengan enhanced configuration
        if USE_ENHANCED_CONFIG:
            headless_mode = config_manager.get('headless_mode', False)  # Default false if config not available
        else:
            # Try to get from constants.py as fallback
            try:
                from .constants import HEADLESS_MODE
                headless_mode = HEADLESS_MODE
            except ImportError:
                headless_mode = False  # Default to visible mode if everything fails
        
        driver = setup_driver(headless=headless_mode)
        driver.get(LOGIN_URL)
        
        # Tunggu halaman loading - OPTIMIZED DELAY
        time.sleep(1.0)  # Reduced from DEFAULT_DELAY to 1.0 second
        
        # Langsung cari dan isi email
        print("📧 Mencari dan mengisi field email...")
        email_inputs = driver.find_elements(By.TAG_NAME, "input")
        
        email_filled = False
        for input_field in email_inputs:
            try:
                input_type = input_field.get_attribute("type")
                if input_type in ["text", "email"]:
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
                if any(text in button_text for text in ["MASUK", "LOGIN"]):
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
        
        # Tunggu proses login - OPTIMIZED DELAY
        time.sleep(1.5)  # Reduced from DEFAULT_DELAY to 1.5 seconds
        
        # === DETEKSI CEPAT "GAGAL MASUK AKUN" ===
        gagal_masuk_detected = False
        
        try:
            # Super cepat: langsung cek dengan find_element, jika tidak ada langsung lanjut
            error_element = driver.find_element(By.XPATH, "//h5[contains(@class, 'mantine-Title-root') and text()='Gagal Masuk Akun']")
            if error_element:
                gagal_masuk_detected = True
                print("❌ PESAN 'GAGAL MASUK AKUN' TERDETEKSI!")
        except:
            # Tidak ditemukan - langsung lanjut ke proses selanjutnya tanpa delay
            pass
        
        # === HANDLE GAGAL MASUK AKUN ===
        if gagal_masuk_detected:
            print("🔄 === PROSES RETRY LOGIN SETELAH GAGAL MASUK AKUN ===")
            
            # Tunggu 30 detik - OPTIMIZED
            print("⏳ Menunggu 30 detik...")
            time.sleep(30)
            print("✅ Tunggu 30 detik selesai!")
            
            # Langsung klik tombol MASUK lagi tanpa reload - OPTIMIZED
            print("🔄 Mengklik tombol MASUK lagi tanpa reload...")
            
            retry_clicked = False
            try:
                # Direct approach: cari tombol MASUK langsung dengan XPath
                login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'MASUK') or contains(text(), 'LOGIN')]")
                if login_button.is_displayed() and login_button.is_enabled():
                    login_button.click()
                    print("✅ Tombol MASUK berhasil diklik lagi!")
                    retry_clicked = True
            except:
                # Fallback: cari dengan tag button tapi lebih efisien
                try:
                    login_buttons = driver.find_elements(By.TAG_NAME, "button")
                    for button in login_buttons[:5]:  # Limit hanya 5 button pertama
                        try:
                            button_text = button.text.strip().upper()
                            if any(text in button_text for text in ["MASUK", "LOGIN"]):
                                if button.is_displayed() and button.is_enabled():
                                    button.click()
                                    print("✅ Tombol MASUK berhasil diklik lagi!")
                                    retry_clicked = True
                                    break
                        except:
                            continue
                except:
                    pass
            
            if not retry_clicked:
                print("❌ Gagal mengklik tombol MASUK lagi")
                return None, {'gagal_masuk_akun': gagal_masuk_detected, 'count': 1}
            
            # Tunggu proses login kedua - OPTIMIZED
            print("⏳ Menunggu proses login kedua...")
            time.sleep(1.0)  # Further reduced to 1.0 second
        
        # Cek apakah login berhasil (setelah retry jika ada)
        current_url = driver.current_url
        if "merchant-login" not in current_url:
            print("✅ Login berhasil!")
            return driver, {'gagal_masuk_akun': gagal_masuk_detected, 'count': 1 if gagal_masuk_detected else 0}
        else:
            print("❌ Login gagal - masih di halaman login")
            return None, {'gagal_masuk_akun': gagal_masuk_detected, 'count': 1 if gagal_masuk_detected else 0}
        
    except Exception as e:
        print(f"❌ Error dalam login: {str(e)}")
        if driver:
            driver.quit()
        return None, {'gagal_masuk_akun': False, 'count': 0}


def click_laporan_penjualan_direct(driver):
    """
    Navigasi langsung ke halaman Laporan Penjualan dengan debugging detail
    Mencari dan mengklik tombol/link Laporan Penjualan
    
    Args:
        driver: WebDriver object yang sudah login
        
    Returns:
        bool: True jika berhasil navigasi ke Laporan Penjualan, False jika gagal
    """
    print("📊 === DEBUGGING LAPORAN PENJUALAN ===")
    print("🔍 Mencari elemen Laporan Penjualan...")
    
    try:
        # Tunggu sebentar untuk memastikan halaman sudah load - OPTIMIZED
        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
        
        # Debug: Ambil semua elemen yang mungkin terkait dengan "Laporan Penjualan" - OPTIMIZED (reduced output)
        print("\n🔍 === DEBUGGING SEMUA ELEMEN TERKAIT LAPORAN PENJUALAN ===")
        
        # Cari semua elemen yang mengandung teks "Laporan Penjualan"
        laporan_selectors = [
            "//a[contains(text(), 'Laporan Penjualan')]",
            "//button[contains(text(), 'Laporan Penjualan')]",
            "//span[contains(text(), 'Laporan Penjualan')]",
            "//div[contains(text(), 'Laporan Penjualan')]",
            "//*[contains(text(), 'Laporan Penjualan')]",
            "//a[contains(text(), 'Laporan')]",
            "//button[contains(text(), 'Laporan')]",
            "//span[contains(text(), 'Laporan')]",
            "//div[contains(text(), 'Laporan')]",
            "//*[contains(text(), 'Laporan')]",
            "//a[contains(text(), 'Penjualan')]",
            "//button[contains(text(), 'Penjualan')]",
            "//span[contains(text(), 'Penjualan')]",
            "//div[contains(text(), 'Penjualan')]",
            "//*[contains(text(), 'Penjualan')]"
        ]
        
        found_elements = []
        for i, selector in enumerate(laporan_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"\n📍 Selector {i+1}: {selector}")
                    print(f"   Ditemukan {len(elements)} elemen")
                    
                    for j, element in enumerate(elements[:3]):  # Limit to first 3 elements
                        try:
                            text = element.text.strip()
                            tag_name = element.tag_name
                            is_displayed = element.is_displayed()
                            is_enabled = element.is_enabled()
                            location = element.location
                            size = element.size
                            
                            print(f"   Element {j+1}:")
                            print(f"     - Tag: {tag_name}")
                            print(f"     - Text: '{text}'")
                            print(f"     - Displayed: {is_displayed}")
                            print(f"     - Enabled: {is_enabled}")
                            print(f"     - Location: {location}")
                            print(f"     - Size: {size}")
                            
                            # Coba ambil atribut class dan id
                            try:
                                class_attr = element.get_attribute("class")
                                id_attr = element.get_attribute("id")
                                print(f"     - Class: '{class_attr}'")
                                print(f"     - ID: '{id_attr}'")
                            except:
                                pass
                            
                            found_elements.append({
                                'element': element,
                                'selector': selector,
                                'text': text,
                                'tag': tag_name,
                                'displayed': is_displayed,
                                'enabled': is_enabled,
                                'location': location,
                                'size': size
                            })
                            
                        except Exception as e:
                            print(f"   Element {j+1}: Error membaca properti - {str(e)}")
                            
            except Exception as e:
                print(f"   Selector {i+1}: Error - {str(e)}")
        
        # Debug: Cari semua elemen yang terlihat di halaman - OPTIMIZED (reduced output)
        print(f"\n🔍 === DEBUGGING SEMUA ELEMEN YANG TERLIHAT ===")
        try:
            all_visible_elements = driver.find_elements(By.XPATH, "//*[text()]")
            print(f"Ditemukan {len(all_visible_elements)} elemen dengan teks")
            
            # Filter elemen yang kemungkinan terkait dengan menu/navigasi
            menu_keywords = ['laporan', 'penjualan', 'rekap', 'menu', 'dashboard', 'home']
            relevant_elements = []
            
            for element in all_visible_elements:
                try:
                    text = element.text.strip().lower()
                    if any(keyword in text for keyword in menu_keywords):
                        relevant_elements.append(element)
                except:
                    continue
            
            print(f"Ditemukan {len(relevant_elements)} elemen relevan dengan keyword menu")
            
            for i, element in enumerate(relevant_elements[:5]):  # Limit to 5 for readability
                try:
                    text = element.text.strip()
                    tag_name = element.tag_name
                    print(f"   Element {i+1}: '{text}' ({tag_name})")
                except:
                    pass
                    
        except Exception as e:
            print(f"Error dalam debugging elemen terlihat: {str(e)}")
        
        # Coba klik elemen yang ditemukan
        print(f"\n🖱️ === MENCARI ELEMEN YANG BISA DIKLIK ===")
        laporan_clicked = False
        
        for element_info in found_elements:
            if element_info['displayed'] and element_info['enabled']:
                try:
                    print(f"🖱️ Mencoba klik: '{element_info['text']}'")
                    element_info['element'].click()
                    print("✅ Berhasil mengklik Laporan Penjualan!")
                    laporan_clicked = True
                    break
                except Exception as e:
                    print(f"❌ Gagal klik: {str(e)}")
                    continue
        
        if not laporan_clicked:
            print("❌ Tidak ada elemen Laporan Penjualan yang bisa diklik")
            return False
        
        # Tunggu navigasi ke halaman Laporan Penjualan - OPTIMIZED
        print("⏳ Menunggu navigasi ke halaman Laporan Penjualan...")
        time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
        
        # Verifikasi bahwa sudah berada di halaman Laporan Penjualan
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        print(f"📍 URL saat ini: {current_url}")
        print(f"🔍 Kata kunci dalam halaman: 'laporan'={'laporan' in page_source}, 'penjualan'={'penjualan' in page_source}")
        
        if "laporan" in page_source or "penjualan" in page_source:
            print("✅ Berhasil navigasi ke halaman Laporan Penjualan!")
            return True
        else:
            print("⚠️ Mungkin belum berada di halaman Laporan Penjualan yang benar")
            return True  # Tetap return True karena mungkin strukturnya berbeda
        
    except Exception as e:
        print(f"❌ Error dalam navigasi ke Laporan Penjualan: {str(e)}")
        return False


def click_rekap_penjualan_direct(driver):
    """
    Navigasi langsung ke halaman Rekap Penjualan dengan selector yang sudah diketahui
    Berdasarkan debugging: //div[contains(text(), 'Rekap Penjualan')]
    
    Args:
        driver: WebDriver object yang sudah login
        
    Returns:
        bool: True jika berhasil navigasi ke Rekap Penjualan, False jika gagal
    """
    print("📈 Mengklik Rekap Penjualan...")
    
    try:
        # Tunggu sebentar untuk memastikan halaman sudah load - OPTIMIZED
        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
        
        # Langsung gunakan selector yang sudah diketahui dari debugging
        try:
            rekap_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Rekap Penjualan')]")
            text = rekap_element.text.strip()
            print(f"🔍 Debug Rekap Penjualan 1: Text='{text}', Tag={rekap_element.tag_name}, Class={rekap_element.get_attribute('class')}, ID={rekap_element.get_attribute('id')}")
            
            if rekap_element.is_displayed() and rekap_element.is_enabled():
                rekap_element.click()
                print(f"🔍 Debug Rekap Penjualan Success: XPath='//div[contains(text(), 'Rekap Penjualan')]'")
                print("✅ Berhasil mengklik Rekap Penjualan!")
                
                # Tunggu navigasi ke halaman Rekap Penjualan - OPTIMIZED
                time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                
                # Verifikasi navigasi
                current_url = driver.current_url
                if "saleRecap" in current_url:
                    print("✅ Berhasil navigasi ke halaman Rekap Penjualan!")
                    return True
                else:
                    print("⚠️ URL tidak sesuai, tapi mungkin sudah di halaman yang benar")
                    return True
            else:
                print("❌ Elemen Rekap Penjualan tidak terlihat atau tidak bisa diklik")
                return False
                
        except Exception as e:
            print(f"❌ Error mengklik Rekap Penjualan: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Error dalam navigasi ke Rekap Penjualan: {str(e)}")
        return False


def get_customer_list_direct(driver, pin):
    """
    ============================================
    FUNGSI AMBIL DATA LIST PEMBELI DARI REKAP PENJUALAN
    ============================================
    
    Fungsi ini mengambil data list pembeli dari halaman Rekap Penjualan dan melakukan
    analisis untuk menemukan pembeli dengan >1 tabung yang perlu dibatalkan.
    
    Proses yang dilakukan:
    1. Ambil semua teks dari halaman Rekap Penjualan
    2. Analisis pola data: Nama → HP/NIK → Jenis Pelanggan → X Tabung LPG
    3. Identifikasi pembeli dengan >1 tabung
    4. Untuk setiap pembeli dengan >1 tabung:
       - Klik nama pembeli untuk masuk ke detail
       - Analisis jenis pembelian (Rumah Tangga/Usaha Mikro)
       - Jika Rumah Tangga dengan >1 tabung, lakukan pembatalan transaksi
       - Kembali ke halaman Rekap Penjualan
    5. Refresh halaman dan ulangi proses sampai tidak ada lagi pembeli dengan >1 tabung
    
    Args:
        driver: WebDriver object yang sudah berada di halaman Rekap Penjualan
        pin: PIN dari akun yang sedang login untuk konfirmasi pembatalan
    
    Returns:
        list: List nama pembeli dengan format "Nama Lengkap (Nomor HP/NIK) - X Tabung"
               atau None jika gagal mengambil data
    """
    print("👥 Mengambil data list pembeli...")
    
    try:
        # Tunggu sebentar untuk memastikan halaman sudah load - OPTIMIZED
        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
        
        # Ambil semua teks dari halaman
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        all_texts = []
        
        for element in all_elements:
            text = element.text.strip()
            if text and len(text) > 2:
                all_texts.append(text)
        
        print(f"📊 Ditemukan {len(all_texts)} elemen dengan teks")
        
        # DEBUG: Tampilkan semua teks untuk analisis - OPTIMIZED (reduced output)
        print(f"🔍 Debug: Semua teks yang ditemukan:")
        for idx, text in enumerate(all_texts[:20]):  # Limit to first 20 for readability
            print(f"   {idx:2d}: '{text}'")
        if len(all_texts) > 20:
            print(f"   ... dan {len(all_texts) - 20} teks lainnya")
        
        # Proses data berdasarkan pola yang sudah diketahui
        customer_list = []
        customer_elements = []  # Simpan elemen untuk klik
        i = 0
        
        while i < len(all_texts) - 3:
            current_text = all_texts[i]
            
            # Cek apakah ini kemungkinan nama pembeli
            # Berdasarkan debugging: nama pembeli biasanya huruf besar, panjang, tidak mengandung angka di awal
            if (len(current_text) > 5 and 
                current_text[0].isupper() and 
                not current_text.startswith(('710', '717', '917', '920', '711')) and  # Tambahkan 711
                'Jenis Pelanggan' not in current_text and
                'Tabung LPG' not in current_text and
                'Penjualan' not in current_text and
                'Total' not in current_text and
                'Jumlah' not in current_text and
                'Atur Rentang Waktu' not in current_text and
                'Rekap Penjualan' not in current_text and  # Tambahkan filter
                'icon customer' not in current_text):  # Tambahkan filter
                
                # Cek 3 baris berikutnya untuk memastikan ini adalah data pembeli
                if i + 3 < len(all_texts):
                    next_text1 = all_texts[i + 1]  # Nomor HP/NIK
                    next_text2 = all_texts[i + 2]  # "Jenis Pelanggan"
                    next_text3 = all_texts[i + 3]  # "X Tabung LPG 3Kg"
                    
                    # Validasi berdasarkan pola yang sudah diketahui - PERLUAS VALIDASI
                    if (next_text1.startswith(('710', '717', '917', '920', '711')) and  # Tambahkan 711
                        'Jenis Pelanggan' in next_text2 and
                        'Tabung LPG' in next_text3):
                        
                        # Debug validation messages - OPTIMIZED (reduced output)
                        if idx < 5:  # Only show first 5 validations
                            print(f"🔍 Debug: Validating - NIK: {next_text1}, Jenis: {next_text2}, Tabung: {next_text3}")
                        
                        # Extract jumlah tabung dari next_text3
                        # Contoh: "1 Tabung LPG 3Kg", "3 Tabung LPG 3Kg", "2 Tabung LPG 3Kg"
                        import re
                        tabung_match = re.search(r'(\d+)\s+Tabung LPG', next_text3)
                        jumlah_tabung = tabung_match.group(1) if tabung_match else "?"
                        
                        if idx < 5:  # Only show first 5 extractions
                            print(f"🔍 Debug: Extracted tabung - Raw: '{next_text3}', Match: {jumlah_tabung}, Jumlah: {jumlah_tabung}")
                        
                        # Format data pembeli dengan informasi jumlah tabung
                        customer_info = f"{current_text} ({next_text1}) - {jumlah_tabung} Tabung"
                        if customer_info not in customer_list:
                            customer_list.append(customer_info)
                            
                            # Jika pembeli membeli lebih dari 1 tabung, simpan untuk diklik
                            if jumlah_tabung != "?" and int(jumlah_tabung) > 1:
                                customer_elements.append({
                                    'name': current_text,
                                    'nik': next_text1,
                                    'tabung': jumlah_tabung,
                                    'element': None  # Akan dicari nanti
                                })
                        
                        # Skip 4 baris (nama, HP, jenis pelanggan, detail)
                        i += 4
                        continue
                    else:
                        # Debug mengapa tidak valid - OPTIMIZED (reduced output)
                        if idx < 3:  # Only show first 3 skips
                            print(f"🔍 Debug: Skip '{current_text}' - tidak memenuhi kriteria:")
                            print(f"   - NIK: '{next_text1}' (startswith 710/717/917/920/711: {next_text1.startswith(('710', '717', '917', '920', '711'))})")
                            print(f"   - Jenis: '{next_text2}' (contains 'Jenis Pelanggan': {'Jenis Pelanggan' in next_text2})")
                            print(f"   - Tabung: '{next_text3}' (contains 'Tabung LPG': {'Tabung LPG' in next_text3})")
            
            i += 1
        
        # Jika ada pembeli dengan >1 tabung, cari dan klik mereka
        if customer_elements:
            print(f"\n🔍 Ditemukan {len(customer_elements)} pembeli dengan >1 tabung:")
            for customer in customer_elements:
                print(f"   - {customer['name']} ({customer['nik']}) - {customer['tabung']} Tabung")
            
            print(f"\n🖱️ Mengklik pembeli dengan >1 tabung untuk melihat detail...")
            
            # Process customers in a loop, rechecking after each cancellation
            processed_customers = []
            max_iterations = 5  # Reduced from 10 to 5 to prevent long loops
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                print(f"\n{'='*60}")
                print(f"🔄 Iterasi {iteration}: Mencari ulang pembeli dengan >1 tabung...")
                print(f"{'='*60}")
                
                # Refresh halaman untuk mendapatkan data terbaru - OPTIMIZED
                if iteration > 1:
                    print("🔄 Refresh halaman untuk mendapatkan data terbaru...")
                    driver.refresh()
                    time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                
                # Cari ulang pembeli dengan >1 tabung - OPTIMIZED
                time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                all_elements = driver.find_elements(By.XPATH, "//*[text()]")
                all_texts = []
                
                for element in all_elements:
                    text = element.text.strip()
                    if text and len(text) > 2:
                        all_texts.append(text)
                
                # Re-analyze customer data
                customer_elements_current = []
                i = 0
                
                while i < len(all_texts) - 3:
                    current_text = all_texts[i]
                    
                    if (len(current_text) > 5 and 
                        current_text[0].isupper() and 
                        not current_text.startswith(('710', '717', '917', '920', '711')) and  # Tambahkan 711
                        'Jenis Pelanggan' not in current_text and
                        'Tabung LPG' not in current_text and
                        'Penjualan' not in current_text and
                        'Total' not in current_text and
                        'Jumlah' not in current_text and
                        'Atur Rentang Waktu' not in current_text and
                        'Rekap Penjualan' not in current_text and  # Tambahkan filter
                        'icon customer' not in current_text):  # Tambahkan filter
                        
                        if i + 3 < len(all_texts):
                            next_text1 = all_texts[i + 1]
                            next_text2 = all_texts[i + 2]
                            next_text3 = all_texts[i + 3]
                            
                            if (next_text1.startswith(('710', '717', '917', '920', '711')) and  # Tambahkan 711
                                'Jenis Pelanggan' in next_text2 and
                                'Tabung LPG' in next_text3):
                                
                                import re
                                tabung_match = re.search(r'(\d+)\s+Tabung LPG', next_text3)
                                jumlah_tabung = tabung_match.group(1) if tabung_match else "?"
                                
                                # Check if this customer was already processed
                                customer_key = f"{current_text}_{next_text1}"
                                if customer_key not in processed_customers and jumlah_tabung != "?" and int(jumlah_tabung) > 1:
                                    customer_elements_current.append({
                                        'name': current_text,
                                        'nik': next_text1,
                                        'tabung': jumlah_tabung,
                                        'key': customer_key
                                    })
                                
                                i += 4
                                continue
                    
                    i += 1
                
                print(f"📊 Found {len(customer_elements_current)} pembeli dengan >1 tabung yang belum diproses")
                
                if not customer_elements_current:
                    print("✅ Tidak ada lagi pembeli dengan >1 tabung yang perlu diproses")
                    break
                
                # Process each customer
                for customer in customer_elements_current:
                    try:
                        # Cari elemen yang mengandung nama pembeli dan bisa diklik
                        clickable_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{customer['name']}')]")
                        
                        for element in clickable_elements:
                            try:
                                # Cek apakah elemen bisa diklik dan terlihat
                                if element.is_displayed() and element.is_enabled():
                                    # Cek apakah ini bukan elemen yang sudah kita proses sebelumnya
                                    element_text = element.text.strip()
                                    if customer['name'] in element_text and len(element_text) < 100:  # Pastikan ini nama, bukan teks panjang
                                        print(f"🖱️ Mengklik: {customer['name']} ({customer['tabung']} Tabung)")
                                        print(f"🔍 Debug Customer Click 1: Text='{element_text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                                        element.click()
                                        print(f"🔍 Debug Customer Click Success: XPath='//*[contains(text(), '{customer['name']}')]'")
                                        
                                        # Tunggu halaman detail load - OPTIMIZED
                                        time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                                        
                                        # Ambil detail informasi dari halaman "Identitas Pelanggan"
                                        detail_info = get_customer_detail_info(driver)
                                        
                                        if detail_info:
                                            print(f"📋 Detail untuk {customer['name']}:")
                                            print(f"   - Nama: {detail_info.get('nama', 'N/A')}")
                                            print(f"   - NIK: {detail_info.get('nik', 'N/A')}")
                                            print(f"   - Status: {detail_info.get('status', 'N/A')}")
                                            print(f"   - Total Pembelian: {detail_info.get('total_pembelian', 'N/A')}")
                                            print(f"   - Riwayat Transaksi: {len(detail_info.get('riwayat', []))} transaksi")
                                            
                                            # Tampilkan summary sederhana jenis pembelian
                                            transaksi_per_jenis = detail_info.get('transaksi_per_jenis', {})
                                            
                                            if transaksi_per_jenis:
                                                print(f"   📊 Summary Pembelian:")
                                                
                                                # Tampilkan detail transaksi untuk analisis
                                                if detail_info.get('riwayat'):
                                                    print(f"   📋 Detail Riwayat Transaksi:")
                                                    riwayat_count = 0
                                                    for text in detail_info['riwayat'][:10]:  # Batasi untuk readability
                                                        if 'Tabung LPG' in text or 'Rumah Tangga' in text or 'Rp' in text:
                                                            riwayat_count += 1
                                                            print(f"      {riwayat_count}. {text}")
                                                
                                                # Cek apakah ada "Usaha Mikro" - jika ya, skip
                                                if 'Usaha Mikro' in transaksi_per_jenis:
                                                    print(f"   ⏭️ Skip {customer['name']} - Jenis Usaha Mikro")
                                                    # Tambahkan customer ke processed_customers untuk menghindari loop
                                                    processed_customers.append(customer['key'])
                                                    # Kembali ke halaman sebelumnya tanpa klik transaksi
                                                    driver.back()
                                                    time.sleep(2.0)
                                                    continue  # Lanjut ke customer berikutnya
                                                
                                                # Focus hanya pada "Rumah Tangga"
                                                rumah_tangga_data = transaksi_per_jenis.get('Rumah Tangga')
                                                if rumah_tangga_data and rumah_tangga_data['jumlah_tabung'] > 1:
                                                    print(f"   🎯 Focus pada Rumah Tangga: {rumah_tangga_data['jumlah_tabung']} tabung")
                                                    
                                                    # ANALISIS SKENARIO PEMBATALAN BERDASARKAN JUMLAH INPUTAN
                                                    jumlah_transaksi = rumah_tangga_data['jumlah_transaksi']
                                                    jumlah_tabung = rumah_tangga_data['jumlah_tabung']
                                                    
                                                    if jumlah_transaksi == 1 and jumlah_tabung > 1:
                                                        # SKENARIO 1: 2 TABUNG - 1 INPUTAN (SALAH INPUTAN)
                                                        print(f"   🔍 SKENARIO 1: {jumlah_tabung} Tabung - {jumlah_transaksi} Inputan")
                                                        print(f"   📋 AKSI: BATALKAN SEMUA (Salah Inputan - seharusnya 1 tabung)")
                                                        
                                                        # Batalkan transaksi tunggal yang salah inputan
                                                        cancel_result, cancelled_position = click_rumah_tangga_transaction(driver, pin)
                                                        if cancel_result:
                                                            print(f"   ✅ Berhasil membatalkan transaksi salah inputan untuk {customer['name']}")
                                                            # Kembali ke halaman Rekap Penjualan - OPTIMIZED
                                                            driver.back()
                                                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                                                            # Kembali sekali lagi ke halaman Rekap Penjualan
                                                            driver.back()
                                                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                                                            # Mark as processed
                                                            processed_customers.append(customer['key'])
                                                            # Break inner loop to recheck page
                                                            break
                                                        else:
                                                            print(f"   ❌ Gagal membatalkan transaksi salah inputan untuk {customer['name']}")
                                                        
                                                        # Kembali ke halaman Rekap Penjualan
                                                        driver.back()
                                                        time.sleep(2.0)
                                                        driver.back()
                                                        time.sleep(2.0)
                                                        # Break inner loop to recheck page
                                                        break
                                                    
                                                    elif jumlah_transaksi > 1 and jumlah_tabung > 1:
                                                        # SKENARIO 2: 2 TABUNG - 2 INPUTAN (DUPLIKASI INPUTAN)
                                                        print(f"   🔍 SKENARIO 2: {jumlah_tabung} Tabung - {jumlah_transaksi} Inputan")
                                                        print(f"   📋 AKSI: BATALKAN SALAH SATU (Duplikasi Inputan)")
                                                        
                                                        # Implementasi multiple cancellations dalam detail page
                                                        cancelled_positions = set()
                                                        cancellation_count = 0
                                                        max_cancellations = 5  # Reduced from 10 to 5
                                                        
                                                        print(f"   🔄 Memulai proses multiple cancellations untuk {customer['name']}...")
                                                        
                                                        while cancellation_count < max_cancellations:
                                                            print(f"   🔄 Cancellation attempt {cancellation_count + 1}...")
                                                            
                                                            # Batalkan salah satu transaksi dengan tracking posisi
                                                            cancel_result, cancelled_position = click_rumah_tangga_transaction(driver, pin, cancelled_positions)
                                                            
                                                            if cancel_result:
                                                                cancelled_positions.add(cancelled_position)
                                                                cancellation_count += 1
                                                                print(f"   ✅ Berhasil membatalkan transaksi ke-{cancellation_count} untuk {customer['name']}")
                                                                
                                                                # Cek berapa transaksi aktif yang tersisa di halaman detail saat ini
                                                                try:
                                                                    # Tunggu sebentar untuk memastikan DOM sudah stabil setelah pembatalan - OPTIMIZED
                                                                    time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                                                                    
                                                                    # Refresh elemen untuk menghindari stale element reference
                                                                    print(f"   🔄 Refresh elemen setelah pembatalan untuk menghitung transaksi aktif...")
                                                                    
                                                                    # Ambil semua text dari halaman detail saat ini dengan fresh elements
                                                                    all_texts_detail = driver.find_elements(By.XPATH, "//*[text()]")
                                                                    all_texts_detail = [elem.text for elem in all_texts_detail if elem.text.strip()]
                                                                    
                                                                    # Hitung transaksi Rumah Tangga yang masih aktif
                                                                    rumah_tangga_count = count_active_rumah_tangga_transactions(all_texts_detail)
                                                                    print(f"   📊 Transaksi aktif tersisa: {rumah_tangga_count}")
                                                                    
                                                                    # PERBAIKAN LOGIKA: Berhenti berdasarkan target tabung yang diinginkan
                                                                    # Target: Sisa 1 tabung, jadi harus membatalkan (total_tabung - 1) transaksi
                                                                    target_remaining = 1  # Target sisa 1 tabung
                                                                    expected_cancellations = int(customer['tabung']) - target_remaining
                                                                    print(f"   🔍 Debug: Target sisa {target_remaining} tabung, harus membatalkan {expected_cancellations} transaksi")
                                                                    
                                                                    if cancellation_count >= expected_cancellations:
                                                                        print(f"   ✅ Target tercapai! Sudah membatalkan {cancellation_count} transaksi (target: {expected_cancellations})")
                                                                        print(f"   ✅ Sisa {rumah_tangga_count} transaksi = {rumah_tangga_count} tabung (sesuai target)")
                                                                        # Kembali ke halaman Rekap Penjualan - OPTIMIZED
                                                                        driver.back()
                                                                        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                                                                        driver.back()
                                                                        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                                                                        # Mark as processed
                                                                        processed_customers.append(customer['key'])
                                                                        # Break inner loop to recheck page
                                                                        break
                                                                    else:
                                                                        remaining_cancellations = expected_cancellations - cancellation_count
                                                                        print(f"   🔄 Masih perlu membatalkan {remaining_cancellations} transaksi lagi (sisa {rumah_tangga_count} transaksi)")
                                                                        continue
                                                                        
                                                                except Exception as count_e:
                                                                    print(f"   ⚠️ Error saat menghitung transaksi aktif: {str(count_e)}")
                                                                    print(f"   🔄 Menggunakan strategi alternatif - cek berdasarkan jumlah pembatalan")
                                                                    
                                                                    # STRATEGI ALTERNATIF: Berhenti berdasarkan jumlah pembatalan yang sudah dilakukan
                                                                    # Target: Sisa 1 tabung, jadi harus membatalkan (total_tabung - 1) transaksi
                                                                    target_remaining = 1  # Target sisa 1 tabung
                                                                    expected_cancellations = int(customer['tabung']) - target_remaining
                                                                    print(f"   🔍 Debug: Expected cancellations untuk {customer['name']}: {expected_cancellations} (target sisa {target_remaining} tabung)")
                                                                    
                                                                    if cancellation_count >= expected_cancellations:
                                                                        print(f"   ✅ Sudah membatalkan {cancellation_count} transaksi (target: {expected_cancellations}) - selesai")
                                                                        driver.back()
                                                                        time.sleep(2.0)
                                                                        driver.back()
                                                                        time.sleep(2.0)
                                                                        processed_customers.append(customer['key'])
                                                                        break
                                                                    else:
                                                                        remaining_cancellations = expected_cancellations - cancellation_count
                                                                        print(f"   🔄 Masih perlu membatalkan {remaining_cancellations} transaksi lagi")
                                                                        continue
                                                            else:
                                                                print(f"   ❌ Gagal membatalkan transaksi ke-{cancellation_count + 1} untuk {customer['name']}")
                                                                # Jika gagal, kembali ke Rekap Penjualan
                                                                driver.back()
                                                                time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                                                                driver.back()
                                                                time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                                                                break
                                                        
                                                        # Jika loop selesai tanpa break, berarti sudah mencapai max_cancellations
                                                        if cancellation_count >= max_cancellations:
                                                            print(f"   ⚠️ Mencapai batas maksimal cancellations ({max_cancellations}) untuk {customer['name']}")
                                                            driver.back()
                                                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second

                                                            driver.back()
                                                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second

                                                            processed_customers.append(customer['key'])
                                                        
                                                        # Break inner loop to recheck page
                                                        break
                                                        if cancel_result:
                                                            print(f"   ✅ Berhasil membatalkan salah satu transaksi duplikasi untuk {customer['name']}")
                                                            # Kembali ke halaman Rekap Penjualan
                                                            driver.back()
                                                            time.sleep(2.0)
                                                            # Kembali sekali lagi ke halaman Rekap Penjualan
                                                            driver.back()
                                                            time.sleep(2.0)
                                                            # Mark as processed
                                                            processed_customers.append(customer['key'])
                                                            # Break inner loop to recheck page
                                                            break
                                                        else:
                                                            print(f"   ❌ Gagal membatalkan transaksi duplikasi untuk {customer['name']}")
                                                        
                                                        # Kembali ke halaman Rekap Penjualan
                                                        driver.back()
                                                        time.sleep(2.0)
                                                        driver.back()
                                                        time.sleep(2.0)
                                                        # Break inner loop to recheck page
                                                        break
                                                    
                                                    else:
                                                        # SKENARIO LAIN: Tidak perlu dibatalkan
                                                        print(f"   ⏭️ SKENARIO LAIN: {jumlah_tabung} Tabung - {jumlah_transaksi} Inputan")
                                                        print(f"   📋 AKSI: SKIP (Tidak perlu dibatalkan)")
                                                        # Tambahkan customer ke processed_customers untuk menghindari loop
                                                        processed_customers.append(customer['key'])
                                                        driver.back()
                                                        time.sleep(2.0)
                                                        continue
                                                    
                                                    # Tampilkan summary untuk jenis lain
                                                    for jenis, data in transaksi_per_jenis.items():
                                                        if jenis != 'Rumah Tangga':
                                                            print(f"      {customer['name']}: {data['jumlah_tabung']} tabung - {jenis}")
                                        
                                        # Kembali ke halaman sebelumnya
                                        driver.back()
                                        time.sleep(2.0)
                                        continue  # Lanjut ke customer berikutnya
                            except Exception as e:
                                print(f"❌ Error mengklik {customer['name']}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        print(f"❌ Error mencari elemen untuk {customer['name']}: {str(e)}")
                        continue
        
        # Tidak ada batasan - ambil semua data pembeli yang ada
        
        if customer_list:
            print(f"\n✅ Berhasil mengambil {len(customer_list)} data pembeli")
            return customer_list
        else:
            print("⚠️ Tidak ditemukan data pembeli")
            return None
        
    except Exception as e:
        print(f"❌ Error dalam mengambil data pembeli: {str(e)}")
        return None


def click_rumah_tangga_transaction(driver, pin, cancelled_positions=None):
    """
    ============================================
    FUNGSI KLIK TRANSAKSI RUMAH TANGGA DENGAN SKIP TRANSAKSI DIBATALKAN
    ============================================
    
    Fungsi ini mengklik transaksi Rumah Tangga dengan strategi skip transaksi yang sudah dibatalkan
    dan selalu memilih transaksi dari posisi paling bawah (yang belum dibatalkan).
    
    Proses yang dilakukan:
    1. Ambil semua elemen "Rumah Tangga" dari halaman
    2. Filter elemen yang TIDAK memiliki "Transaksi Dibatalkan" di parent container
    3. Skip transaksi yang posisinya sudah pernah dibatalkan
    4. Pilih transaksi dari posisi paling bawah (index terakhir)
    5. Jika gagal, coba transaksi kedua dari bawah, ketiga dari bawah, dst
    6. Klik parent element untuk masuk ke detail transaksi
    7. Lakukan pembatalan transaksi
    
    Args:
        driver: WebDriver object yang sudah berada di halaman detail pelanggan
        pin: PIN dari akun yang sedang login
        cancelled_positions: Set berisi posisi elemen yang sudah dibatalkan
        
    Returns:
        tuple: (bool, int) - (True jika berhasil, posisi elemen jika berhasil)
    """
    try:
        print(f"🖱️ Mencari dan mengklik transaksi Rumah Tangga (skip yang sudah dibatalkan)...")
        
        # Tunggu halaman load - OPTIMIZED
        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
        
        # Debug: Tampilkan informasi halaman saat ini
        current_url = driver.current_url
        print(f"🔍 Debug: URL saat ini: {current_url}")
        
        # Ambil semua elemen "Rumah Tangga" dengan direct selector
        print(f"🔍 Debug: Mencari semua elemen 'Rumah Tangga'...")
        rumah_tangga_elements = driver.find_elements(By.XPATH, "//*[text()='Rumah Tangga']")
        print(f"🔍 Debug: Ditemukan {len(rumah_tangga_elements)} elemen 'Rumah Tangga'")
        
        if not rumah_tangga_elements:
            print(f"❌ Tidak ditemukan elemen 'Rumah Tangga'")
            return False, None
        
        # Initialize cancelled_positions if None
        if cancelled_positions is None:
            cancelled_positions = set()
        
        # Filter: Skip elemen yang memiliki "Transaksi Dibatalkan" di parent/sibling
        active_transactions = []
        cancelled_count = 0
        
        for i, element in enumerate(rumah_tangga_elements):
            try:
                # Debug posisi detail untuk setiap elemen - OPTIMIZED (reduced output)
                element_location = element.location
                element_size = element.size
                element_class = element.get_attribute('class')
                element_id = element.get_attribute('id')
                
                if i < 3:  # Only show first 3 positions
                    print(f"🔍 Debug Posisi Detail {i+1}: Location={element_location}, Size={element_size}, Class={element_class}, ID={element_id}")
                
                # Cek parent container untuk text "Transaksi Dibatalkan" dengan berbagai variasi
                parent = element.find_element(By.XPATH, "../..")
                parent_text = parent.text
                
                # Debug parent text untuk analisis - OPTIMIZED (reduced output)
                if i < 3:  # Only show first 3 parent texts
                    print(f"🔍 Debug Parent Text {i+1}: '{parent_text[:100]}...' (truncated)")
                
                # Cek berbagai variasi text pembatalan
                cancelled_keywords = [
                    "Transaksi Dibatalkan",
                    "TRANSAKSI DIBATALKAN", 
                    "Dibatalkan",
                    "DIBATALKAN",
                    "Salah Inputan",
                    "SALAH INPUTAN"
                ]
                
                is_cancelled = any(keyword in parent_text for keyword in cancelled_keywords)
                
                if is_cancelled:
                    cancelled_count += 1
                    if i < 3:  # Only show first 3 cancellations
                        print(f"🔍 Debug: Transaksi {i+1} sudah dibatalkan - SKIP (detected keyword)")
                elif cancelled_positions and i in cancelled_positions:
                    cancelled_count += 1
                    if i < 3:  # Only show first 3 cancellations
                        print(f"🔍 Debug: Transaksi {i+1} sudah dibatalkan sebelumnya (posisi {i}) - SKIP")
                else:
                    # Simpan elemen aktif tanpa perlu klik untuk mendapatkan URL
                    active_transactions.append({
                        'element': element,
                        'index': i,
                        'parent': parent,
                        'location': element_location,
                        'size': element_size
                    })
                    if i < 3:  # Only show first 3 active transactions
                        print(f"🔍 Debug: Transaksi {i+1} aktif - TERSEDIA (Location: {element_location})")
                        
            except Exception as e:
                print(f"🔍 Debug: Error cek transaksi {i+1}: {str(e)}")
                # Jika error, anggap sebagai transaksi aktif
                active_transactions.append({
                    'element': element,
                    'index': i,
                    'parent': None,
                    'location': None,
                    'size': None
                })
        
        print(f"📊 Summary: {len(rumah_tangga_elements)} total, {cancelled_count} dibatalkan, {len(active_transactions)} aktif")
        
        if not active_transactions:
            print(f"❌ Tidak ada transaksi aktif yang bisa diproses")
            return False, None
        
        # Ambil transaksi dari posisi paling bawah (terakhir) dan coba fallback jika gagal
        for attempt in range(len(active_transactions)):
            try:
                # Mulai dari paling bawah (index terakhir)
                target_index = len(active_transactions) - 1 - attempt
                target_transaction = active_transactions[target_index]
                target_element = target_transaction['element']
                
                print(f"🎯 Mencoba transaksi dari posisi {target_index + 1} dari bawah (index {target_transaction['index'] + 1})...")
                
                # Debug posisi detail untuk transaksi yang akan diklik
                target_location = target_transaction.get('location', target_element.location)
                target_size = target_transaction.get('size', target_element.size)
                print(f"🔍 Debug Target Position: Index={target_transaction['index']}, Location={target_location}, Size={target_size}")
                
                # Validasi elemen
                if not target_element.is_displayed() or not target_element.is_enabled():
                    print(f"⚠️ Transaksi {target_index + 1} tidak dapat diklik - coba berikutnya")
                    continue
                
                # Klik parent element untuk masuk ke detail transaksi
                if target_transaction['parent']:
                    parent = target_transaction['parent']
                else:
                    parent = target_element.find_element(By.XPATH, "..")
                
                if parent.is_displayed() and parent.is_enabled():
                    print(f"🖱️ Mengklik transaksi dari posisi paling bawah (attempt {attempt + 1})...")
                    print(f"🔍 Debug Rumah Tangga Bottom-Up: Text='Rumah Tangga', Tag={target_element.tag_name}, Class={target_element.get_attribute('class')}, ID={target_element.get_attribute('id')}, Location={target_location}, Size={target_size}")
                    print(f"🔍 Debug Parent Element: Tag={parent.tag_name}, Class={parent.get_attribute('class')}, Location={parent.location}, Size={parent.size}")
                    
                    # Simpan URL sebelum klik untuk perbandingan
                    url_before = driver.current_url
                    print(f"🔍 Debug: URL sebelum klik: {url_before}")
                    
                    parent.click()
                    time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                    
                    # Cek apakah URL berubah setelah klik
                    url_after = driver.current_url
                    print(f"🔍 Debug: URL setelah klik: {url_after}")
                    
                    # Jika URL tidak berubah atau tidak mengandung transactionId, coba klik elemen yang lebih spesifik
                    if url_after == url_before or 'transactionId=' not in url_after:
                        print(f"⚠️ URL tidak berubah atau tidak ada transactionId - coba klik elemen yang lebih spesifik...")
                        
                        # Coba klik elemen Rumah Tangga langsung
                        try:
                            target_element.click()
                            time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                            url_after_retry = driver.current_url
                            print(f"🔍 Debug: URL setelah retry klik elemen langsung: {url_after_retry}")
                            
                            if url_after_retry != url_after and 'transactionId=' in url_after_retry:
                                print(f"✅ Retry berhasil - URL berubah dengan transactionId")
                                url_after = url_after_retry
                            else:
                                print(f"⚠️ Retry juga gagal - URL masih tidak berubah")
                        except Exception as retry_e:
                            print(f"⚠️ Error saat retry klik elemen langsung: {str(retry_e)}")
                    
                    # Verifikasi navigasi dan lakukan pembatalan
                    if verify_transaction_detail_page(driver):
                        print(f"✅ Berhasil masuk ke detail transaksi dari posisi paling bawah")
                        
                        # Cek apakah transaksi ini sudah dibatalkan dengan melihat page source
                        page_source = driver.page_source.lower()
                        cancelled_keywords = [
                            "transaksi dibatalkan",
                            "dibatalkan", 
                            "salah inputan",
                            "transaction cancelled"
                        ]
                        
                        is_already_cancelled = any(keyword in page_source for keyword in cancelled_keywords)
                        
                        if is_already_cancelled:
                            print(f"⚠️ Transaksi ini sudah dibatalkan sebelumnya - SKIP")
                            # Kembali ke halaman sebelumnya
                            driver.back()
                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                            # Mark posisi ini sebagai dibatalkan
                            cancelled_positions.add(target_transaction['index'])
                            # Refresh elemen karena DOM sudah berubah
                            print(f"🔄 Refresh elemen setelah skip transaksi dibatalkan...")
                            return click_rumah_tangga_transaction(driver, pin, cancelled_positions)
                        
                        # Ambil transaction ID dari URL saat ini
                        current_url = driver.current_url
                        import re
                        transaction_id_match = re.search(r'transactionId=([^&]+)', current_url)
                        transaction_id = transaction_id_match.group(1) if transaction_id_match else None
                        
                        # Lakukan pembatalan transaksi
                        cancel_result = cancel_transaction(driver, pin)
                        if cancel_result:
                            # Return posisi elemen jika berhasil
                            return True, target_transaction['index']
                        else:
                            return False, None
                    else:
                        print(f"⚠️ Tidak berhasil masuk ke halaman detail transaksi dari posisi {target_index + 1}")
                        # Kembali ke halaman sebelumnya untuk coba transaksi lain
                        try:
                            driver.back()
                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                            
                            # Verifikasi bahwa kita kembali ke halaman yang benar
                            current_url = driver.current_url
                            if 'rekap' not in current_url.lower() and 'saleRecap' not in current_url.lower():
                                print(f"⚠️ Tidak kembali ke halaman Rekap Penjualan - coba navigasi eksplisit...")
                                # Coba navigasi eksplisit ke Rekap Penjualan
                                if not click_rekap_penjualan_direct(driver):
                                    print(f"❌ Gagal navigasi ke Rekap Penjualan - mungkin perlu refresh halaman")
                                    # Jika gagal, refresh halaman dan coba lagi
                                    driver.refresh()
                                    time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                                    click_rekap_penjualan_direct(driver)
                        except Exception as nav_e:
                            print(f"⚠️ Error saat navigasi kembali: {str(nav_e)}")
                            # Jika error, refresh halaman
                            try:
                                driver.refresh()
                                time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                                click_rekap_penjualan_direct(driver)
                            except Exception as refresh_e:
                                print(f"❌ Error saat refresh halaman: {str(refresh_e)}")
                        
                        continue
                else:
                    print(f"❌ Parent element tidak dapat diklik untuk posisi {target_index + 1}")
                    continue
                    
            except Exception as e:
                print(f"🔍 Debug: Error dengan transaksi posisi {target_index + 1}: {str(e)}")
                if "stale element reference" in str(e).lower():
                    print(f"🔄 Stale element detected - refresh elemen dan coba lagi...")
                    return click_rumah_tangga_transaction(driver, pin, cancelled_positions)
                elif "element click intercepted" in str(e).lower():
                    print(f"🔄 Element click intercepted - coba strategi alternatif...")
                    try:
                        # Strategi alternatif 1: Scroll ke elemen dan gunakan JavaScript click
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target_transaction['element'])
                        time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                        
                        # Coba klik dengan JavaScript
                        driver.execute_script("arguments[0].click();", target_transaction['element'])
                        print(f"✅ Berhasil klik menggunakan JavaScript")
                        
                        # Tunggu dan verifikasi apakah berhasil masuk ke halaman detail
                        time.sleep(1.5)  # Reduced from 3.0 to 1.5 seconds
                        current_url = driver.current_url
                        if 'transactionId=' in current_url:
                            print(f"✅ Berhasil masuk ke halaman detail transaksi")
                            return cancel_transaction(driver, pin)
                        else:
                            print(f"⚠️ JavaScript click tidak berhasil masuk ke halaman detail")
                            continue
                            
                    except Exception as js_error:
                        print(f"❌ JavaScript click juga gagal: {str(js_error)}")
                        
                        # Strategi alternatif 2: Coba klik parent element
                        try:
                            parent_element = target_transaction['element'].find_element(By.XPATH, "./..")
                            driver.execute_script("arguments[0].click();", parent_element)
                            print(f"✅ Berhasil klik parent element menggunakan JavaScript")
                            time.sleep(1.0)  # Reduced from 2.0 to 1.0 second
                            return cancel_transaction(driver, pin)
                        except Exception as parent_error:
                            print(f"❌ Parent element click juga gagal: {str(parent_error)}")
                            continue
                continue
        
        print(f"❌ Semua transaksi aktif gagal diklik")
        return False, None
        
    except Exception as e:
        print(f"❌ Error mengklik transaksi Rumah Tangga: {str(e)}")
        return False, None


def count_active_rumah_tangga_transactions(all_texts):
    """
    Menghitung jumlah transaksi Rumah Tangga yang masih aktif (belum dibatalkan)
    
    Args:
        all_texts: List berisi semua text dari halaman
        
    Returns:
        int: Jumlah transaksi Rumah Tangga yang aktif
    """
    rumah_tangga_count = 0
    try:
        print(f"   🔍 Debug: Menganalisis {len(all_texts)} teks untuk jenis pembelian...")
        
        for i, text in enumerate(all_texts):
            if text == "Rumah Tangga":
                is_cancelled = False
                
                # Cek dalam range 10 elemen sebelum dan sesudah untuk keyword pembatalan
                for j in range(max(0, i-10), min(len(all_texts), i+10)):
                    check_text = all_texts[j].lower()
                    if any(keyword in check_text for keyword in [
                        "transaksi dibatalkan", "dibatalkan", "cancel", "batal",
                        "pembatalan", "sudah dibatalkan", "status dibatalkan"
                    ]):
                        is_cancelled = True
                        print(f"   🔍 Debug: Transaksi Rumah Tangga di index {i} DIBATALKAN (keyword: '{all_texts[j]}')")
                        break
                
                if not is_cancelled:
                    rumah_tangga_count += 1
                    print(f"   🔍 Debug: Transaksi Rumah Tangga di index {i} AKTIF")
        
        print(f"   🔍 Debug: Total transaksi Rumah Tangga aktif: {rumah_tangga_count}")
        
    except Exception as e:
        print(f"   ⚠️ Error dalam count_active_rumah_tangga_transactions: {str(e)}")
        # Jika error, return jumlah yang lebih tinggi untuk safety (agar tidak berhenti prematur)
        rumah_tangga_count = 2
    
    return rumah_tangga_count


def verify_transaction_detail_page(driver):
    """
    Verifikasi apakah sudah masuk ke halaman detail transaksi dengan prioritas URL-based check
    
    Args:
        driver: WebDriver object
        
    Returns:
        bool: True jika sudah di halaman detail transaksi, False jika belum
    """
    try:
        # Tunggu sebentar untuk memastikan halaman sudah load
        time.sleep(2.0)
        
        # Ambil URL dan page source saat ini
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        print(f"🔍 Debug: Verifikasi halaman detail transaksi...")
        print(f"🔍 Debug: URL saat ini: {current_url}")
        
        # Cek apakah URL mengandung transactionId sebagai indikator utama
        has_transaction_id = 'transactionid=' in current_url.lower()
        print(f"🔍 Debug: URL contains 'transactionId': {has_transaction_id}")
        
        # Verifikasi berdasarkan berbagai indikator
        page_indicators = [
            "informasi transaksi",
            "rincian", 
            "pembayaran",
            "total pembayaran",
            "item pembelian",
            "detail transaksi",
            "transaction detail",
            "status transaksi"
        ]
        
        found_indicators = [indicator for indicator in page_indicators if indicator in page_source]
        print(f"🔍 Debug: Page source contains 'informasi transaksi': {'informasi transaksi' in page_source}")
        print(f"🔍 Debug: Page source contains 'rincian': {'rincian' in page_source}")
        print(f"🔍 Debug: Found page indicators: {found_indicators}")
        
        # Jika URL mengandung transactionId, anggap sudah di halaman yang benar
        if has_transaction_id:
            print(f"✅ Berhasil masuk ke halaman detail transaksi (berdasarkan URL dengan transactionId)!")
            return True
        
        # Jika ada minimal 2 indikator halaman detail transaksi
        if len(found_indicators) >= 2:
            print(f"✅ Berhasil masuk ke halaman detail transaksi!")
            return True
        
        # Jika hanya ada 1 indikator, cek lebih detail
        if len(found_indicators) == 1:
            print(f"⚠️ Hanya ditemukan 1 indikator: {found_indicators[0]}")
            # Cek apakah ada elemen yang menunjukkan ini bukan halaman utama
            if "rekap" not in current_url.lower() and "saleRecap" not in current_url.lower():
                print(f"✅ Berhasil masuk ke halaman detail transaksi (berdasarkan indikator tunggal)!")
                return True
        
        print(f"❌ Belum masuk ke halaman detail transaksi")
        print(f"🔍 Debug: URL tidak mengandung transactionId dan hanya {len(found_indicators)} indikator ditemukan")
        return False
        
    except Exception as e:
        print(f"❌ Error verifikasi halaman detail transaksi: {str(e)}")
        return False


def cancel_transaction(driver, pin):
    """
    ============================================
    FUNGSI PEMBATALAN TRANSAKSI OTOMATIS
    ============================================
    
    Fungsi ini melakukan pembatalan transaksi secara otomatis dengan menggunakan
    direct selector yang sudah dioptimasi berdasarkan debugging sebelumnya.
    
    Proses yang dilakukan:
    1. Klik tombol "Rincian" untuk membuka detail transaksi
    2. Klik tombol "BATALKAN" untuk memulai proses pembatalan
    3. Klik tombol "YA, BATALKAN TRANSAKSI" untuk konfirmasi
    4. Isi alasan pembatalan dengan text "Salah Inputan"
    5. Isi PIN untuk konfirmasi pembatalan
    6. Klik tombol "BATALKAN TRANSAKSI" untuk menyelesaikan pembatalan
    
    Semua langkah menggunakan direct selector untuk performa optimal dan
    memiliki fallback mechanism jika selector utama gagal.
    
    Args:
        driver: WebDriver object yang sudah berada di halaman detail transaksi
        pin: PIN dari akun untuk konfirmasi pembatalan
    
    Returns:
        bool: True jika pembatalan berhasil, False jika gagal
    """
    
    print("🔄 Memulai proses pembatalan transaksi...")
    
    try:
        
        # Ambil informasi detail transaksi terlebih dahulu
        get_transaction_detail_info(driver)
        
        # === LANGKAH 1: Klik "Rincian" dengan direct class selector ===
        print(f"🔍 Langkah 1: Mencari dan mengklik 'Rincian'...")
        try:
            # Direct class selector berdasarkan terminal output
            element = driver.find_element(By.CLASS_NAME, "styles_btnDetail__OqNm0")
            text = element.text.strip()
            print(f"🔍 Debug Rincian 1: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
            
            if element.is_displayed() and element.is_enabled():
                print(f"🖱️ Mengklik 'Rincian'...")
                print(f"🔍 Debug Rincian Success: Class='styles_btnDetail__OqNm0'")
                element.click()
                time.sleep(2.0)
            else:
                print(f"❌ Elemen Rincian tidak dapat diklik")
                return False
        except Exception as e:
            print(f"❌ Error dengan direct class selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath text-based
            try:
                element = driver.find_element(By.XPATH, "//*[contains(text(), 'Rincian')][1]")
                text = element.text.strip()
                print(f"🔍 Debug Rincian Fallback: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                
                if element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik 'Rincian' (fallback)...")
                    print(f"🔍 Debug Rincian Fallback Success: XPath='//*[contains(text(), 'Rincian')][1]'")
                    element.click()
                    time.sleep(2.0)
                else:
                    print(f"❌ Elemen Rincian fallback tidak dapat diklik")
                    return False
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return False
        
        # === LANGKAH 2: Klik "BATALKAN" dengan direct class selector ===
        print(f"🔍 Langkah 2: Mencari tombol 'Batalkan'...")
        try:
            # Direct class selector berdasarkan terminal output
            element = driver.find_element(By.CLASS_NAME, "styles_btnCancel__iT8X5")
            text = element.text.strip()
            print(f"🔍 Debug Batalkan 1: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
            
            if element.is_displayed() and element.is_enabled():
                print(f"🖱️ Mengklik tombol 'BATALKAN'...")
                print(f"🔍 Debug Batalkan Success: Class='styles_btnCancel__iT8X5'")
                
                # Scroll ke elemen untuk memastikan terlihat
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1.0)
                
                # Coba klik dengan JavaScript jika normal click gagal
                try:
                    element.click()
                    print(f"✅ Berhasil mengklik dengan normal click")
                except Exception as click_error:
                    print(f"⚠️ Normal click gagal, mencoba JavaScript click: {str(click_error)}")
                    driver.execute_script("arguments[0].click();", element)
                    print(f"✅ Berhasil mengklik dengan JavaScript click")
                
                time.sleep(2.0)
            else:
                print(f"❌ Elemen BATALKAN tidak dapat diklik")
                return False
        except Exception as e:
            print(f"❌ Error dengan direct class selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath text-based
            try:
                elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Batalkan')]")
                print(f"🔍 Debug: Selector '//*[contains(text(), 'Batalkan')]' menemukan {len(elements)} elemen")
                
                for i, element in enumerate(elements):
                    text = element.text.strip()
                    print(f"🔍 Debug Batalkan Fallback {i+1}: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                    
                    # Cek apakah ini tombol "BATALKAN" yang benar
                    if (text == "BATALKAN" and 
                        element.is_displayed() and 
                        element.is_enabled()):
                        print(f"🖱️ Mengklik tombol 'BATALKAN' (fallback)...")
                        print(f"🔍 Debug Batalkan Fallback Success: XPath='//*[contains(text(), 'Batalkan')][{i+1}]'")
                        
                        # Scroll ke elemen untuk memastikan terlihat
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(1.0)
                        
                        # Coba klik dengan JavaScript jika normal click gagal
                        try:
                            element.click()
                            print(f"✅ Berhasil mengklik dengan normal click")
                        except Exception as click_error:
                            print(f"⚠️ Normal click gagal, mencoba JavaScript click: {str(click_error)}")
                            driver.execute_script("arguments[0].click();", element)
                            print(f"✅ Berhasil mengklik dengan JavaScript click")
                        
                        time.sleep(2.0)
                        break
                else:
                    print(f"❌ Tidak ditemukan tombol 'BATALKAN' yang bisa diklik")
                    return False
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return False
        
        # === LANGKAH 3: Klik "YA, BATALKAN TRANSAKSI" dengan direct class selector ===
        print(f"🔍 Langkah 3: Mencari tombol 'YA, BATALKAN TRANSAKSI'...")
        try:
            # Direct class selector berdasarkan terminal output - filter dengan text validation
            elements = driver.find_elements(By.CLASS_NAME, "styles_fullWidth__r6_1Z")
            target_element = None
            
            for element in elements:
                text = element.text.strip()
                if "YA, BATALKAN TRANSAKSI" in text:
                    target_element = element
                    break
            
            if target_element:
                text = target_element.text.strip()
                print(f"🔍 Debug YA Batalkan 1: Text='{text}', Tag={target_element.tag_name}, Class={target_element.get_attribute('class')}, ID={target_element.get_attribute('id')}")
                
                if target_element.is_displayed() and target_element.is_enabled():
                    print(f"🖱️ Mengklik 'YA, BATALKAN TRANSAKSI'...")
                    print(f"🔍 Debug YA Batalkan Success: Class='styles_fullWidth__r6_1Z' (filtered)")
                    target_element.click()
                    time.sleep(2.0)
                else:
                    print(f"❌ Elemen YA BATALKAN tidak dapat diklik")
                    return False
            else:
                print(f"❌ Tidak ditemukan elemen YA BATALKAN dengan class yang sesuai")
                return False
        except Exception as e:
            print(f"❌ Error dengan direct class selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath text-based
            try:
                element = driver.find_element(By.XPATH, "//*[contains(text(), 'YA, BATALKAN TRANSAKSI')][1]")
                text = element.text.strip()
                print(f"🔍 Debug YA Batalkan Fallback: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                
                if element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik 'YA, BATALKAN TRANSAKSI' (fallback)...")
                    print(f"🔍 Debug YA Batalkan Fallback Success: XPath='//*[contains(text(), 'YA, BATALKAN TRANSAKSI')][1]'")
                    element.click()
                    time.sleep(2.0)
                else:
                    print(f"❌ Elemen YA BATALKAN fallback tidak dapat diklik")
                    return False
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return False
        
        # === LANGKAH 4: Isi alasan pembatalan dengan direct name selector ===
        print(f"🔍 Langkah 4: Mengisi alasan pembatalan 'Salah Inputan'...")
        try:
            # Direct name selector berdasarkan terminal output
            element = driver.find_element(By.NAME, "reason")
            element_type = element.get_attribute('type')
            element_placeholder = element.get_attribute('placeholder')
            print(f"🔍 Debug Alasan 1: Type='{element_type}', Placeholder='{element_placeholder}', Name='reason', Tag={element.tag_name}, Class={element.get_attribute('class')}")
            
            if element.is_displayed() and element.is_enabled():
                element.clear()
                element.send_keys("Salah Inputan")
                print(f"✅ Alasan pembatalan berhasil diisi: 'Salah Inputan'")
                print(f"🔍 Debug Alasan Success: Name='reason'")
            else:
                print(f"❌ Elemen alasan tidak dapat diisi")
                return False
        except Exception as e:
            print(f"❌ Error dengan direct name selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath dengan type dan placeholder
            try:
                element = driver.find_element(By.XPATH, "(//input[@type='text'] | //textarea)[1]")
                element_type = element.get_attribute('type')
                element_placeholder = element.get_attribute('placeholder')
                print(f"🔍 Debug Alasan Fallback: Type='{element_type}', Placeholder='{element_placeholder}', Tag={element.tag_name}, Class={element.get_attribute('class')}")
                
                if element.is_displayed() and element.is_enabled():
                    element.clear()
                    element.send_keys("Salah Inputan")
                    print(f"✅ Alasan pembatalan berhasil diisi: 'Salah Inputan' (fallback)")
                    print(f"🔍 Debug Alasan Fallback Success: XPath='(//input[@type='text'] | //textarea)[1]'")
                else:
                    print(f"❌ Elemen alasan fallback tidak dapat diisi")
                    return False
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return False
        
        # === LANGKAH 5: Isi PIN dengan direct XPath selector ===
        print(f"🔍 Langkah 5: Mengisi PIN: {pin}...")
        try:
            # Direct XPath selector berdasarkan terminal output
            element = driver.find_element(By.XPATH, "//input[@type='password' and @placeholder='Masukkan PIN Anda']")
            element_placeholder = element.get_attribute('placeholder')
            element_name = element.get_attribute('name')
            print(f"🔍 Debug PIN 1: Placeholder='{element_placeholder}', Name='{element_name}', Tag={element.tag_name}, Class={element.get_attribute('class')}")
            
            if element.is_displayed() and element.is_enabled():
                element.clear()
                element.send_keys(pin)
                print(f"✅ PIN berhasil diisi: {pin}")
                print(f"🔍 Debug PIN Success: XPath='//input[@type='password' and @placeholder='Masukkan PIN Anda']'")
            else:
                print(f"❌ Elemen PIN tidak dapat diisi")
                return False
        except Exception as e:
            print(f"❌ Error dengan direct XPath selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath dengan type password
            try:
                element = driver.find_element(By.XPATH, "//input[@type='password'][1]")
                element_placeholder = element.get_attribute('placeholder')
                element_name = element.get_attribute('name')
                print(f"🔍 Debug PIN Fallback: Placeholder='{element_placeholder}', Name='{element_name}', Tag={element.tag_name}, Class={element.get_attribute('class')}")
                
                if element.is_displayed() and element.is_enabled():
                    element.clear()
                    element.send_keys(pin)
                    print(f"✅ PIN berhasil diisi: {pin} (fallback)")
                    print(f"🔍 Debug PIN Fallback Success: XPath='//input[@type='password'][1]'")
                else:
                    print(f"❌ Elemen PIN fallback tidak dapat diisi")
                    return False
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return False
        
        # === LANGKAH 6: Klik "BATALKAN TRANSAKSI" dengan direct class selector ===
        print(f"🔍 Langkah 6: Mencari tombol 'BATALKAN TRANSAKSI'...")
        try:
            # Direct class selector berdasarkan terminal output - filter bukan fullWidth
            elements = driver.find_elements(By.CLASS_NAME, "styles_primary__k_AUJ")
            target_element = None
            
            for element in elements:
                class_attr = element.get_attribute('class')
                if "fullWidth" not in class_attr:
                    target_element = element
                    break
            
            if target_element:
                text = target_element.text.strip()
                print(f"🔍 Debug Batalkan Transaksi 1: Text='{text}', Tag={target_element.tag_name}, Class={target_element.get_attribute('class')}, ID={target_element.get_attribute('id')}")
                
                if target_element.is_displayed() and target_element.is_enabled():
                    print(f"🖱️ Mengklik 'BATALKAN TRANSAKSI'...")
                    print(f"🔍 Debug Batalkan Transaksi Success: Class='styles_primary__k_AUJ' (filtered)")
                    target_element.click()
                    time.sleep(3.0)
                else:
                    print(f"❌ Elemen BATALKAN TRANSAKSI tidak dapat diklik")
                    return False
            else:
                print(f"❌ Tidak ditemukan elemen BATALKAN TRANSAKSI yang sesuai")
                return False
        except Exception as e:
            print(f"❌ Error dengan direct class selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath text-based
            try:
                element = driver.find_element(By.XPATH, "//*[contains(text(), 'BATALKAN TRANSAKSI')][1]")
                text = element.text.strip()
                print(f"🔍 Debug Batalkan Transaksi Fallback: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                
                if element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik 'BATALKAN TRANSAKSI' (fallback)...")
                    print(f"🔍 Debug Batalkan Transaksi Fallback Success: XPath='//*[contains(text(), 'BATALKAN TRANSAKSI')][1]'")
                    element.click()
                    time.sleep(3.0)
                else:
                    print(f"❌ Elemen BATALKAN TRANSAKSI fallback tidak dapat diklik")
                    return False
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return False
        
        # Verifikasi apakah transaksi berhasil dibatalkan
        page_source = driver.page_source.lower()
        if "berhasil" in page_source or "dibatalkan" in page_source or "sukses" in page_source:
            print(f"✅ Transaksi berhasil dibatalkan!")
            return True
        else:
            print(f"⚠️ Status pembatalan tidak jelas")
            return False
        
    except Exception as e:
        print(f"❌ Error membatalkan transaksi: {str(e)}")
        return False


def get_transaction_detail_info(driver):
    """
    Mengambil informasi detail dari halaman transaksi
    
    Args:
        driver: WebDriver object yang sudah berada di halaman detail transaksi
    """
    try:
        print(f"📋 Mengambil detail informasi transaksi...")
        
        # Tunggu halaman load
        time.sleep(2.0)
        
        # Ambil semua teks dari halaman
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        all_texts = []
        
        for element in all_elements:
            text = element.text.strip()
            if text and len(text) > 1:
                all_texts.append(text)
        
        # Cari informasi penting
        transaction_info = {}
        
        for i, text in enumerate(all_texts):
            # Cari nama pelanggan (biasanya di bagian atas)
            if len(text) > 5 and text[0].isupper() and not text.startswith(('Rp', 'LPG', 'Tabung')):
                if 'Jaga' in text or len(text.split()) >= 2:
                    transaction_info['nama'] = text
                    print(f"   👤 Nama: {text}")
            
            # Cari nomor telepon (format: 08xxxxxxxxxx)
            elif text.startswith('08') and len(text) >= 10:
                transaction_info['telepon'] = text
                print(f"   📞 Telepon: {text}")
            
            # Cari status pembayaran
            elif text in ['LUNAS', 'BELUM LUNAS', 'PENDING']:
                transaction_info['status'] = text
                print(f"   💰 Status: {text}")
            
            # Cari harga
            elif text.startswith('Rp') and '19' in text:
                transaction_info['harga'] = text
                print(f"   💵 Harga: {text}")
        
        print(f"✅ Detail transaksi berhasil diambil!")
        
    except Exception as e:
        print(f"❌ Error mengambil detail transaksi: {str(e)}")


def get_customer_detail_info(driver):
    """
    Mengambil detail informasi dari halaman "Identitas Pelanggan"
    Termasuk analisis jenis pembelian dalam riwayat transaksi
    
    Args:
        driver: WebDriver object yang sudah berada di halaman detail pelanggan
        
    Returns:
        dict: Dictionary berisi detail informasi pelanggan dan analisis jenis pembelian
    """
    try:
        detail_info = {}
        
        # Tunggu halaman load
        time.sleep(2.0)
        
        # Ambil semua teks dari halaman
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        all_texts = []
        
        for element in all_elements:
            text = element.text.strip()
            if text and len(text) > 1:
                all_texts.append(text)
        
        # Cari informasi berdasarkan pola yang diketahui
        for i, text in enumerate(all_texts):
            # Cari "Nama Pelanggan"
            if "Nama Pelanggan" in text and i + 1 < len(all_texts):
                detail_info['nama'] = all_texts[i + 1]
            
            # Cari "NIK"
            elif "NIK" in text and i + 1 < len(all_texts):
                detail_info['nik'] = all_texts[i + 1]
            
            # Cari "Pelanggan Terdaftar sebagai"
            elif "Pelanggan Terdaftar sebagai" in text and i + 1 < len(all_texts):
                detail_info['status'] = all_texts[i + 1]
            
            # Cari "Total Pembelian Tabung"
            elif "Total Pembelian Tabung" in text and i + 1 < len(all_texts):
                detail_info['total_pembelian'] = all_texts[i + 1]
        
        # Cari riwayat transaksi dan analisis jenis pembelian dengan penggabungan
        riwayat_transaksi = []
        jenis_pembelian_count = {
            'Rumah Tangga': 0,
            'Usaha Mikro': 0,
            'Usaha Kecil': 0,
            'Usaha Menengah': 0,
            'Usaha Besar': 0,
            'Lainnya': 0
        }
        
        # Dictionary untuk menyimpan detail transaksi per jenis
        transaksi_per_jenis = {}
        
        # Debug: Tampilkan semua teks untuk analisis
        print(f"🔍 Debug: Menganalisis {len(all_texts)} teks untuk jenis pembelian...")
        
        # Cari bagian "Riwayat Transaksi"
        riwayat_started = False
        current_transaksi = {}
        
        for i, text in enumerate(all_texts):
            if "Riwayat Transaksi" in text:
                riwayat_started = True
                print(f"🔍 Debug: Riwayat Transaksi ditemukan di index {i}")
                continue
            
            if riwayat_started:
                # Ambil teks yang relevan untuk riwayat transaksi
                if text and len(text) > 5:
                    riwayat_transaksi.append(text)
                    
                    # Deteksi jumlah tabung dari teks seperti "2 Tabung LPG 3 Kg"
                    import re
                    tabung_match = re.search(r'(\d+)\s+Tabung LPG', text)
                    if tabung_match:
                        jumlah_tabung = int(tabung_match.group(1))
                        current_transaksi['jumlah_tabung'] = jumlah_tabung
                        print(f"🔍 Debug: Ditemukan {jumlah_tabung} Tabung LPG")
                    
                    # Deteksi jenis pembelian
                    if text in ['Rumah Tangga', 'Usaha Mikro', 'Usaha Kecil', 'Usaha Menengah', 'Usaha Besar']:
                        jenis_pembelian = text
                        current_transaksi['jenis'] = jenis_pembelian
                        
                        # Gabungkan dengan transaksi sebelumnya jika jenis sama
                        if jenis_pembelian in transaksi_per_jenis:
                            transaksi_per_jenis[jenis_pembelian]['jumlah_tabung'] += current_transaksi.get('jumlah_tabung', 1)
                            transaksi_per_jenis[jenis_pembelian]['jumlah_transaksi'] += 1
                        else:
                            transaksi_per_jenis[jenis_pembelian] = {
                                'jumlah_tabung': current_transaksi.get('jumlah_tabung', 1),
                                'jumlah_transaksi': 1
                            }
                        
                        # Update counter untuk summary
                        jenis_pembelian_count[jenis_pembelian] += 1
                        print(f"🔍 Debug: +1 {jenis_pembelian} ({current_transaksi.get('jumlah_tabung', 1)} tabung)")
                        
                        # Reset untuk transaksi berikutnya
                        current_transaksi = {}
                
                # Batasi untuk menghindari mengambil terlalu banyak data
                if len(riwayat_transaksi) > 50:
                    break
        
        print(f"🔍 Debug: Hasil analisis jenis pembelian (digabung):")
        for jenis, data in transaksi_per_jenis.items():
            print(f"   - {jenis}: {data['jumlah_transaksi']} transaksi, {data['jumlah_tabung']} tabung total")
        
        detail_info['riwayat'] = riwayat_transaksi
        detail_info['jenis_pembelian'] = jenis_pembelian_count
        detail_info['transaksi_per_jenis'] = transaksi_per_jenis
        
        # Buat summary analisis dengan data yang sudah digabung
        total_transaksi = sum(jenis_pembelian_count.values())
        total_tabung = sum(data['jumlah_tabung'] for data in transaksi_per_jenis.values())
        
        detail_info['summary'] = {
            'total_transaksi': total_transaksi,
            'total_tabung': total_tabung,
            'rumah_tangga': jenis_pembelian_count['Rumah Tangga'],
            'usaha_mikro': jenis_pembelian_count['Usaha Mikro'],
            'usaha_kecil': jenis_pembelian_count['Usaha Kecil'],
            'usaha_menengah': jenis_pembelian_count['Usaha Menengah'],
            'usaha_besar': jenis_pembelian_count['Usaha Besar'],
            'lainnya': jenis_pembelian_count['Lainnya']
        }
        
        return detail_info
        
    except Exception as e:
        print(f"❌ Error mengambil detail pelanggan: {str(e)}")
        return None
        print(f"❌ Error mengambil detail pelanggan: {str(e)}")
        return None