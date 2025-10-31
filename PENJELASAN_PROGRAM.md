# Penjelasan Dasar Program SnapFlux v2

## Apa itu Program Ini?

Program ini adalah **automasi web scraping** untuk mengambil data dari platform merchant Pertamina secara otomatis. Bayangkan seperti robot yang bisa membuka browser, login, klik tombol, dan mengambil data dari halaman web - semua dilakukan secara otomatis tanpa kita harus klik manual.

---

## Bagaimana Cara Kerjanya?

### 1. **Mencari Elemen dengan Selector**

Program menggunakan **Selenium WebDriver** untuk mencari elemen di halaman web. Ada beberapa cara mencari elemen:

#### A. **XPath** (seperti alamat lengkap)
```python
# Contoh: Mencari tombol dengan teks "CEK PESANAN"
driver.find_element(By.XPATH, "//button[contains(text(), 'CEK PESANAN')]")
```

**Penjelasan:**
- `//button` = cari semua tag `<button>`
- `[contains(text(), 'CEK PESANAN')]` = yang teksnya mengandung "CEK PESANAN"

**Analoginya:** Seperti mencari rumah dengan alamat lengkap: "Jalan Raya No. 123, RT 05, RW 02"

#### B. **Class Name** (seperti nama kelas)
```python
# Contoh: Mencari elemen dengan class "styles_summaryProductCard__Uv3IK"
element = driver.find_element(By.CLASS_NAME, "styles_summaryProductCard__Uv3IK")
```

**Penjelasan:**
- Mencari elemen HTML yang punya class `styles_summaryProductCard__Uv3IK`

**Analoginya:** Seperti mencari semua siswa di kelas "Kelas 3A"

#### C. **ID** (seperti nomor identitas unik)
```python
# Contoh: Mencari input dengan ID tertentu
nik_input = driver.find_element(By.ID, "mantine-r123")
```

**Analoginya:** Seperti mencari seseorang dengan NIK spesifik

---

### 2. **Alur Kerja Program (Flow)**

Program bekerja seperti langkah-langkah berikut:

```
1. LOGIN
   -> Buka browser Chrome
   -> Buka halaman login
   -> Cari input username (pakai XPath/Class/ID)
   -> Isi username
   -> Cari input password/PIN
   -> Isi password/PIN
   -> Cari tombol "Login"
   -> Klik tombol login

2. AMBIL DATA STOK
   -> Setelah login, halaman dashboard muncul
   -> Cari elemen yang berisi data stok
   -> Ambil teks dari elemen tersebut
   -> Extract angka dari teks (misalnya "150 tabung" -> ambil "150")

3. NAVIGASI KE LAPORAN PENJUALAN
   -> Cari menu/tombol "Laporan Penjualan"
   -> Klik tombol tersebut
   -> Tunggu halaman baru muncul

4. AMBIL DATA TABUNG TERJUAL
   -> Cari elemen yang berisi data "28 Tabung"
   -> Ambil teks dari elemen
   -> Extract angka (misalnya "28 Tabung" -> ambil "28")

5. SIMPAN KE EXCEL
   -> Buat file Excel
   -> Tulis data yang sudah diambil
   -> Simpan file
```

---

## Contoh Konkret: Bagaimana Program Mencari Elemen?

Mari kita lihat contoh dari kode program:

### **Contoh 1: Mencari Data Stok**

```python
def get_stock_value_direct(driver):
    # 1. Cari elemen dengan CLASS NAME
    element = driver.find_element(By.CLASS_NAME, "styles_summaryProductCard__Uv3IK")
    
    # 2. Ambil teks dari elemen tersebut
    text = element.text.strip()  # Contoh: "150 tabung tersedia"
    
    # 3. Extract angka dari teks menggunakan regex
    numbers = re.findall(r'\d+', text)  # Hasil: ["150"]
    
    # 4. Ambil angka pertama
    stock_value = numbers[0]  # Hasil: "150"
    
    return stock_value
```

**Penjelasan langkah demi langkah:**
1. Program mencari elemen yang punya class `styles_summaryProductCard__Uv3IK`
2. Ambil teks yang ada di dalam elemen tersebut
3. Gunakan regex untuk mengambil semua angka dari teks
4. Return angka pertama yang ditemukan

**Di browser, elemen HTML-nya mungkin seperti ini:**
```html
<div class="styles_summaryProductCard__Uv3IK">
    Stok: 150 tabung tersedia
</div>
```

---

### **Contoh 2: Mencari dan Klik Tombol**

