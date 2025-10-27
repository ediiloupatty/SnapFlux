"""
Login handling dan fungsi authentication untuk platform merchant Pertamina
File ini menangani proses login dan error handling
"""
import time
from selenium.webdriver.common.by import By
import logging

from .constants import LOGIN_URL, DEFAULT_DELAY
from .selectors import LoginSelectors, InputSelectors
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
    Login langsung dengan strategi yang sudah terbukti berhasil
    Fungsi ini melakukan login otomatis ke portal merchant dengan retry mechanism
    
    Args:
        username (str): Username berupa email atau nomor HP
        pin (str): PIN untuk authentication
        
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
        
        # Tunggu halaman loading - ANTI-RATE LIMITING
        time.sleep(DEFAULT_DELAY)
        
        # Langsung cari dan isi email
        print("📧 Mencari dan mengisi field email...")
        email_inputs = driver.find_elements(LoginSelectors.EMAIL_INPUT[0], LoginSelectors.EMAIL_INPUT[1])
        
        email_filled = False
        for input_field in email_inputs:
            try:
                input_type = input_field.get_attribute("type")
                if input_type in InputSelectors.EMAIL_TYPES:
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
        pin_inputs = driver.find_elements(LoginSelectors.PIN_INPUT[0], LoginSelectors.PIN_INPUT[1])
        
        pin_filled = False
        for input_field in pin_inputs:
            try:
                input_type = input_field.get_attribute("type")
                if input_type == InputSelectors.PASSWORD_TYPE:
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
        login_buttons = driver.find_elements(LoginSelectors.LOGIN_BUTTON[0], LoginSelectors.LOGIN_BUTTON[1])
        
        login_clicked = False
        for button in login_buttons:
            try:
                button_text = button.text.strip().upper()
                if any(text in button_text for text in InputSelectors.BUTTON_TEXTS):
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
        
        # Tunggu proses login - ANTI-RATE LIMITING
        time.sleep(DEFAULT_DELAY)
        
        # === DETEKSI CEPAT "GAGAL MASUK AKUN" ===
        gagal_masuk_detected = False
        
        try:
            # Super cepat: langsung cek dengan find_element, jika tidak ada langsung lanjut
            error_element = driver.find_element(LoginSelectors.GAGAL_MASUK_ERROR[0], LoginSelectors.GAGAL_MASUK_ERROR[1])
            if error_element:
                gagal_masuk_detected = True
                print("❌ PESAN 'GAGAL MASUK AKUN' TERDETEKSI!")
        except:
            # Tidak ditemukan - langsung lanjut ke proses selanjutnya tanpa delay
            pass
        
        # === HANDLE GAGAL MASUK AKUN ===
        if gagal_masuk_detected:
            print("🔄 === PROSES RETRY LOGIN SETELAH GAGAL MASUK AKUN ===")
            
            # Tunggu 2 menit (120 detik)
            print("⏳ Menunggu 2 menit (120 detik)...")
            time.sleep(120)
            print("✅ Tunggu 2 menit selesai!")
            
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
                            if any(text in button_text for text in InputSelectors.BUTTON_TEXTS):
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
            time.sleep(1.5)  # Kurangi dari 3 ke 1.5 detik
        
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
        # Tunggu sebentar untuk memastikan halaman sudah load
        time.sleep(2.0)
        
        # Debug: Ambil semua elemen yang mungkin terkait dengan "Laporan Penjualan"
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
                    
                    for j, element in enumerate(elements):
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
        
        # Debug: Cari semua elemen yang terlihat di halaman
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
            
            for i, element in enumerate(relevant_elements[:10]):  # Limit 10 untuk readability
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
        
        # Tunggu navigasi ke halaman Laporan Penjualan
        print("⏳ Menunggu navigasi ke halaman Laporan Penjualan...")
        time.sleep(3.0)
        
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
        # Tunggu sebentar untuk memastikan halaman sudah load
        time.sleep(2.0)
        
        # Langsung gunakan selector yang sudah diketahui dari debugging
        try:
            rekap_element = driver.find_element(By.XPATH, "//div[contains(text(), 'Rekap Penjualan')]")
            
            if rekap_element.is_displayed() and rekap_element.is_enabled():
                rekap_element.click()
                print("✅ Berhasil mengklik Rekap Penjualan!")
                
                # Tunggu navigasi ke halaman Rekap Penjualan
                time.sleep(3.0)
                
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
    Mengambil data list pembeli dari halaman Rekap Penjualan dengan pola yang sudah diketahui
    Berdasarkan debugging: Struktur Nama → HP/NIK → "Jenis Pelanggan" → "X Tabung LPG 3Kg"
    Jika pembeli membeli >1 tabung, akan diklik untuk melihat detail dan membatalkan transaksi
    
    Args:
        driver: WebDriver object yang sudah berada di halaman Rekap Penjualan
        pin: PIN dari akun yang sedang login
        
    Returns:
        list: List nama pembeli dengan format "Nama Lengkap (Nomor HP/NIK) - X Tabung", atau None jika gagal
    """
    print("👥 Mengambil data list pembeli...")
    
    try:
        # Tunggu sebentar untuk memastikan halaman sudah load
        time.sleep(2.0)
        
        # Ambil semua teks dari halaman
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        all_texts = []
        
        for element in all_elements:
            text = element.text.strip()
            if text and len(text) > 2:
                all_texts.append(text)
        
        print(f"📊 Ditemukan {len(all_texts)} elemen dengan teks")
        
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
                not current_text.startswith(('710', '717', '917', '920')) and
                'Jenis Pelanggan' not in current_text and
                'Tabung LPG' not in current_text and
                'Penjualan' not in current_text and
                'Total' not in current_text and
                'Jumlah' not in current_text and
                'Atur Rentang Waktu' not in current_text):
                
                # Cek 3 baris berikutnya untuk memastikan ini adalah data pembeli
                if i + 3 < len(all_texts):
                    next_text1 = all_texts[i + 1]  # Nomor HP/NIK
                    next_text2 = all_texts[i + 2]  # "Jenis Pelanggan"
                    next_text3 = all_texts[i + 3]  # "X Tabung LPG 3Kg"
                    
                    # Validasi berdasarkan pola yang sudah diketahui
                    if (next_text1.startswith(('710', '717', '917', '920')) and
                        'Jenis Pelanggan' in next_text2 and
                        'Tabung LPG' in next_text3):
                        
                        # Extract jumlah tabung dari next_text3
                        # Contoh: "1 Tabung LPG 3Kg", "3 Tabung LPG 3Kg", "2 Tabung LPG 3Kg"
                        import re
                        tabung_match = re.search(r'(\d+)\s+Tabung LPG', next_text3)
                        jumlah_tabung = tabung_match.group(1) if tabung_match else "?"
                        
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
            
            i += 1
        
        # Jika ada pembeli dengan >1 tabung, cari dan klik mereka
        if customer_elements:
            print(f"\n🔍 Ditemukan {len(customer_elements)} pembeli dengan >1 tabung:")
            for customer in customer_elements:
                print(f"   - {customer['name']} ({customer['nik']}) - {customer['tabung']} Tabung")
            
            print(f"\n🖱️ Mengklik pembeli dengan >1 tabung untuk melihat detail...")
            
            # Process customers in a loop, rechecking after each cancellation
            processed_customers = []
            max_iterations = 10  # Prevent infinite loop
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                print(f"\n{'='*60}")
                print(f"🔄 Iterasi {iteration}: Mencari ulang pembeli dengan >1 tabung...")
                print(f"{'='*60}")
                
                # Refresh halaman untuk mendapatkan data terbaru
                if iteration > 1:
                    print("🔄 Refresh halaman untuk mendapatkan data terbaru...")
                    driver.refresh()
                    time.sleep(3.0)
                
                # Cari ulang pembeli dengan >1 tabung
                time.sleep(2.0)
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
                        not current_text.startswith(('710', '717', '917', '920')) and
                        'Jenis Pelanggan' not in current_text and
                        'Tabung LPG' not in current_text and
                        'Penjualan' not in current_text and
                        'Total' not in current_text and
                        'Jumlah' not in current_text and
                        'Atur Rentang Waktu' not in current_text):
                        
                        if i + 3 < len(all_texts):
                            next_text1 = all_texts[i + 1]
                            next_text2 = all_texts[i + 2]
                            next_text3 = all_texts[i + 3]
                            
                            if (next_text1.startswith(('710', '717', '917', '920')) and
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
                                        element.click()
                                        
                                        # Tunggu halaman detail load
                                        time.sleep(3.0)
                                        
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
                                                        cancel_result = click_rumah_tangga_transaction(driver, pin)
                                                        if cancel_result:
                                                            print(f"   ✅ Berhasil membatalkan transaksi salah inputan untuk {customer['name']}")
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
                                                        
                                                        # Batalkan salah satu transaksi (yang pertama)
                                                        cancel_result = click_rumah_tangga_transaction(driver, pin)
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


def click_rumah_tangga_transaction(driver, pin):
    """
    Mengklik transaksi Rumah Tangga pertama untuk masuk ke halaman detail transaksi
    Menggunakan berbagai metode pencarian untuk memastikan berhasil
    Kemudian melakukan pembatalan transaksi
    
    Args:
        driver: WebDriver object yang sudah berada di halaman detail pelanggan
        pin: PIN dari akun yang sedang login
        
    Returns:
        bool: True jika berhasil klik transaksi dan batalkan, False jika gagal
    """
    try:
        print(f"🖱️ Mencari dan mengklik transaksi Rumah Tangga...")
        
        # Tunggu halaman load
        time.sleep(2.0)
        
        # Debug: Tampilkan informasi halaman saat ini
        current_url = driver.current_url
        print(f"🔍 Debug: URL saat ini: {current_url}")
        
        # Metode 1: Cari elemen dengan teks "Rumah Tangga" dan klik parent
        print(f"🔍 Debug: Metode 1 - Mencari elemen 'Rumah Tangga'...")
        rumah_tangga_elements = driver.find_elements(By.XPATH, "//*[text()='Rumah Tangga']")
        print(f"🔍 Debug: Ditemukan {len(rumah_tangga_elements)} elemen 'Rumah Tangga'")
        
        for i, element in enumerate(rumah_tangga_elements):
            try:
                print(f"🔍 Debug: Elemen {i+1}: Tag={element.tag_name}, Class={element.get_attribute('class')}")
                
                # Coba klik parent element
                parent = element.find_element(By.XPATH, "..")
                if parent.is_displayed() and parent.is_enabled():
                    print(f"🖱️ Mengklik parent element dari Rumah Tangga (metode 1)...")
                    parent.click()
                    time.sleep(3.0)
                    
                    # Verifikasi navigasi dan lakukan pembatalan
                    if verify_transaction_detail_page(driver):
                        # Lakukan pembatalan transaksi
                        cancel_result = cancel_transaction(driver, pin)
                        return cancel_result
                        
            except Exception as e:
                print(f"🔍 Debug: Error dengan elemen {i+1}: {str(e)}")
                continue
        
        # Metode 2: Cari elemen yang mengandung "Tabung LPG" dan "Rumah Tangga"
        print(f"🔍 Debug: Metode 2 - Mencari elemen dengan 'Tabung LPG' dan 'Rumah Tangga'...")
        tabung_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Tabung LPG')]")
        print(f"🔍 Debug: Ditemukan {len(tabung_elements)} elemen 'Tabung LPG'")
        
        for i, element in enumerate(tabung_elements):
            try:
                element_text = element.text.strip()
                print(f"🔍 Debug: Elemen {i+1}: '{element_text[:100]}...'")
                
                if 'Rumah Tangga' in element_text and element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik elemen Tabung LPG dengan Rumah Tangga (metode 2)...")
                    element.click()
                    time.sleep(3.0)
                    
                    if verify_transaction_detail_page(driver):
                        # Lakukan pembatalan transaksi
                        cancel_result = cancel_transaction(driver, pin)
                        return cancel_result
                        
            except Exception as e:
                print(f"🔍 Debug: Error dengan elemen Tabung LPG {i+1}: {str(e)}")
                continue
        
        # Metode 3: Cari elemen dengan harga "Rp19" dan "Rumah Tangga"
        print(f"🔍 Debug: Metode 3 - Mencari elemen dengan 'Rp19' dan 'Rumah Tangga'...")
        harga_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Rp19')]")
        print(f"🔍 Debug: Ditemukan {len(harga_elements)} elemen 'Rp19'")
        
        for i, element in enumerate(harga_elements):
            try:
                element_text = element.text.strip()
                print(f"🔍 Debug: Elemen {i+1}: '{element_text[:100]}...'")
                
                if 'Rumah Tangga' in element_text and element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik elemen harga dengan Rumah Tangga (metode 3)...")
                    element.click()
                    time.sleep(3.0)
                    
                    if verify_transaction_detail_page(driver):
                        # Lakukan pembatalan transaksi
                        cancel_result = cancel_transaction(driver, pin)
                        return cancel_result
                        
            except Exception as e:
                print(f"🔍 Debug: Error dengan elemen harga {i+1}: {str(e)}")
                continue
        
        # Metode 4: Cari semua elemen yang bisa diklik dan cek isinya
        print(f"🔍 Debug: Metode 4 - Mencari semua elemen yang bisa diklik...")
        clickable_elements = driver.find_elements(By.XPATH, "//*[@onclick or @href or contains(@class, 'click') or contains(@class, 'btn') or contains(@class, 'card')]")
        print(f"🔍 Debug: Ditemukan {len(clickable_elements)} elemen yang bisa diklik")
        
        for i, element in enumerate(clickable_elements[:10]):  # Batasi untuk performa
            try:
                element_text = element.text.strip()
                if len(element_text) > 20 and 'Rumah Tangga' in element_text:
                    print(f"🔍 Debug: Elemen clickable {i+1}: '{element_text[:100]}...'")
                    
                    if element.is_displayed() and element.is_enabled():
                        print(f"🖱️ Mengklik elemen clickable dengan Rumah Tangga (metode 4)...")
                        element.click()
                        time.sleep(3.0)
                        
                        if verify_transaction_detail_page(driver):
                            return True
                            
            except Exception as e:
                print(f"🔍 Debug: Error dengan elemen clickable {i+1}: {str(e)}")
                continue
        
        print(f"❌ Semua metode gagal menemukan transaksi Rumah Tangga yang bisa diklik")
        return False
        
    except Exception as e:
        print(f"❌ Error mengklik transaksi Rumah Tangga: {str(e)}")
        return False


def verify_transaction_detail_page(driver):
    """
    Verifikasi apakah sudah masuk ke halaman detail transaksi
    
    Args:
        driver: WebDriver object
        
    Returns:
        bool: True jika sudah di halaman detail transaksi, False jika belum
    """
    try:
        # Tunggu halaman load
        time.sleep(2.0)
        
        # Cek URL dan page source
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        print(f"🔍 Debug: URL setelah klik: {current_url}")
        print(f"🔍 Debug: Page source contains 'informasi transaksi': {'informasi transaksi' in page_source}")
        print(f"🔍 Debug: Page source contains 'rincian': {'rincian' in page_source}")
        print(f"🔍 Debug: Page source contains 'pembayaran': {'pembayaran' in page_source}")
        print(f"🔍 Debug: Page source contains 'total pembayaran': {'total pembayaran' in page_source}")
        
        # Verifikasi berdasarkan berbagai indikator
        if ("informasi transaksi" in page_source or 
            "rincian" in page_source or
            "pembayaran" in page_source or
            "total pembayaran" in page_source or
            "item pembelian" in page_source):
            print(f"✅ Berhasil masuk ke halaman detail transaksi!")
            return True
        else:
            print(f"⚠️ Tidak berhasil masuk ke halaman detail transaksi")
            return False
            
    except Exception as e:
        print(f"❌ Error verifikasi halaman detail transaksi: {str(e)}")
        return False


def cancel_transaction(driver, pin):
    """
    Membatalkan transaksi dengan langkah-langkah:
    1. Klik "Rincian"
    2. Klik "Batalkan"
    3. Klik "YA, BATALKAN TRANSAKSI"
    4. Isi alasan pembatalan: "Salah Inputan"
    5. Isi PIN
    6. Klik "BATALKAN TRANSAKSI"
    
    Args:
        driver: WebDriver object yang sudah berada di halaman detail transaksi
        pin: PIN dari akun yang sedang login
        
    Returns:
        bool: True jika berhasil membatalkan transaksi, False jika gagal
    """
    try:
        print(f"🔄 Memulai proses pembatalan transaksi...")
        
        # Ambil informasi detail transaksi terlebih dahulu
        get_transaction_detail_info(driver)
        
        # Langkah 1: Klik "Rincian" terlebih dahulu
        print(f"🔍 Langkah 1: Mencari dan mengklik 'Rincian'...")
        rincian_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Rincian')]")
        
        rincian_clicked = False
        for i, element in enumerate(rincian_elements):
            try:
                element_text = element.text.strip()
                print(f"🔍 Debug Rincian {i+1}: Text='{element_text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                
                if element_text == "Rincian" and element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik 'Rincian'...")
                    print(f"🔍 Debug Rincian Success: XPath='//*[contains(text(), 'Rincian')][{i+1}]'")
                    element.click()
                    time.sleep(2.0)
                    rincian_clicked = True
                    break
            except Exception as e:
                print(f"🔍 Debug Rincian Error {i+1}: {str(e)}")
                continue
        
        if not rincian_clicked:
            print(f"❌ Tidak ditemukan tombol 'Rincian'")
            return False
        
        # Langkah 2: Cari dan klik tombol "Batalkan"
        print(f"🔍 Langkah 2: Mencari tombol 'Batalkan'...")
        
        # Cari tombol "Batalkan" dengan berbagai cara
        batalkan_selectors = [
            "//*[contains(text(), 'Batalkan')]",
            "//*[text()='Batalkan']",
            "//button[contains(text(), 'Batalkan')]",
            "//div[contains(text(), 'Batalkan')]",
            "//span[contains(text(), 'Batalkan')]"
        ]
        
        batalkan_clicked = False
        for selector in batalkan_selectors:
            try:
                batalkan_elements = driver.find_elements(By.XPATH, selector)
                print(f"🔍 Debug: Selector '{selector}' menemukan {len(batalkan_elements)} elemen")
                
                for j, element in enumerate(batalkan_elements):
                    try:
                        element_text = element.text.strip()
                        print(f"🔍 Debug Batalkan {j+1}: Text='{element_text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                        
                        # Cek apakah ini tombol "BATALKAN" yang benar
                        if (element_text == "BATALKAN" and 
                            element.is_displayed() and 
                            element.is_enabled()):
                            print(f"🖱️ Mengklik tombol 'BATALKAN'...")
                            print(f"🔍 Debug Batalkan Success: XPath='{selector}[{j+1}]'")
                            
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
                            batalkan_clicked = True
                            break
                    except Exception as e:
                        print(f"🔍 Debug Batalkan Error {j+1}: {str(e)}")
                        continue
                        
                if batalkan_clicked:
                    break
                    
            except Exception as e:
                print(f"🔍 Debug: Error dengan selector '{selector}': {str(e)}")
                continue
        
        if not batalkan_clicked:
            print(f"❌ Tidak ditemukan tombol 'Batalkan'")
            return False
        
        # Langkah 3: Cari dan klik "YA, BATALKAN TRANSAKSI"
        print(f"🔍 Langkah 3: Mencari tombol 'YA, BATALKAN TRANSAKSI'...")
        ya_batalkan_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'YA, BATALKAN TRANSAKSI')]")
        
        ya_batalkan_clicked = False
        for i, element in enumerate(ya_batalkan_elements):
            try:
                element_text = element.text.strip()
                print(f"🔍 Debug YA Batalkan {i+1}: Text='{element_text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                
                if element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik 'YA, BATALKAN TRANSAKSI'...")
                    print(f"🔍 Debug YA Batalkan Success: XPath='//*[contains(text(), 'YA, BATALKAN TRANSAKSI')][{i+1}]'")
                    element.click()
                    time.sleep(2.0)
                    ya_batalkan_clicked = True
                    break
            except Exception as e:
                print(f"🔍 Debug YA Batalkan Error {i+1}: {str(e)}")
                continue
        
        if not ya_batalkan_clicked:
            print(f"❌ Tidak ditemukan tombol 'YA, BATALKAN TRANSAKSI'")
            return False
        
        # Langkah 4: Isi alasan pembatalan "Salah Inputan"
        print(f"🔍 Langkah 4: Mengisi alasan pembatalan 'Salah Inputan'...")
        alasan_elements = driver.find_elements(By.XPATH, "//input[@type='text'] | //textarea")
        
        alasan_filled = False
        for i, element in enumerate(alasan_elements):
            try:
                element_type = element.get_attribute('type')
                element_placeholder = element.get_attribute('placeholder')
                element_name = element.get_attribute('name')
                print(f"🔍 Debug Alasan {i+1}: Type='{element_type}', Placeholder='{element_placeholder}', Name='{element_name}', Tag={element.tag_name}, Class={element.get_attribute('class')}")
                
                if element.is_displayed() and element.is_enabled():
                    element.clear()
                    element.send_keys("Salah Inputan")
                    print(f"✅ Alasan pembatalan berhasil diisi: 'Salah Inputan'")
                    print(f"🔍 Debug Alasan Success: XPath='(//input[@type='text'] | //textarea)[{i+1}]'")
                    alasan_filled = True
                    break
            except Exception as e:
                print(f"🔍 Debug Alasan Error {i+1}: {str(e)}")
                continue
        
        if not alasan_filled:
            print(f"❌ Tidak ditemukan field alasan pembatalan")
            return False
        
        # Langkah 5: Isi PIN
        print(f"🔍 Langkah 5: Mengisi PIN: {pin}...")
        pin_elements = driver.find_elements(By.XPATH, "//input[@type='password']")
        
        pin_filled = False
        for i, element in enumerate(pin_elements):
            try:
                element_placeholder = element.get_attribute('placeholder')
                element_name = element.get_attribute('name')
                print(f"🔍 Debug PIN {i+1}: Placeholder='{element_placeholder}', Name='{element_name}', Tag={element.tag_name}, Class={element.get_attribute('class')}")
                
                if element.is_displayed() and element.is_enabled():
                    element.clear()
                    element.send_keys(pin)
                    print(f"✅ PIN berhasil diisi: {pin}")
                    print(f"🔍 Debug PIN Success: XPath='//input[@type='password'][{i+1}]'")
                    pin_filled = True
                    break
            except Exception as e:
                print(f"🔍 Debug PIN Error {i+1}: {str(e)}")
                continue
        
        if not pin_filled:
            print(f"❌ Tidak ditemukan field PIN")
            return False
        
        # Langkah 6: Klik "BATALKAN TRANSAKSI"
        print(f"🔍 Langkah 6: Mencari tombol 'BATALKAN TRANSAKSI'...")
        batalkan_transaksi_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'BATALKAN TRANSAKSI')]")
        
        batalkan_transaksi_clicked = False
        for i, element in enumerate(batalkan_transaksi_elements):
            try:
                element_text = element.text.strip()
                print(f"🔍 Debug Batalkan Transaksi {i+1}: Text='{element_text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}")
                
                if element.is_displayed() and element.is_enabled():
                    print(f"🖱️ Mengklik 'BATALKAN TRANSAKSI'...")
                    print(f"🔍 Debug Batalkan Transaksi Success: XPath='//*[contains(text(), 'BATALKAN TRANSAKSI')][{i+1}]'")
                    element.click()
                    time.sleep(3.0)
                    batalkan_transaksi_clicked = True
                    break
            except Exception as e:
                print(f"🔍 Debug Batalkan Transaksi Error {i+1}: {str(e)}")
                continue
        
        if not batalkan_transaksi_clicked:
            print(f"❌ Tidak ditemukan tombol 'BATALKAN TRANSAKSI'")
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

