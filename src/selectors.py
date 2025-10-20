"""
Selector dan XPath untuk element HTML
File ini berisi semua selector yang digunakan untuk mencari element di web
"""
from selenium.webdriver.common.by import By

# ========== LOGIN SELECTORS ==========
class LoginSelectors:
    EMAIL_INPUT = (By.TAG_NAME, "input")
    PIN_INPUT = (By.TAG_NAME, "input")
    LOGIN_BUTTON = (By.TAG_NAME, "button")
    GAGAL_MASUK_ERROR = (By.XPATH, "//h5[contains(@class, 'mantine-Title-root') and text()='Gagal Masuk Akun']")

# ========== NAVIGATION SELECTORS ==========
class NavigationSelectors:
    STOCK_ELEMENT = (By.CLASS_NAME, "styles_summaryProductCard__Uv3IK")
    LAPORAN_PENJUALAN = (By.XPATH, "//*[contains(text(), 'Laporan Penjualan')]")
    ATUR_PRODUK = [
        "//*[(self::button or self::a or self::div or self::span) and contains(text(), 'Atur Produk')]",
        "//*[(self::button or self::a or self::div or self::span) and contains(text(), 'Atur Stok')]",
        "//*[contains(text(), 'Atur') and contains(text(), 'Harga')]"
    ]

# ========== DATE SELECTORS ==========
class DateSelectors:
    ATUR_RENTANG_WAKTU = (By.XPATH, "//*[contains(text(), 'Atur Rentang Waktu')]")
    BULAN_TAHUN_BUTTON = (By.CLASS_NAME, "mantine-UnstyledButton-root")
    TANGGAL_ELEMENT = (By.XPATH, "//*[text()='{}']")  # Dynamic selector

# ========== DATA EXTRACTION SELECTORS ==========
class DataExtractionSelectors:
    TABUNG_TERJUAL = (By.CLASS_NAME, "mantine-Text-root")
    TABUNG_TERJUAL_FALLBACK = [
        "//*[contains(text(), 'Tabung')]",
        "//div[contains(@class, 'text')]//*[contains(text(), 'tabung')]",
        "//span[contains(text(), 'tabung')]",
        "//p[contains(text(), 'tabung')]"
    ]
    CUSTOMER_LIST = [
        (By.CLASS_NAME, "styles_listTransactionRoot__pvz4r"),
        (By.CLASS_NAME, "mantine-1uguyhf"),
        (By.XPATH, "//div[@class='styles_listTransactionRoot__pvz4r mantine-1uguyhf']")
    ]
    REKAP_PENJUALAN = (By.XPATH, "//*[contains(text(), 'Rekap Penjualan')]")

# ========== INPUT SELECTORS ==========
class InputSelectors:
    EMAIL_TYPES = ["text", "email"]
    PASSWORD_TYPE = "password"
    BUTTON_TEXTS = ["MASUK", "LOGIN"]
