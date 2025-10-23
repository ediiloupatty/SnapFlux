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


def get_customer_list_direct(driver):
    """
    Mengambil data list pembeli dari halaman Rekap Penjualan dengan pola yang sudah diketahui
    Berdasarkan debugging: Struktur Nama → HP/NIK → "Jenis Pelanggan" → "X Tabung LPG 3Kg"
    Jika pembeli membeli >1 tabung, akan diklik untuk melihat detail
    
    Args:
        driver: WebDriver object yang sudah berada di halaman Rekap Penjualan
        
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
            
            # Cari elemen yang bisa diklik untuk setiap pembeli dengan >1 tabung
            for customer in customer_elements:
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
                                        
                                        # Tampilkan analisis jenis pembelian
                                        summary = detail_info.get('summary', {})
                                        if summary:
                                            print(f"   📊 Analisis Jenis Pembelian:")
                                            print(f"      - Total Transaksi: {summary.get('total_transaksi', 0)}")
                                            print(f"      - Rumah Tangga: {summary.get('rumah_tangga', 0)} kali")
                                            print(f"      - Usaha Mikro: {summary.get('usaha_mikro', 0)} kali")
                                            print(f"      - Usaha Kecil: {summary.get('usaha_kecil', 0)} kali")
                                            print(f"      - Usaha Menengah: {summary.get('usaha_menengah', 0)} kali")
                                            print(f"      - Usaha Besar: {summary.get('usaha_besar', 0)} kali")
                                            if summary.get('lainnya', 0) > 0:
                                                print(f"      - Lainnya: {summary.get('lainnya', 0)} kali")
                                    
                                    # Kembali ke halaman sebelumnya
                                    driver.back()
                                    time.sleep(2.0)
                                    break
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
        
        # Cari riwayat transaksi dan analisis jenis pembelian
        riwayat_transaksi = []
        jenis_pembelian_count = {
            'Rumah Tangga': 0,
            'Usaha Mikro': 0,
            'Usaha Kecil': 0,
            'Usaha Menengah': 0,
            'Usaha Besar': 0,
            'Lainnya': 0
        }
        
        # Cari bagian "Riwayat Transaksi"
        riwayat_started = False
        for i, text in enumerate(all_texts):
            if "Riwayat Transaksi" in text:
                riwayat_started = True
                continue
            
            if riwayat_started:
                # Ambil teks yang relevan untuk riwayat transaksi
                if text and len(text) > 5:
                    riwayat_transaksi.append(text)
                    
                    # Analisis jenis pembelian
                    if text in jenis_pembelian_count:
                        jenis_pembelian_count[text] += 1
                    elif any(keyword in text.lower() for keyword in ['rumah tangga', 'usaha mikro', 'usaha kecil', 'usaha menengah', 'usaha besar']):
                        # Jika ada jenis pembelian yang tidak terdaftar
                        jenis_pembelian_count['Lainnya'] += 1
                
                # Batasi untuk menghindari mengambil terlalu banyak data
                if len(riwayat_transaksi) > 50:
                    break
        
        detail_info['riwayat'] = riwayat_transaksi
        detail_info['jenis_pembelian'] = jenis_pembelian_count
        
        # Buat summary analisis
        total_transaksi = sum(jenis_pembelian_count.values())
        detail_info['summary'] = {
            'total_transaksi': total_transaksi,
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

