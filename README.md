# SnapFlux Automation v2.0

Automation script untuk mengambil data transaksi dari platform Snapflux menggunakan Selenium WebDriver dengan enhanced features untuk standar perusahaan.

## 📋 Description

SnapFlux adalah aplikasi untuk automated web scraping dan data extraction dari portal [subsiditepatlpg.mypertamina.id](https://subsiditepatlpg.mypertamina.id). Aplikasi ini mengotomatisasi login, navigasi, dan pengambilan laporan menggunakan Selenium WebDriver.

## 🚀 Key Features

### Core Automation Features

- **Automated Login & Navigation** - Login otomatis ke portal merchant
- **Data Extraction** - Ekstraksi data penjualan dengan status dan timestamp
- **Excel Export** - Export hasil ke format Excel dengan struktur yang rapi
- **Headless Mode** - Mode tanpa GUI untuk performa optimal

### 📋 Main Menu Options

1. **Check Stok** - Automated stock monitoring dan penjualan tracking
   - Automatic stock data retrieval dari dashboard
   - Penjualan tracking dengan filter tanggal opsional
   - Excel export dengan format pivot yang rapi
2. **Batalkan Inputan** ⭐ NEW in v2
   - Navigasi ke Rekap Penjualan
   - Menampilkan list pembeli dari sistem
   - Support filter tanggal untuk pencarian spesifik
   - Fitur ini tidak tersedia di v1

### 🆕 Enhanced Enterprise Features (v2.0)

- **Environment Configuration Management** - Configuration via environment variables (optional YAML)
- **Comprehensive Error Handling** - Custom exceptions dan retry mechanism dengan exponential backoff
- **Security Improvements** - Credential encryption dan input sanitization
- **Basic Testing Framework** - Unit tests
- **Advanced Logging** - Structured logging dengan rotating file handler

## 🛠️ Technical Stack

- **Language**: Python 3.7+
- **Framework**: Selenium WebDriver
- **Browser**: Chrome/Chromium (bundled)
- **Data Export**: pandas + openpyxl
- **Configuration**: YAML (optional) + Environment Variables
- **Testing**: pytest
- **Platform**: Windows

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/ediiloupatty/SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina.git
cd SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Setup environment configuration (recommended)
cp env.example .env
# Edit .env dengan path dan konfigurasi Anda

# Setup account data (edit with your credentials)
cp akun/akun.xlsx.example akun/akun.xlsx

# Optional: Setup config.yaml for advanced configuration
cp config.yaml.example config.yaml
```

### 3. Run

```bash
python main.py
```

## ⚙️ Configuration

### Environment Variables (.env)

Copy `env.example` ke `.env` dan edit dengan konfigurasi Anda:

```bash
# Browser Configuration
CHROME_BINARY_PATH=D:\path\to\chrome.exe
CHROMEDRIVER_PATH=D:\path\to\chromedriver.exe

# Application Settings
LOGIN_URL=https://subsiditepatlpg.mypertamina.id/merchant-login
DEFAULT_DELAY=2.0
MAX_RETRIES=3
HEADLESS_MODE=true

# Security (Optional)
ENCRYPTION_KEY=your-encryption-key-here
```

### Account Configuration

Edit `akun/akun.xlsx` dengan:

- Nama pangkalan
- Username (email/phone)
- PIN credentials

### Advanced Configuration (Optional)

Edit `config.yaml` untuk advanced settings jika diperlukan.

## 💻 System Requirements

### Minimum

- **OS**: Windows 10 (64-bit)
- **Python**: 3.7+
- **RAM**: 4 GB
- **Storage**: 1–2 GB free space
- **Network**: ≥ 5 Mbps stable connection

### Recommended

- **OS**: Windows 11
- **Python**: 3.9+
- **RAM**: 8+ GB
- **Storage**: SSD dengan ≥ 5 GB free space
- **Network**: ≥ 10 Mbps stable connection

## 🔒 Security & Privacy

- **Account files** (`akun.xlsx`) tidak di-commit untuk keamanan
- **Browser profiles** dan cache tidak disimpan di Git
- **Log files** berisi informasi sensitif tidak di-upload
- **Template files** (`.example`) digunakan untuk konfigurasi

## 🛠️ Development

### Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Enhanced features dependencies (auto-included):
# - pyyaml>=6.0.0 (Configuration management)
# - cryptography>=3.4.8 (Security encryption)
# - python-dotenv>=0.19.0 (Environment variables)
```

### Key Components

#### Core Components

- **Selenium WebDriver** - Browser automation
- **pandas** - Data processing and Excel export
- **openpyxl** - Excel file operations

#### Enhanced Components (v2.0)

- **config_manager.py** - Environment & YAML configuration management
- **error_handler.py** - Comprehensive error handling dengan retry mechanism
- **exceptions.py** - Custom exception classes untuk better error tracking
- **security.py** - Credential encryption dan input sanitization
- **validators.py** - Input validation functions
- **tests/** - Unit testing framework

## 📊 Features in Detail

### Feature 1: Check Stok

- **Stock Monitoring**: Automatic stock data retrieval dari dashboard
- **Sales Tracking**: Data tabung terjual dengan format "X Tabung"
- **Date Filtering**: Filter reports by specific date ranges (opsional)
- **Status Detection**: Auto-detect status (Ada Penjualan/Tidak Ada Penjualan)
- **Excel Export**: Export hasil ke Excel dengan format pivot yang rapi
- **Progress Tracking**: Real-time progress monitoring dengan detailed logging

### Feature 2: Batalkan Inputan (NEW in v2)

- **Rekap Penjualan Navigation**: Otomatis navigasi ke halaman Rekap Penjualan
- **Customer List Display**: Menampilkan list pembeli dari Rekap Penjualan
- **Date Filtering**: Support filter tanggal untuk pencarian data spesifik
- **Real-time Data**: Live data retrieval dari sistem merchant
- **Terminal Display**: Menampilkan hasil langsung di terminal dengan format rapi
- **Status Tracking**: Track sukses/gagal untuk setiap akun yang diproses

> **Note**: Fitur Batalkan Inputan tidak tersedia di v1 dan merupakan fitur eksklusif v2.0

### Enhanced Enterprise Features (v2.0)

- **Environment Configuration**: Flexible configuration via `.env` files (optional YAML)
- **Advanced Error Handling**: Custom exceptions dengan retry mechanism dan exponential backoff
- **Security Features**: Credential encryption dan input sanitization
- **Testing Framework**: Unit tests dengan test fixtures
- **Structured Logging**: Rotating log files dengan proper error tracking

## 🆕 What's New in v2.0

### Major Features Added

1. **🆕 Fitur Batalkan Inputan** - Fitur baru untuk navigasi ke Rekap Penjualan dan menampilkan list pembeli (tidak tersedia di v1)

### Enterprise-Grade Improvements

Project ini telah ditingkatkan dengan 4 major enhancements untuk mencapai standar perusahaan:

1. **🌍 Environment Configuration Management**

   - Configuration via environment variables (`.env` file)
   - Optional YAML configuration support untuk advanced settings
   - Fallback strategy untuk backward compatibility

2. **🛡️ Comprehensive Error Handling**

   - Custom exception classes (`AuthenticationError`, `NavigationError`, etc.)
   - Retry mechanism dengan exponential backoff
   - Context logging untuk operation tracking

3. **🔒 Security Improvements**

   - Optional credential encryption dengan Fernet cryptography
   - Input sanitization untuk mencegah injection attacks
   - PIN validation dengan weak PIN detection

4. **🧪 Basic Testing Framework**
   - Unit tests untuk validator functions
   - Test fixtures dan mock objects untuk reliable testing

### Backward Compatibility

Semua enhancement features adalah **optional** dan tidak mengubah fungsi existing. Project tetap berfungsi dengan konfigurasi original jika enhanced features tidak digunakan.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Users are responsible for complying with the terms of service of the target platform and applicable laws.
