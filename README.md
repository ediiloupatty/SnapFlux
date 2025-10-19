# Snapflux Automation v2

Automation script untuk mengambil data transaksi dari platform Snapflux menggunakan Selenium WebDriver.

## 🚀 Setup Sebelum Push ke GitHub

### 1. File yang TIDAK akan di-push (dalam .gitignore):

- **Akun dan Data Sensitif:**

  - `akun/` - Folder berisi data akun (.xlsx files)
  - `config.yaml` - File konfigurasi yang mungkin berisi data sensitif

- **Browser dan Automation Files:**

  - `chrome/` - Browser binary dan driver executable
  - `chrome_profile/` - Browser profile data
  - `chromedriver.exe` - ChromeDriver executable
  - `drivers/` - WebDriver files

- **Log dan Results:**

  - `logs/` - File log automation
  - `results/` - Output Excel files
  - `*.log` - Semua file log

- **Cache dan Temporary:**
  - `__pycache__/` - Python cache
  - `*.tmp`, `*.temp` - Temporary files
  - `debug_calendar_selectors.txt` - Debug files

### 2. Sebelum Push - Buat File Template:

Buat file template untuk konfigurasi dan akun:

```bash
# Copy dan rename file konfigurasi
cp config.yaml config.yaml.example

# Copy dan rename file akun template
cp akun/akun.xlsx akun/akun.xlsx.example
```

### 3. Yang akan di-push ke GitHub:

- **Source Code:**

  - `main.py` - Entry point utama
  - `src/` - Folder berisi source code Python
  - `icon/` - Icons untuk GUI (jika ada)

- **Documentation:**

  - `README.md` - Dokumentasi proyek
  - `README_HEADLESS.md` - Dokumentasi mode headless

- **Configuration Templates:**
  - `config.yaml.example` - Template konfigurasi
  - `akun/akun.xlsx.example` - Template file akun

## 📋 Setup untuk Developer Baru

1. **Clone repository:**

   ```bash
   git clone <repository-url>
   cd snapflux-automation-v2
   ```

2. **Setup environment:**

   ```bash
   pip install -r requirements.txt  # Jika ada
   ```

3. **Setup konfigurasi:**

   ```bash
   cp config.yaml.example config.yaml
   cp akun/akun.xlsx.example akun/akun.xlsx
   ```

4. **Download ChromeDriver:**

   ```bash
   # Download ChromeDriver sesuai versi Chrome Anda
   # Letakkan di root folder sebagai chromedriver.exe
   ```

5. **Setup browser:**
   ```bash
   # Download Chrome/Chromium browser
   # Extract ke folder chrome/
   ```

## 🔧 Cara Menjalankan

```bash
python main.py
```

## 📁 Struktur Proyek

```
snapflux-automation-v2/
├── main.py                 # Entry point
├── src/                    # Source code
│   ├── login_handler.py    # Login automation
│   ├── utils.py            # Utility functions
│   └── driver_setup.py     # WebDriver setup
├── akun/                   # Account data (gitignored)
├── results/                # Output files (gitignored)
├── logs/                   # Log files (gitignored)
├── chrome/                 # Browser files (gitignored)
├── chrome_profile/         # Browser profile (gitignored)
├── config.yaml.example     # Config template
└── README.md               # This file
```

## ⚠️ Security Notes

- JANGAN commit file `akun.xlsx` yang berisi data akun real
- JANGAN commit `config.yaml` yang berisi konfigurasi sensitif
- SELALU gunakan `.example` files untuk template
- Browser binary dan driver terlalu besar untuk git (gunakan .gitignore)

## 🛠️ Development

Proyek ini menggunakan:

- Python 3.x
- Selenium WebDriver
- Chrome/Chromium browser
- pandas untuk Excel export

## 📝 License

[Tambahkan informasi license sesuai kebutuhan]
