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
        time.sleep(1.0)
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


def read_nik_from_excel():
    """
    ============================================
    FUNGSI BACA NIK DARI FILE EXCEL
    ============================================
    
    Fungsi ini membaca daftar NIK dari file akun/NIK.xlsx
    dan mengembalikan list NIK yang siap digunakan.
    
    Returns:
        list: List NIK dalam format string, atau None jika gagal
    """
    print("\n📋 === BACA NIK DARI EXCEL ===")
    
    try:
        import openpyxl
        import os
        
        nik_file_path = "akun/NIK.xlsx"
        
        if not os.path.exists(nik_file_path):
            print(f"❌ File NIK tidak ditemukan: {nik_file_path}")
            return None
        
        print(f"📂 Membaca file NIK: {nik_file_path}")
        
        wb = openpyxl.load_workbook(nik_file_path)
        ws = wb.active
        
        print(f"📊 Sheet: {ws.title}")
        print(f"📊 Total rows: {ws.max_row}")
        
        nik_list = []
        
        # Baca NIK dari kolom A (mulai dari row 2, karena row 1 adalah header)
        for row in range(2, ws.max_row + 1):
            nik_value = ws.cell(row=row, column=1).value
            if nik_value and str(nik_value).strip():
                nik_list.append(str(nik_value).strip())
        
        print(f"✅ Berhasil membaca {len(nik_list)} NIK dari Excel")
        
        if nik_list:
            print(f"📝 NIK pertama: {nik_list[0]}")
            print(f"📝 NIK terakhir: {nik_list[-1]}")
        
        return nik_list
        
    except Exception as e:
        print(f"❌ Error membaca file NIK: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def fill_nik_form_and_continue(driver, nik_list, start_index=0):
    """
    ============================================
    FUNGSI ISI FORM NIK DAN LANJUTKAN PENJUALAN
    ============================================
    
    Fungsi ini mengisi form NIK di halaman Catat Penjualan
    dan mengklik tombol "LANJUTKAN PENJUALAN".
    
    Args:
        driver: WebDriver object yang sudah berada di halaman Catat Penjualan
        nik_list (list): List NIK yang akan diisi
        start_index (int): Index NIK yang akan dimulai (default: 0)
    
    Returns:
        bool: True jika berhasil mengisi form dan klik lanjutkan, False jika gagal
    """
    print(f"\n📝 === ISI FORM NIK DAN LANJUTKAN PENJUALAN ===")
    
    try:
        if not nik_list or start_index >= len(nik_list):
            print("❌ Tidak ada NIK yang tersedia atau index melebihi batas")
            return False
        
        nik_to_use = nik_list[start_index]
        print(f"🔢 Menggunakan NIK index {start_index}: {nik_to_use}")
        
        # Tunggu popup muncul
        print("⏳ Menunggu popup form NIK muncul...")
        time.sleep(1.0)
        
        # Cari input field NIK dengan direct approach
        nik_input = None
        try:
            # Coba cari input dengan ID yang berubah-ubah (mantine-rXX)
            input_elements = driver.find_elements(By.XPATH, "//input[contains(@id, 'mantine-r') and @type='text']")
            if input_elements:
                nik_input = input_elements[0]  # Ambil yang pertama
                print(f"✅ Input field NIK ditemukan dengan ID: {nik_input.get_attribute('id')}")
            else:
                # Fallback ke placeholder search
                nik_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'NIK')]")
                print(f"✅ Input field NIK ditemukan dengan placeholder")
        except:
            # Fallback ke class search
            try:
                nik_input = driver.find_element(By.CLASS_NAME, "mantine-Input-input")
                print(f"✅ Input field NIK ditemukan dengan class")
            except:
                print("❌ Input field NIK tidak ditemukan dengan semua metode")
                return False
        
        # Debug info (hanya jika berhasil)
        if nik_input:
            try:
                xpath = driver.execute_script("""
                    function absoluteXPath(el){
                      if(el.id) return '//*[@id="'+el.id+'"]';
                      const parts=[]; while(el && el.nodeType===1){
                        let ix=0, sib=el.previousSibling; while(sib){ if(sib.nodeType===1 && sib.nodeName===el.nodeName) ix++; sib=sib.previousSibling; }
                        parts.unshift(el.nodeName.toLowerCase()+'['+(ix+1)+']'); el=el.parentNode; }
                      return '//'+parts.join('/'); }
                    return absoluteXPath(arguments[0]);
                """, nik_input)
                css = driver.execute_script("""
                    function cssPath(el){ if (!(el instanceof Element)) return; const path=[]; while (el.nodeType===1){ let selector=el.nodeName.toLowerCase(); if (el.id){ selector+='#'+el.id; path.unshift(selector); break; } else { let sib=el, nth=1; while (sib=sib.previousElementSibling){ if (sib.nodeName.toLowerCase()==selector) nth++; } selector += ':nth-of-type('+nth+')'; path.unshift(selector); el=el.parentNode; } } return path.join(' > '); }
                    return cssPath(arguments[0]);
                """, nik_input)
                print(f"🔗 NIK Input XPath: {xpath}")
                print(f"🔗 NIK Input CSS: {css}")
            except Exception:
                pass
        
        if not nik_input:
            print("❌ Input field NIK tidak ditemukan")
            return False
        
        # Clear dan isi NIK
        print(f"📝 Mengisi NIK: {nik_to_use}")
        nik_input.clear()
        nik_input.send_keys(nik_to_use)
        
        # Tunggu sebentar untuk memastikan input terisi
        time.sleep(0.5)
        
        # Cari tombol "LANJUTKAN PENJUALAN" dengan direct approach
        continue_button = None
        try:
            # Coba cari tombol dengan text "LANJUTKAN PENJUALAN" langsung
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'LANJUTKAN PENJUALAN')]")
            if buttons:
                continue_button = buttons[0]  # Ambil yang pertama
                print(f"✅ Tombol LANJUTKAN PENJUALAN ditemukan: '{continue_button.text}'")
            else:
                # Fallback ke text "LANJUTKAN" saja
                buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'LANJUTKAN')]")
                if buttons:
                    continue_button = buttons[0]
                    print(f"✅ Tombol LANJUTKAN ditemukan: '{continue_button.text}'")
                else:
                    # Fallback ke class search
                    buttons = driver.find_elements(By.CLASS_NAME, "mantine-Button-root")
                    for button in buttons:
                        if 'LANJUTKAN' in button.text.strip().upper():
                            continue_button = button
                            print(f"✅ Tombol LANJUTKAN ditemukan dengan class: '{button.text}'")
                            break
        except Exception as e:
            print(f"⚠️ Error mencari tombol LANJUTKAN: {str(e)}")
        
        # Debug info (hanya jika berhasil)
        if continue_button:
            try:
                xpath = driver.execute_script("""
                    function absoluteXPath(el){
                      if(el.id) return '//*[@id="'+el.id+'"]';
                      const parts=[]; while(el && el.nodeType===1){
                        let ix=0, sib=el.previousSibling; while(sib){ if(sib.nodeType===1 && sib.nodeName===el.nodeName) ix++; sib=sib.previousSibling; }
                        parts.unshift(el.nodeName.toLowerCase()+'['+(ix+1)+']'); el=el.parentNode; }
                      return '//'+parts.join('/'); }
                    return absoluteXPath(arguments[0]);
                """, continue_button)
                css = driver.execute_script("""
                    function cssPath(el){ if (!(el instanceof Element)) return; const path=[]; while (el.nodeType===1){ let selector=el.nodeName.toLowerCase(); if (el.id){ selector+='#'+el.id; path.unshift(selector); break; } else { let sib=el, nth=1; while (sib=sib.previousElementSibling){ if (sib.nodeName.toLowerCase()==selector) nth++; } selector += ':nth-of-type('+nth+')'; path.unshift(selector); el=el.parentNode; } } return path.join(' > '); }
                    return cssPath(arguments[0]);
                """, continue_button)
                print(f"🔗 CEK LANJUTKAN XPath: {xpath}")
                print(f"🔗 CEK LANJUTKAN CSS: {css}")
            except Exception:
                pass
        
        if not continue_button:
            print("❌ Tombol LANJUTKAN PENJUALAN tidak ditemukan")
            return False
        
        # Klik tombol LANJUTKAN PENJUALAN
        print("🚀 Mengklik tombol LANJUTKAN PENJUALAN...")
        try:
            # Coba klik normal dulu
            continue_button.click()
        except Exception as click_error:
            print(f"⚠️ Klik normal gagal: {str(click_error)}")
            print("🔄 Mencoba JavaScript click...")
            try:
                # Fallback: JavaScript click
                driver.execute_script("arguments[0].click();", continue_button)
                print("✅ JavaScript click berhasil!")
            except Exception as js_error:
                print(f"❌ JavaScript click juga gagal: {str(js_error)}")
                raise js_error
        
        print("✅ Berhasil mengisi NIK dan mengklik LANJUTKAN PENJUALAN!")
        time.sleep(0.5)  # Tunggu halaman load
        
        # Langsung return True setelah berhasil mengisi NIK dan klik LANJUTKAN
        print("✅ Form NIK berhasil diisi dan LANJUTKAN PENJUALAN diklik!")
        return True
        
    except Exception as e:
        print(f"❌ Error mengisi form NIK: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def click_cek_pesanan(driver):
    """
    ============================================
    KLIK TOMBOL "CEK PESANAN"
    ============================================
    Mencari dan mengklik tombol CEK PESANAN pada halaman Penjualan.
    """
    print("\n🧾 === KLIK CEK PESANAN ===")
    try:
        time.sleep(0.5)

        candidate_selectors = [
            (By.XPATH, "//html[1]/body[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/form[1]/div[4]/div[1]/button[1]"),
            (By.XPATH, "//button[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'CEK PESANAN')]") ,
            (By.XPATH, "//*[self::button or self::a][contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'CEK PESANAN')]") ,
            (By.XPATH, "//button[contains(@class,'button') and contains(., 'CEK')]") ,
            (By.CLASS_NAME, "mantine-Button-root")
        ]

        target = None
        for how, value in candidate_selectors:
            try:
                elements = driver.find_elements(how, value)
                for el in elements:
                    label = (el.text or "").strip().upper()
                    if "CEK" in label and "PESANAN" in label and el.is_enabled() and el.is_displayed():
                        target = el
                        break
                if target:
                    break
            except Exception:
                continue

        if not target:
            print("❌ Tombol CEK PESANAN tidak ditemukan")
            return False

        try:
            xpath = driver.execute_script("""
                function absoluteXPath(el){
                  if(el.id) return '//*[@id="'+el.id+'"]';
                  const parts=[]; while(el && el.nodeType===1){
                    let ix=0, sib=el.previousSibling; while(sib){ if(sib.nodeType===1 && sib.nodeName===el.nodeName) ix++; sib=sib.previousSibling; }
                    parts.unshift(el.nodeName.toLowerCase()+'['+(ix+1)+']'); el=el.parentNode; }
                  return '//'+parts.join('/'); }
                return absoluteXPath(arguments[0]);
            """, target)
            css = driver.execute_script("""
                function cssPath(el){ if (!(el instanceof Element)) return; const path=[]; while (el.nodeType===1){ let selector=el.nodeName.toLowerCase(); if (el.id){ selector+='#'+el.id; path.unshift(selector); break; } else { let sib=el, nth=1; while (sib=sib.previousElementSibling){ if (sib.nodeName.toLowerCase()==selector) nth++; } selector += ':nth-of-type('+nth+')'; path.unshift(selector); el=el.parentNode; } } return path.join(' > '); }
                return cssPath(arguments[0]);
            """, target)
            print(f"🔗 CEK PESANAN XPath: {xpath}")
            print(f"🔗 CEK PESANAN CSS: {css}")
        except Exception:
            pass
        print(f"✅ Tombol ditemukan: '{target.text.strip()}' — klik...")
        target.click()
        time.sleep(0.5)
        print("✅ Berhasil klik CEK PESANAN")
        return True

    except Exception as e:
        print(f"❌ Error klik CEK PESANAN: {str(e)}")
        return False


def click_proses_penjualan(driver):
    """
    ============================================
    KLIK TOMBOL "PROSES PENJUALAN" / "PROSES PESANAN"
    ============================================
    Pada halaman konfirmasi (Cek Penjualan), klik tombol proses.
    """
    print("\n🧾 === KLIK PROSES PENJUALAN ===")
    try:
        time.sleep(0.5)

        candidate_selectors = [
            (By.XPATH, "//html[1]/body[1]/div[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[4]/div[1]/button[1]"),
            (By.XPATH, "//button[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'PROSES PENJUALAN')]") ,
            (By.XPATH, "//button[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'PROSES PESANAN')]") ,
            (By.XPATH, "//*[self::button or self::a][contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'PROSES')]"),
            (By.CLASS_NAME, "mantine-Button-root")
        ]

        target = None
        for how, value in candidate_selectors:
            try:
                elements = driver.find_elements(how, value)
                for el in elements:
                    label = (el.text or "").strip().upper()
                    if "PROSES" in label and ("PENJUALAN" in label or "PESANAN" in label) and el.is_enabled() and el.is_displayed():
                        target = el
                        break
                if target:
                    break
            except Exception:
                continue

        if not target:
            print("❌ Tombol PROSES PENJUALAN tidak ditemukan")
            return False

        try:
            xpath = driver.execute_script("""
                function absoluteXPath(el){
                  if(el.id) return '//*[@id="'+el.id+'"]';
                  const parts=[]; while(el && el.nodeType===1){
                    let ix=0, sib=el.previousSibling; while(sib){ if(sib.nodeType===1 && sib.nodeName===el.nodeName) ix++; sib=sib.previousSibling; }
                    parts.unshift(el.nodeName.toLowerCase()+'['+(ix+1)+']'); el=el.parentNode; }
                  return '//'+parts.join('/'); }
                return absoluteXPath(arguments[0]);
            """, target)
            css = driver.execute_script("""
                function cssPath(el){ if (!(el instanceof Element)) return; const path=[]; while (el.nodeType===1){ let selector=el.nodeName.toLowerCase(); if (el.id){ selector+='#'+el.id; path.unshift(selector); break; } else { let sib=el, nth=1; while (sib=sib.previousElementSibling){ if (sib.nodeName.toLowerCase()==selector) nth++; } selector += ':nth-of-type('+nth+')'; path.unshift(selector); el=el.parentNode; } } return path.join(' > '); }
                return cssPath(arguments[0]);
            """, target)
            print(f"🔗 PROSES PENJUALAN XPath: {xpath}")
            print(f"🔗 PROSES PENJUALAN CSS: {css}")
        except Exception:
            pass
        print(f"✅ Tombol ditemukan: '{target.text.strip()}' — klik...")
        target.click()
        time.sleep(0.5)
        print("✅ Berhasil klik PROSES PENJUALAN")
        return True

    except Exception as e:
        print(f"❌ Error klik PROSES PENJUALAN: {str(e)}")
        return False


def wait_for_captcha_and_success(driver, max_wait_seconds=180):
    """
    Menunggu user menyelesaikan captcha (slider) lalu mendeteksi halaman sukses transaksi.
    Strategi:
    - Tampilkan instruksi di terminal agar user menyelesaikan captcha.
    - Polling DOM tiap 0.5s untuk indikator sukses seperti 'LUNAS' atau tombol 'KIRIM STRUK KE PELANGGAN'.
    - Timeout default 180 detik.
    """
    print("\n🧩 === MENUNGGU USER SELESAIKAN CAPTCHA ===")
    try:
        print("Silakan selesaikan captcha pada popup (geser untuk cocokan gambar).")
        print("Setelah selesai, sistem akan otomatis mendeteksi halaman sukses.")

        waited = 0.0
        success_detected = False
        while waited < max_wait_seconds:
            try:
                # Indikator sukses potensial
                indicators = [
                    (By.XPATH, "//*[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'LUNAS')]") ,
                    (By.XPATH, "//*[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'KIRIM STRUK KE PELANGGAN')]") ,
                    (By.XPATH, "//*[contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'INFORMASI TRANSAKSI PELANGGAN')]") ,
                ]
                for how, sel in indicators:
                    els = driver.find_elements(how, sel)
                    if els:
                        success_detected = True
                        break
                if success_detected:
                    print("✅ Halaman sukses transaksi terdeteksi (LUNAS / Informasi Transaksi).")
                    return True
            except Exception:
                pass

            time.sleep(0.5)
            waited += 0.5

        print("❌ Timeout menunggu penyelesaian captcha / halaman sukses tidak terdeteksi.")
        return False

    except Exception as e:
        print(f"❌ Error saat menunggu captcha/sukses: {str(e)}")
        return False


def click_kembali_ke_halaman_utama(driver):
    """
    Klik tombol 'KEMBALI KE HALAMAN UTAMA' pada halaman sukses transaksi.
    Menggunakan direct text match dan fallback class.
    """
    print("\n🏠 === KLIK KEMBALI KE HALAMAN UTAMA ===")
    try:
        time.sleep(0.5)

        candidates = [
            (By.XPATH, "//*[self::button or self::a][contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'KEMBALI KE HALAMAN UTAMA')]") ,
            (By.XPATH, "//button[contains(@class,'button') and contains(translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'KEMBALI')]") ,
            (By.CLASS_NAME, "mantine-Button-root")
        ]

        target = None
        for how, sel in candidates:
            try:
                els = driver.find_elements(how, sel)
                for el in els:
                    txt = (el.text or '').strip().upper()
                    if 'KEMBALI' in txt and 'HALAMAN' in txt:
                        if el.is_displayed() and el.is_enabled():
                            target = el
                            break
                if target:
                    break
            except Exception:
                continue

        if not target:
            print("❌ Tombol 'KEMBALI KE HALAMAN UTAMA' tidak ditemukan")
            return False

        # Cetak selector bantu
        try:
            xpath = driver.execute_script("""
                function absoluteXPath(el){ if(el.id) return '//*[@id="'+el.id+'"]';
                  const parts=[]; while(el && el.nodeType===1){ let ix=0, sib=el.previousSibling; while(sib){ if(sib.nodeType===1 && sib.nodeName===el.nodeName) ix++; sib=sib.previousSibling; }
                  parts.unshift(el.nodeName.toLowerCase()+'['+(ix+1)+']'); el=el.parentNode; } return '//'+parts.join('/'); }
                return absoluteXPath(arguments[0]);
            """, target)
            css = driver.execute_script("""
                function cssPath(el){ if (!(el instanceof Element)) return; const path=[]; while (el.nodeType===1){ let selector=el.nodeName.toLowerCase(); if (el.id){ selector+='#'+el.id; path.unshift(selector); break; } else { let sib=el, nth=1; while (sib=sib.previousElementSibling){ if (sib.nodeName.toLowerCase()==selector) nth++; } selector += ':nth-of-type('+nth+')'; path.unshift(selector); el=el.parentNode; } } return path.join(' > '); }
                return cssPath(arguments[0]);
            """, target)
            print(f"🔗 KEMBALI XPath: {xpath}")
            print(f"🔗 KEMBALI CSS: {css}")
        except Exception:
            pass

        print("🚀 Klik 'KEMBALI KE HALAMAN UTAMA'...")
        target.click()
        time.sleep(0.5)
        print("✅ Berhasil kembali ke halaman utama")
        return True

    except Exception as e:
        print(f"❌ Error klik kembali ke halaman utama: {str(e)}")
        return False

