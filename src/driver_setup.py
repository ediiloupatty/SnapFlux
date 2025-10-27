"""
Setup dan konfigurasi browser driver untuk automation
File ini mengatur Chrome WebDriver dengan optimasi performa maksimal
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import logging

# Import enhanced error handling (backward compatible)
try:
    from .error_handler import handle_selenium_errors
    from .exceptions import DriverSetupError
    ENHANCED_ERROR_HANDLING = True
except ImportError:
    ENHANCED_ERROR_HANDLING = False

# Setup logging untuk tracking error driver
logger = logging.getLogger('driver_setup')

# Konfigurasi path Chrome binary dan ChromeDriver (hardcoded untuk menghindari masalah import)
CHROME_BINARY = r"D:\edi\Programing\Snapflux v2\chrome\Chromium\bin\chrome.exe"      # Path ke executable Chrome
CHROMEDRIVER_PATH = r"D:\edi\Programing\Snapflux v2\chrome\chromedriver.exe"         # Path ke ChromeDriver executable

# Enhanced configuration support (backward compatible)
try:
    from .config_manager import config_manager
    def get_chrome_binary():
        return config_manager.get('chrome_binary', CHROME_BINARY)
    def get_chromedriver_path():
        return config_manager.get('chromedriver_path', CHROMEDRIVER_PATH)
except ImportError:
    def get_chrome_binary():
        return CHROME_BINARY
    def get_chromedriver_path():
        return CHROMEDRIVER_PATH

def setup_driver(headless=False):
    """
    Setup Chrome WebDriver dengan konfigurasi optimal untuk performa maksimal
    
    Args:
        headless (bool): Jika True, browser akan berjalan tanpa GUI untuk performa lebih cepat
        
    Returns:
        webdriver.Chrome: Object WebDriver yang sudah dikonfigurasi
        
    Raises:
        Exception: Jika terjadi error saat setup driver
    """
    print("🚀 Setting up Chrome WebDriver dengan optimasi performa...")
    
    try:
        # Buat object ChromeOptions untuk mengatur setting browser
        options = Options()
        
        # ========== OPTIMASI PERFORMA MAKSIMAL ==========
        # Opsi-opsi untuk meningkatkan kecepatan dan stabilitas browser
        options.add_argument("--no-sandbox")                                    # Disable sandbox untuk performa
        options.add_argument("--disable-dev-shm-usage")                         # Disable shared memory usage
        options.add_argument("--disable-gpu")                                   # Disable GPU rendering
        options.add_argument("--disable-extensions")                            # Disable browser extensions
        options.add_argument("--disable-plugins")                               # Disable plugins
        options.add_argument("--disable-web-security")                          # Disable web security untuk automation
        options.add_argument("--disable-features=VizDisplayCompositor")         # Disable display compositor
        options.add_argument("--disable-background-timer-throttling")           # Disable background throttling
        options.add_argument("--disable-backgrounding-occluded-windows")        # Disable background tab throttling
        options.add_argument("--disable-renderer-backgrounding")                # Disable renderer backgrounding
        options.add_argument("--disable-field-trial-config")                   # Disable field trials
        options.add_argument("--disable-ipc-flooding-protection")              # Disable IPC protection
        
        # ========== BLOCK GAMBAR DAN MEDIA ==========
        # Setting untuk memblokir konten yang tidak diperlukan untuk mempercepat loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Block images
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
            "profile.managed_default_content_settings.media_stream": 2,  # Block media
            "profile.managed_default_content_settings.plugins": 2,  # Block plugins
            "profile.managed_default_content_settings.popups": 2,  # Block popups
            "profile.managed_default_content_settings.geolocation": 2,  # Block location
            "profile.managed_default_content_settings.midi_sysex": 2,  # Block MIDI
            "profile.managed_default_content_settings.protected_media_identifier": 2,  # Block protected media
            "profile.managed_default_content_settings.automatic_downloads": 2,  # Block downloads
        }
        options.add_experimental_option("prefs", prefs)
        
        # === OPTIMASI MEMORI DAN CPU ===
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=1024")  # Kurangi dari 4096 ke 2048
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--mute-audio")
        
        # === OPTIMASI JAVASCRIPT ===
        #Block JavaScript untuk performa maksimal
        options.add_argument("--disable-java")
        options.add_argument("--disable-flash")
        
        # === OPTIMASI NETWORK ===
        options.add_argument("--aggressive-cache-discard")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-web-resources")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-permissions-api")
        
        # === USER AGENT ===
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # === WINDOW SIZE ===
        if headless:
            options.add_argument("--headless")
        else:
            options.add_argument("--window-size=1366,768")  # Kurangi dari 1920x1080 ke 1366x768
        
        # === CHROME BINARY PATH ===
        chrome_binary_path = get_chrome_binary()
        if os.path.exists(chrome_binary_path):
            options.binary_location = chrome_binary_path
            print(f"✅ Menggunakan Chrome binary: {chrome_binary_path}")
        else:
            print("⚠️ Chrome binary tidak ditemukan, menggunakan default")
        
        # === CHROMEDRIVER SERVICE ===
        chromedriver_path = get_chromedriver_path()
        if os.path.exists(chromedriver_path):
            service = Service(chromedriver_path)
            print(f"✅ Menggunakan ChromeDriver: {chromedriver_path}")
        else:
            print("⚠️ ChromeDriver tidak ditemukan, menggunakan default")
            service = Service()
        
        # === CREATE DRIVER ===
        driver = webdriver.Chrome(service=service, options=options)
        
        # === SET TIMEOUTS ===
        driver.set_page_load_timeout(20)  # Kurangi dari 30 ke 20 detik
        driver.implicitly_wait(5)  # Kurangi dari 10 ke 5 detik
        
        print("✅ Chrome WebDriver berhasil di-setup dengan optimasi performa maksimal!")
        print("🚫 Gambar, JavaScript, dan media telah di-block untuk performa optimal")
        return driver
        
    except Exception as e:
        print(f"❌ Error setup Chrome WebDriver: {str(e)}")
        logger.error(f"Error setup driver: {str(e)}", exc_info=True)
        
        # Enhanced error handling jika tersedia
        if ENHANCED_ERROR_HANDLING:
            try:
                raise DriverSetupError(f"Failed to setup Chrome WebDriver: {str(e)}")
            except DriverSetupError:
                return None
        
        return None