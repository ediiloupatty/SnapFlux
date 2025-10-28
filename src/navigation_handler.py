"""
Navigation handler untuk mengelola navigasi antar halaman
File ini berisi semua fungsi untuk navigasi di dalam aplikasi web
"""
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from .constants import BULAN_ID, BULAN_SINGKAT

def click_laporan_penjualan_direct(driver):
    """Klik menu 'Laporan Penjualan' langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n📊 === KLIK LAPORAN PENJUALAN LANGSUNG ===")
    try:
        time.sleep(1.5)
        print("🚀 Mengklik Laporan Penjualan langsung menggunakan lokasi yang sudah diketahui...")
        try:
            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Laporan Penjualan')]")
            text = element.text.strip()
            if text and 'laporan' in text.lower() and 'penjualan' in text.lower():
                print(f"✅ Menu Laporan Penjualan ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                print(f"🔍 Debug Laporan Penjualan 1: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"🔍 Debug Laporan Penjualan Success: XPath='//*[contains(text(), 'Laporan Penjualan')]'")
                    print(f"✅ Berhasil mengklik menu: '{text}'")
                    time.sleep(2.0)
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
                    print(f"🔍 Debug Laporan Penjualan Fallback: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"🔍 Debug Laporan Penjualan Fallback Success: XPath='//*[contains(text(), 'Laporan Penjualan')]'")
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
        time.sleep(1)
        print("🔍 Mencari menu 'Atur Produk' atau 'Atur Stok & Harga'...")
        
        atur_produk_selectors = [
            "//*[(self::button or self::a or self::div or self::span) and contains(text(), 'Atur Produk')]",
            "//*[(self::button or self::a or self::div or self::span) and contains(text(), 'Atur Stok')]",
            "//*[contains(text(), 'Atur') and contains(text(), 'Harga')]"
        ]
        for selector in atur_produk_selectors:
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
                                    time.sleep(1.5)
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
            "//*[(self::button or self::a or self::div or self::span) and contains(text(), 'Laporan Penjualan')]",
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
        time.sleep(0.5)
        print("🚀 Mengklik elemen tanggal langsung menggunakan lokasi yang sudah diketahui...")
        
        # === STEP 1: Klik "Atur Rentang Waktu" langsung ===
        print("\n📅 === STEP 1: KLIK 'ATUR RENTANG WAKTU' LANGSUNG ===")
        try:
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

        time.sleep(1)
                                
        # === STEP 2: Klik bulan tahun sesuai input user ===
        print("\n📅 === STEP 2: KLIK BULAN TAHUN SESUAI INPUT USER ===")
        
        # Tentukan bulan dan tahun berdasarkan input user - langsung gunakan format yang benar
        if selected_date:
            bulan_name = BULAN_ID[selected_date.month]
            tahun = selected_date.year
            # Langsung gunakan format yang benar (capitalize): Oktober 2025
            bulan_tahun_text = f"{bulan_name.lower().capitalize()} {tahun}"
            
            print(f"📅 Menggunakan tanggal input user: {selected_date.strftime('%d %B %Y')}")
            print(f"🎯 Mencari elemen langsung: '{bulan_tahun_text}'")
        else:
            today = datetime.now()
            bulan_name = BULAN_ID[today.month]
            tahun = today.year
            # Langsung gunakan format yang benar (capitalize): Oktober 2025
            bulan_tahun_text = f"{bulan_name.lower().capitalize()} {tahun}"
            
            print(f"📅 Menggunakan tanggal hari ini: {today.strftime('%d %B %Y')}")
            print(f"🎯 Mencari elemen langsung: '{bulan_tahun_text}'")
        
        # Langsung cari dengan format yang benar tanpa mencoba multiple format
        element_found = False
        
        try:
            # Langsung gunakan XPath dengan format yang sudah terbukti bekerja
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{bulan_tahun_text}')]")
            if elements:
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text and bulan_name.lower() in text.lower() and str(tahun) in text:
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                print(f"✅ Elemen bulan tahun ditemukan langsung!")
                                print(f"📝 Text: '{text}'")
                                print(f"✅ Berhasil mengklik bulan tahun: '{text}'")
                                element_found = True
                                break
                            else:
                                print("❌ Elemen tidak dapat diklik")
                        continue
                    except Exception as e_inner:
                        continue
                        
                if not element_found:
                    print(f"🔍 XPath langsung menemukan {len(elements)} elemen tapi tidak ada yang cocok")
            else:
                print(f"🔍 XPath langsung tidak menemukan elemen dengan text '{bulan_tahun_text}'")
        except Exception as e:
            print(f"🔍 XPath selector langsung tidak dapat digunakan, akan coba fallback")

        # Approach 2: Fallback dengan class selector jika approach 1 gagal
        if not element_found:
            print("🔄 Mencoba dengan class fallback...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-UnstyledButton-root")
                print(f"🔍 Ditemukan {len(elements)} elemen dengan class mantine-UnstyledButton-root")
                
                for idx, element in enumerate(elements[:10]):  # Limit search untuk performance
                    try:
                        text = element.text.strip()
                        if text and bulan_name.lower() in text.lower() and str(tahun) in text:
                            print(f"✅ Elemen bulan tahun ditemukan dengan class fallback!")
                            print(f"📝 Text: '{text}'")
                            
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                print(f"✅ Berhasil mengklik bulan tahun: '{text}'")
                                element_found = True
                                break
                            else:
                                print(f"❌ Elemen {idx+1} tidak dapat diklik")
                    except Exception as e3:
                        print(f"⚠️ Error dengan elemen {idx+1}: {str(e3)}")
                        continue

            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")

        if not element_found:
            print(f"❌ Elemen bulan tahun '{bulan_tahun_text}' tidak ditemukan dengan semua approach")
            return False

        time.sleep(2)
        
        # === STEP 3: Klik bulan singkat sesuai input user ===
        print("\n📅 === STEP 3: KLIK BULAN SINGKAT LANGSUNG ===")
        
        # Tentukan bulan singkat berdasarkan input user
        if selected_date:
            bulan_singkat = BULAN_SINGKAT[selected_date.month]
            print(f"🎯 Mengklik bulan singkat langsung: '{bulan_singkat}'")
        else:
            today = datetime.now()
            bulan_singkat = BULAN_SINGKAT[today.month]
            print(f"🎯 Mengklik bulan singkat langsung: '{bulan_singkat}'")
        
        bulan_singkat_found = False
        
        # Approach 1: Direct XPath dengan exact text match (gunakan find_elements untuk menghindari error)
        try:
            elements = driver.find_elements(By.XPATH, f"//*[text()='{bulan_singkat}']")
            if elements:
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text and text == bulan_singkat:
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                print(f"✅ Elemen bulan singkat ditemukan langsung!")
                                print(f"📝 Text: '{text}'")
                                print(f"✅ Berhasil mengklik bulan singkat: '{text}'")
                                bulan_singkat_found = True
                                break
                            else:
                                print("❌ Elemen tidak dapat diklik")
                        continue
                    except Exception as e_inner:
                        continue
                        
                if not bulan_singkat_found:
                    print(f"🔍 XPath langsung menemukan {len(elements)} elemen tapi tidak ada yang cocok dengan '{bulan_singkat}'")
            else:
                print(f"🔍 XPath langsung tidak menemukan elemen bulan singkat '{bulan_singkat}'")
        except Exception as e:
            print(f"🔍 XPath selector bulan singkat tidak dapat digunakan, akan coba fallback")

        # Approach 2: Fallback dengan class selector
        if not bulan_singkat_found:
            print("🔄 Mencoba dengan class fallback untuk bulan singkat...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-UnstyledButton-root")
                print(f"🔍 Mencari bulan singkat '{bulan_singkat}' dari {len(elements)} elemen")
                
                for idx, element in enumerate(elements[:15]):  # Limit search untuk performance
                    try:
                        text = element.text.strip()
                        if text and text == bulan_singkat:
                            print(f"✅ Elemen bulan singkat ditemukan dengan class fallback!")
                            print(f"📝 Text: '{text}'")
                            
                            if element.is_displayed() and element.is_enabled():
                                element.click()
                                print(f"✅ Berhasil mengklik bulan singkat: '{text}'")
                                bulan_singkat_found = True
                                break
                            else:
                                print(f"❌ Elemen bulan singkat {idx+1} tidak dapat diklik")
                    except Exception as e3:
                        continue

            except Exception as e2:
                print(f"❌ Error dengan class fallback bulan singkat: {str(e2)}")

        if not bulan_singkat_found:
            print(f"❌ Elemen bulan singkat '{bulan_singkat}' tidak ditemukan dengan semua approach")
            return False

        time.sleep(1)
        
        # === STEP 4: Klik tanggal spesifik sesuai input user ===
        print("\n📅 === STEP 4: KLIK TANGGAL SPESIFIK LANGSUNG ===")
        
        # Tentukan tanggal berdasarkan input user
        if selected_date:
            tanggal_hari = selected_date.day
            print(f"🎯 Mengklik tanggal langsung: '{tanggal_hari}'")
        else:
            today = datetime.now()
            tanggal_hari = today.day
            print(f"🎯 Mengklik tanggal langsung: '{tanggal_hari}'")
        
        # Klik tanggal sebanyak 2x langsung dengan cepat - robust approach
        element = None
        success_count = 0
        tanggal_found = False
        
        # Approach 1: Direct XPath dengan exact text match (gunakan find_elements untuk menghindari error)
        try:
            elements = driver.find_elements(By.XPATH, f"//*[text()='{tanggal_hari}']")
            if elements:
                for element_candidate in elements:
                    try:
                        text = element_candidate.text.strip()
                        if text and text == str(tanggal_hari):
                            if element_candidate.is_displayed() and element_candidate.is_enabled():
                                element = element_candidate
                                tanggal_found = True
                                print(f"✅ Elemen tanggal ditemukan langsung!")
                                print(f"📝 Text: '{text}'")
                                break
                            else:
                                print("❌ Elemen tanggal tidak dapat diklik")
                        continue
                    except Exception as e_inner:
                        continue
                        
                if not tanggal_found:
                    print(f"🔍 XPath langsung menemukan {len(elements)} elemen tapi tidak ada yang cocok dengan tanggal '{tanggal_hari}'")
            else:
                print(f"🔍 XPath langsung tidak menemukan elemen tanggal '{tanggal_hari}'")
        except Exception as e:
            print(f"🔍 XPath selector tanggal tidak dapat digunakan, akan coba fallback")

        # Approach 2: Fallback dengan class selector
        if not tanggal_found:
            print("🔄 Mencoba dengan class fallback untuk tanggal...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-UnstyledButton-root")
                print(f"🔍 Mencari tanggal '{tanggal_hari}' dari {len(elements)} elemen")
                
                for idx, element_candidate in enumerate(elements[:20]):  # Limit search untuk performance
                    try:
                        text = element_candidate.text.strip()
                        if text and text == str(tanggal_hari):
                            print(f"✅ Elemen tanggal ditemukan dengan class fallback!")
                            print(f"📝 Text: '{text}'")
                            
                            if element_candidate.is_displayed() and element_candidate.is_enabled():
                                element = element_candidate
                                tanggal_found = True
                                break
                            else:
                                print(f"❌ Elemen tanggal {idx+1} tidak dapat diklik")
                    except Exception as e3:
                        continue

            except Exception as e2:
                print(f"❌ Error dengan class fallback tanggal: {str(e2)}")

        if not tanggal_found:
            print(f"❌ Elemen tanggal '{tanggal_hari}' tidak ditemukan dengan semua approach")
            return False

        # Klik tanggal sebanyak 2x dengan cepat setelah elemen ditemukan
        if element and tanggal_found:
            try:
                # Klik 2x dengan cepat tanpa delay panjang
                for klik_ke in range(1, 3):  # Klik 2x
                    try:
                        element.click()
                        success_count += 1
                        print(f"✅ Berhasil mengklik tanggal ke-{klik_ke}: '{text}'")
                        
                        # Delay singkat hanya di antara klik (0.2 detik)
                        if klik_ke < 2:
                            time.sleep(0.2)
                            
                    except Exception as e2:
                        print(f"⚠️ Error pada klik ke-{klik_ke}: {str(e2)}")
                        # Tetap lanjut ke klik berikutnya
                        continue
                
                if success_count >= 1:  # Minimal 1 klik berhasil
                    print(f"✅ Total {success_count} klik berhasil dilakukan!")
                    return True
                else:
                    print("❌ Tidak ada klik yang berhasil")
                    return False
            except Exception as e:
                print(f"❌ Error saat klik tanggal: {str(e)}")
                return False
        
    except Exception as e:
        print(f"❌ Error mengklik elemen tanggal: {str(e)}")
        return False

def click_date_elements_rekap_penjualan(driver, selected_date=None):
    """Klik elemen tanggal di halaman Rekap Penjualan dengan flexible dynamic selector"""
    print("\n📅 === KLIK ELEMEN TANGGAL DI REKAP PENJUALAN ===")
    
    try:
        time.sleep(1.5)
        print("🚀 Mencari elemen filter tanggal di Rekap Penjualan...")
        
        # === STEP 1: Klik "Atur Rentang Waktu" dengan ID selector (STABIL) ===
        print("\n📅 === STEP 1: KLIK 'ATUR RENTANG WAKTU' DENGAN ID SELECTOR ===")
        date_filter_found = False
        
        try:
            # Primary: ID selector (STABIL berdasarkan terminal output)
            element = driver.find_element(By.ID, "mantine-rk-label")
            text = element.text.strip()
            if text and 'atur' in text.lower() and 'rentang' in text.lower():
                print(f"✅ Elemen filter tanggal ditemukan dengan ID selector!")
                print(f"📝 Text: '{text}'")
                print(f"🔍 Debug Filter Tanggal: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"🔍 Debug Filter Tanggal Success: ID='mantine-rk-label'")
                    date_filter_found = True
                else:
                    print("❌ Elemen tidak dapat diklik")
            else:
                print("❌ Elemen tidak mengandung 'Atur Rentang Waktu'")
        except Exception as e:
            print(f"⚠️ Error dengan ID selector: {str(e)}")
            print("🔄 Mencoba dengan XPath fallback...")
            
            # Fallback: XPath text-based
            try:
                element = driver.find_element(By.XPATH, "//*[contains(text(), 'Atur Rentang Waktu')]")
                text = element.text.strip()
                if text and 'atur' in text.lower() and 'rentang' in text.lower():
                    print(f"✅ Elemen filter tanggal ditemukan dengan XPath fallback!")
                    print(f"📝 Text: '{text}'")
                    print(f"🔍 Debug Filter Tanggal: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"🔍 Debug Filter Tanggal Success: XPath='//*[contains(text(), 'Atur Rentang Waktu')]'")
                        date_filter_found = True
                    else:
                        print("❌ Elemen tidak dapat diklik")
            except Exception as e2:
                print(f"❌ Error dengan XPath fallback: {str(e2)}")
        
        if not date_filter_found:
            print("⚠️ Elemen filter tanggal tidak ditemukan di Rekap Penjualan")
            print("ℹ️ Akan lanjut tanpa filter tanggal")
            return False
        
        time.sleep(1)
        
        # === STEP 2: Klik bulan tahun dengan flexible dynamic selector ===
        print("\n📅 === STEP 2: KLIK BULAN TAHUN DENGAN FLEXIBLE DYNAMIC SELECTOR ===")
        
        # Tentukan bulan dan tahun berdasarkan input user
        if selected_date:
            bulan_name = BULAN_ID[selected_date.month]
            tahun = selected_date.year
            bulan_tahun_text = f"{bulan_name.lower().capitalize()} {tahun}"
        else:
            today = datetime.now()
            bulan_name = BULAN_ID[today.month]
            tahun = today.year
            bulan_tahun_text = f"{bulan_name.lower().capitalize()} {tahun}"
        
        print(f"🎯 Mencari elemen bulan tahun: '{bulan_tahun_text}'")
        
        bulan_tahun_found = False
        
        # Tier 1: XPath dengan dynamic text (FAST)
        try:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{bulan_tahun_text}')]")
            for element in elements:
                text = element.text.strip()
                if text and bulan_name.lower() in text.lower() and str(tahun) in text:
                    if element.is_displayed() and element.is_enabled():
                        print(f"🔍 Debug Bulan Tahun: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                        element.click()
                        print(f"🔍 Debug Bulan Tahun Success: XPath='//*[contains(text(), '{bulan_tahun_text}')]'")
                        print(f"✅ Berhasil mengklik bulan tahun: '{text}'")
                        bulan_tahun_found = True
                        break
        except Exception as e:
            print(f"⚠️ Error dengan XPath dynamic: {str(e)}")
        
        # Tier 2: Class + validasi text (FALLBACK)
        if not bulan_tahun_found:
            print("🔄 Mencoba dengan class fallback...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-CalendarHeader-calendarHeaderLevel")
                for element in elements:
                    text = element.text.strip()
                    if text and bulan_name.lower() in text.lower() and str(tahun) in text:
                        if element.is_displayed() and element.is_enabled():
                            print(f"✅ Elemen bulan tahun ditemukan dengan class fallback!")
                            print(f"📝 Text: '{text}'")
                            element.click()
                            print(f"✅ Berhasil mengklik bulan tahun: '{text}'")
                            bulan_tahun_found = True
                            break
            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")
        
        if not bulan_tahun_found:
            print(f"❌ Elemen bulan tahun '{bulan_tahun_text}' tidak ditemukan")
            return False
        
        time.sleep(1)
        
        # === STEP 3: Klik bulan singkat dengan flexible dynamic selector ===
        print("\n📅 === STEP 3: KLIK BULAN SINGKAT DENGAN FLEXIBLE DYNAMIC SELECTOR ===")
        
        # Tentukan bulan singkat berdasarkan input user
        if selected_date:
            bulan_singkat = BULAN_SINGKAT[selected_date.month]
        else:
            today = datetime.now()
            bulan_singkat = BULAN_SINGKAT[today.month]
        
        print(f"🎯 Mencari elemen bulan singkat: '{bulan_singkat}'")
        
        bulan_singkat_found = False
        
        # Tier 1: XPath exact match (FAST)
        try:
            elements = driver.find_elements(By.XPATH, f"//*[text()='{bulan_singkat}']")
            for element in elements:
                text = element.text.strip()
                if text and text == bulan_singkat:
                    if element.is_displayed() and element.is_enabled():
                        print(f"🔍 Debug Bulan Singkat: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                        element.click()
                        print(f"🔍 Debug Bulan Singkat Success: XPath='//*[text()='{bulan_singkat}']'")
                        print(f"✅ Berhasil mengklik bulan singkat: '{text}'")
                        bulan_singkat_found = True
                        break
        except Exception as e:
            print(f"⚠️ Error dengan XPath exact match: {str(e)}")
        
        # Tier 2: Class + validasi text (FALLBACK)
        if not bulan_singkat_found:
            print("🔄 Mencoba dengan class fallback...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-PickerControl-pickerControl")
                for element in elements:
                    text = element.text.strip()
                    if text and text == bulan_singkat:
                        if element.is_displayed() and element.is_enabled():
                            print(f"✅ Elemen bulan singkat ditemukan dengan class fallback!")
                            print(f"📝 Text: '{text}'")
                            element.click()
                            print(f"✅ Berhasil mengklik bulan singkat: '{text}'")
                            bulan_singkat_found = True
                            break
            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")
        
        if not bulan_singkat_found:
            print(f"❌ Elemen bulan singkat '{bulan_singkat}' tidak ditemukan")
            return False
        
        time.sleep(1)
        
        # === STEP 4: Klik tanggal spesifik dengan flexible dynamic selector ===
        print("\n📅 === STEP 4: KLIK TANGGAL SPESIFIK DENGAN FLEXIBLE DYNAMIC SELECTOR ===")
        
        # Tentukan tanggal berdasarkan input user
        if selected_date:
            tanggal_hari = selected_date.day
        else:
            today = datetime.now()
            tanggal_hari = today.day
        
        print(f"🎯 Mencari elemen tanggal: '{tanggal_hari}'")
        
        tanggal_found = False
        
        # Tier 1: XPath exact match (FAST)
        try:
            elements = driver.find_elements(By.XPATH, f"//*[text()='{tanggal_hari}']")
            for element in elements:
                text = element.text.strip()
                if text and text == str(tanggal_hari):
                    if element.is_displayed() and element.is_enabled():
                        print(f"🔍 Debug Tanggal: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                        element.click()
                        print(f"🔍 Debug Tanggal Success: XPath='//*[text()='{tanggal_hari}']'")
                        print(f"✅ Berhasil mengklik tanggal: '{text}'")
                        time.sleep(0.2)
                        element.click()  # Klik 2x
                        print(f"✅ Berhasil mengklik tanggal 2x: '{text}'")
                        tanggal_found = True
                        break
        except Exception as e:
            print(f"⚠️ Error dengan XPath exact match: {str(e)}")
        
        # Tier 2: Class + validasi text (FALLBACK)
        if not tanggal_found:
            print("🔄 Mencoba dengan class fallback...")
            try:
                elements = driver.find_elements(By.CLASS_NAME, "mantine-Day-day")
                for element in elements:
                    text = element.text.strip()
                    if text and text == str(tanggal_hari):
                        if element.is_displayed() and element.is_enabled():
                            print(f"✅ Elemen tanggal ditemukan dengan class fallback!")
                            print(f"📝 Text: '{text}'")
                            element.click()
                            print(f"✅ Berhasil mengklik tanggal: '{text}'")
                            time.sleep(0.2)
                            element.click()  # Klik 2x
                            print(f"✅ Berhasil mengklik tanggal 2x: '{text}'")
                            tanggal_found = True
                            break
            except Exception as e2:
                print(f"❌ Error dengan class fallback: {str(e2)}")
        
        if not tanggal_found:
            print(f"❌ Elemen tanggal '{tanggal_hari}' tidak ditemukan")
            return False
        
        time.sleep(1)
        
        print("✅ Berhasil mengklik elemen tanggal di Rekap Penjualan!")
        return True
        
    except Exception as e:
        print(f"❌ Error mengklik elemen tanggal di Rekap Penjualan: {str(e)}")
        return False

def click_rekap_penjualan_direct(driver):
    """Klik menu 'Rekap Penjualan' langsung menggunakan lokasi yang sudah diketahui - lebih cepat"""
    print("\n📈 === KLIK REKAP PENJUALAN LANGSUNG ===")
    
    try:
        time.sleep(2)
        print("🚀 Mengklik Rekap Penjualan langsung menggunakan lokasi yang sudah diketahui...")
        
        try:
            element = driver.find_element(By.XPATH, "//*[contains(text(), 'Rekap Penjualan')]")
            text = element.text.strip()
            
            if text and 'rekap' in text.lower() and 'penjualan' in text.lower():
                print(f"✅ Menu Rekap Penjualan ditemukan langsung!")
                print(f"📝 Text: '{text}'")
                print(f"🔍 Debug Rekap Penjualan: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    print(f"🔍 Debug Rekap Penjualan Success: XPath='//*[contains(text(), 'Rekap Penjualan')]'")
                    print(f"✅ Berhasil mengklik menu: '{text}'")
                    
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
                        print(f"🔍 Debug Rekap Penjualan Fallback: Text='{text}', Tag={element.tag_name}, Class={element.get_attribute('class')}, ID={element.get_attribute('id')}, Location={element.location}, Size={element.size}")
                        
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            print(f"🔍 Debug Rekap Penjualan Fallback Success: XPath='//*[contains(text(), 'Rekap Penjualan')]'")
                            print(f"✅ Berhasil mengklik menu: '{text}'")
                            
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
