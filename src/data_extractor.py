"""
Data extraction functions
File ini berisi semua fungsi untuk mengekstrak data dari halaman web
"""
import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By

def get_stock_value_direct(driver):
    """
    ============================================
    FUNGSI AMBIL DATA STOK DARI DASHBOARD
    ============================================
    
    Fungsi ini mengambil data stok dari dashboard merchant dengan menggunakan
    direct class selector yang sudah dioptimasi untuk performa maksimal.
    
    Proses yang dilakukan:
    1. Mencari elemen stok menggunakan class selector yang sudah diketahui
    2. Extract text dari elemen stok
    3. Menggunakan regex untuk mengambil angka pertama dari text
    4. Return nilai stok dalam format string
    
    Fungsi ini sangat cepat karena menggunakan direct selector tanpa iterasi
    dan sudah terbukti berhasil berdasarkan debugging sebelumnya.
    
    Args:
        driver: WebDriver object yang sudah login dan berada di dashboard
    
    Returns:
        str: Nilai stok dalam format string (contoh: "150"), atau None jika gagal
    """
    print("\n📦 === AMBIL DATA STOK LANGSUNG ===")
    try:
        time.sleep(1.5)
        print("🚀 Mengambil stok langsung menggunakan class yang sudah diketahui...")
        
        # Langsung ambil dengan class yang sudah terbukti berhasil
        element = driver.find_element(By.CLASS_NAME, "styles_summaryProductCard__Uv3IK")
        text = element.text.strip()
        
        print(f"✅ Elemen stok ditemukan langsung!")
        print(f"📝 Text: '{text}'")
        
        # Langsung extract angka pertama tanpa validasi tambahan
        numbers = re.findall(r'\d+', text)
        if numbers:
            stock_value = numbers[0]
            print(f"🔢 Angka: {numbers}")
            print(f"📊 Nilai Stok: {stock_value}")
            return stock_value
        else:
            print("❌ Tidak ada angka ditemukan dalam text")
            return None
            
    except Exception as e:
        print(f"❌ Error mengambil data stok: {str(e)}")
        return None

def get_tabung_terjual_direct(driver):
    """
    ============================================
    FUNGSI AMBIL DATA TABUNG TERJUAL DARI LAPORAN PENJUALAN
    ============================================
    
    Fungsi ini mengambil data tabung terjual dari halaman Laporan Penjualan dengan
    menggunakan direct selector yang sudah dioptimasi untuk performa maksimal.
    
    Proses yang dilakukan:
    1. Mencari elemen dengan class "mantine-Text-root" yang berisi data tabung
    2. Filter elemen yang mengandung kata "tabung" dan angka
    3. Skip elemen yang merupakan header "Total Tabung LPG 3 Kg Terjual"
    4. Extract angka dari text yang ditemukan
    5. Return data dalam format "X Tabung"
    6. Fallback ke XPath selector jika class selector gagal
    
    Fungsi ini sangat cepat karena menggunakan direct selector tanpa iterasi
    dan sudah terbukti berhasil berdasarkan debugging sebelumnya.
    
    Args:
        driver: WebDriver object yang sudah berada di halaman Laporan Penjualan
    
    Returns:
        str: Data tabung terjual dalam format "X Tabung" (contoh: "28 Tabung"), 
             atau None jika gagal mengambil data
    """
    print("\n📊 === AMBIL DATA TABUNG TERJUAL LANGSUNG ===")
    
    try:
        time.sleep(1.5)
        print("🚀 Mengambil data tabung terjual langsung menggunakan lokasi yang sudah diketahui...")
        
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
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        tabung_value = numbers[0]
                        clean_text = f"{tabung_value} Tabung"
                        print(f"🔢 Angka: {numbers}")
                        print(f"📊 Jumlah Tabung Terjual: {tabung_value}")
                        print(f"📝 Text Bersih: '{clean_text}'")
                        return clean_text
            
            print("❌ Data tabung terjual tidak ditemukan dengan class selector")
            return None
                
        except Exception as e:
            print(f"⚠️ Error dengan class selector: {str(e)}")
            
            # Fallback: gunakan XPath yang lebih spesifik berdasarkan text pattern
            print("🔄 Mencoba dengan XPath fallback yang lebih efisien...")
            try:
                fallback_selectors = [
                    "//*[contains(text(), 'Tabung')]",
                    "//div[contains(@class, 'text')]//*[contains(text(), 'tabung')]",
                    "//span[contains(text(), 'tabung')]",
                    "//p[contains(text(), 'tabung')]"
                ]
                for selector in fallback_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            text = element.text.strip()
                            if (text and len(text) < 50 and 
                                'tabung' in text.lower() and 
                                any(char.isdigit() for char in text) and 
                                'total' not in text.lower()):
                                
                                print(f"✅ Data tabung terjual ditemukan dengan XPath fallback!")
                                print(f"📝 Text: '{text}'")
                                
                                numbers = re.findall(r'\d+', text)
                                if numbers:
                                    tabung_value = numbers[0]
                                    clean_text = f"{tabung_value} Tabung"
                                    print(f"🔢 Angka: {numbers}")
                                    print(f"📊 Jumlah Tabung Terjual: {tabung_value}")
                                    print(f"📝 Text Bersih: '{clean_text}'")
                                    return clean_text
                    except:
                        continue
                                
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
                return None
            
    except Exception as e:
        print(f"❌ Error mengambil data tabung terjual: {str(e)}")
        return None

def get_customer_list_direct(driver):
    """Ambil data list pembeli langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n👥 === AMBIL DATA LIST PEMBELI LANGSUNG ===")
    
    try:
        time.sleep(3)
        print("🚀 Mengambil data list pembeli langsung menggunakan lokasi yang sudah diketahui...")
        
        try:
            elements = None
            customer_selectors = [
                (By.CLASS_NAME, "styles_listTransactionRoot__pvz4r"),
                (By.CLASS_NAME, "mantine-1uguyhf"),
                (By.XPATH, "//div[@class='styles_listTransactionRoot__pvz4r mantine-1uguyhf']")
            ]
            for selector_type, selector_value in customer_selectors:
                try:
                    if selector_type == By.CLASS_NAME:
                        elements = driver.find_elements(selector_type, selector_value)
                        if elements:
                            break
                    elif selector_type == By.XPATH:
                        elements = driver.find_elements(selector_type, selector_value)
                        if elements:
                            break
                except:
                    continue
            
            if elements:
                print(f"✅ Ditemukan {len(elements)} container pembeli langsung!")
                
                customer_data = []
                for idx, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        if text and ('tabung' in text.lower() and 'lpg' in text.lower()):
                            print(f"✅ Container pembeli {idx+1} ditemukan langsung!")
                            print(f"📝 Data: '{text[:50]}...'")
                            
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
                    for idx, customer in enumerate(customer_data[:3]):
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
            print(f"❌ Error mengambil data list pembeli: {str(e)}")
            return None
            
    except Exception as e:
        print(f"❌ Error mengambil data list pembeli: {str(e)}")
        return None

def should_click_rekap_penjualan(tabung_terjual_text):
    """Decision function: apakah perlu klik Rekap Penjualan berdasarkan data tabung terjual"""
    print(f"\n🤔 === DECISION: APAKAH PERLU KLIK REKAP PENJUALAN? ===")
    
    try:
        if not tabung_terjual_text:
            print("❌ Data tabung terjual kosong - SKIP Rekap Penjualan")
            return False
        
        print(f"📊 Data tabung terjual: '{tabung_terjual_text}'")
        
        # Ekstrak angka dari text "28 Tabung" atau "0 Tabung"
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
