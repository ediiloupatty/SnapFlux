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

logger = logging.getLogger('automation')

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
                return None
            
            # Tunggu proses login kedua - OPTIMIZED
            print("⏳ Menunggu proses login kedua...")
            time.sleep(1.5)  # Kurangi dari 3 ke 1.5 detik
        
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