```python
def click_cek_pesanan(driver):
    # 1. Coba beberapa selector sekaligus (fallback strategy)
    candidate_selectors = [
        # XPath pertama: cari button dengan teks "CEK PESANAN"
        (By.XPATH, "//button[contains(text(), 'CEK PESANAN')]"),
        # XPath kedua: alternatif jika pertama gagal
        (By.XPATH, "//*[self::button or self::a][contains(., 'CEK PESANAN')]"),
        # Class name: alternatif ketiga
        (By.CLASS_NAME, "mantine-Button-root")
    ]
    
    # 2. Loop melalui semua selector sampai ketemu
    for how, value in candidate_selectors:
        elements = driver.find_elements(how, value)
        for el in elements:
            # 3. Cek apakah ini tombol yang benar
            if "CEK" in el.text and "PESANAN" in el.text:
                # 4. Klik tombol
                el.click()
                return True
    
    return False
```

**Penjelasan:**
- Program mencoba beberapa cara untuk mencari tombol (strategi fallback)
- Jika cara pertama gagal, coba cara kedua, lalu ketiga
- Setelah menemukan tombol yang benar, langsung klik

---

### **Contoh 3: Mengisi Form NIK**

```python
def fill_nik_form_and_continue(driver, nik_list):
    # 1. Cari input field NIK dengan beberapa cara
    nik_input = None
    
    # Cara 1: Cari dengan XPath yang mencari ID yang mengandung "mantine-r"
    input_elements = driver.find_elements(By.XPATH, "//input[contains(@id, 'mantine-r')]")
    if input_elements:
        nik_input = input_elements[0]
    
    # Cara 2 (fallback): Cari dengan placeholder
    if not nik_input:
        nik_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, 'NIK')]")
    
    # 2. Isi NIK ke input field
    nik_input.clear()  # Hapus isian sebelumnya
    nik_input.send_keys("1234567890123456")  # Ketik NIK
    
    # 3. Cari tombol "LANJUTKAN PENJUALAN"
    continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'LANJUTKAN')]")
    
    # 4. Klik tombol
    continue_button.click()
```

**Penjelasan:**
- Program mencari input field dengan beberapa strategi (ID, placeholder)
- Setelah ketemu, isi dengan NIK
- Cari tombol "LANJUTKAN" lalu klik

---

## Kenapa Pakai Beberapa Selector (Fallback)?

Halaman web kadang berubah-ubah strukturnya. Misalnya:
- **Hari ini:** Tombol punya class `button-primary`
- **Besok:** Class berubah jadi `btn-primary`

Dengan menggunakan **beberapa selector sekaligus**, program tetap bisa berjalan meskipun ada perubahan kecil di halaman web.

**Contoh dari kode:**
```python
# Coba cara 1
try:
    button = driver.find_element(By.CLASS_NAME, "button-primary")
except:
    # Jika gagal, coba cara 2
    try:
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
    except:
        # Jika masih gagal, coba cara 3
        button = driver.find_element(By.ID, "login-btn")
```

---

## Fitur Utama Program

### 1. **Check Stok**
- Login ke semua akun
- Ambil data stok dari dashboard
- Ambil data tabung terjual dari laporan
- Simpan ke Excel

### 2. **Batalkan Inputan**
- Login ke semua akun
- Lihat data pembeli yang beli >1 tabung
- Tampilkan di terminal

### 3. **Catat Penjualan**
- Login ke akun
- Isi form NIK
- Proses penjualan otomatis
- Handle captcha

---

## Istilah Penting

### **XPath**
- Seperti "alamat lengkap" untuk mencari elemen di HTML
- Contoh: `//div[@class='container']//button[1]` = "Tombol pertama di dalam div dengan class container"

### **Selector**
- Cara untuk "menunjuk" elemen tertentu di halaman
- Bisa pakai ID, Class, XPath, dll

### **WebDriver**
- Tool untuk mengontrol browser (Chrome, Firefox, dll)
- Bisa buka halaman, klik, ketik, ambil data

### **Fallback Strategy**
- Jika cara pertama gagal, coba cara lain
- Membuat program lebih "robust" (tahan terhadap perubahan)

---

## Contoh Real di Browser

Ketika program mencari tombol "CEK PESANAN", di browser HTML-nya mungkin seperti ini:

```html
<button class="mantine-Button-root" type="button">
    CEK PESANAN
</button>
```

Program akan:
1. Cari dengan XPath: `//button[contains(text(), 'CEK PESANAN')]`
2. Atau cari dengan Class: `.mantine-Button-root`
3. Setelah ketemu, klik dengan `button.click()`

---

## Kesimpulan

**Program ini bekerja seperti:**
1. **Membuka browser** secara otomatis
2. **Mencari elemen** di halaman web menggunakan XPath/Class/ID (seperti mencari alamat)
3. **Mengambil data** dari elemen tersebut (teks, angka, dll)
4. **Melakukan aksi** (klik, ketik, isi form)
5. **Menyimpan hasil** ke Excel atau tampilkan di terminal

**Sederhananya:** Program ini seperti asisten virtual yang bisa melakukan semua tugas manual di browser secara otomatis, 24/7 tanpa lelah!

