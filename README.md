# SnapFlux Automation v2.0

Automation script untuk mengambil data transaksi dari platform Snapflux menggunakan Selenium WebDriver dengan enhanced features untuk standar perusahaan.

## 📋 Description

SnapFlux adalah aplikasi untuk automated web scraping dan data extraction dari portal [subsiditepatlpg.mypertamina.id](https://subsiditepatlpg.mypertamina.id).  
Aplikasi ini mengotomatisasi login, navigasi, dan pengambilan laporan menggunakan Selenium WebDriver.

## 🚀 Key Features

### Core Automation Features

- **Automated Login & Navigation** - Login otomatis ke portal merchant
- **Data Extraction** - Ekstraksi data penjualan dengan status dan timestamp
- **Stock Monitoring** - Automatic stock data retrieval jika data penjualan tidak ada
- **Excel Export** - Export hasil ke format Excel dengan struktur yang rapi
- **Headless Mode** - Mode tanpa GUI untuk performa optimal
- **Batch Processing** - Support multiple akun dalam satu run

### 🆕 Enhanced Enterprise Features (v2.0)

- **Environment Configuration Management** - Configuration via environment variables dan YAML
- **Comprehensive Error Handling** - Custom exceptions dan retry mechanism dengan exponential backoff
- **Security Improvements** - Credential encryption dan input sanitization
- **Basic Testing Framework** - Unit dan integration tests untuk code reliability
- **Advanced Logging** - Structured logging dengan rotating file handler

## 🛠️ Technical Stack

- **Language**: Python 3.7+
- **Framework**: Selenium WebDriver
- **Browser**: Chrome/Chromium (bundled)
- **Data Export**: pandas + openpyxl
- **Configuration**: YAML + Environment Variables
- **Security**: cryptography (Fernet encryption)
- **Testing**: pytest + coverage reporting
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

## 📁 Project Structure

```
SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina/
├── main.py                 # Main entry point
├── src/                    # Source code
│   ├── login_handler.py    # Login automation logic
│   ├── utils.py            # Utility functions
│   ├── driver_setup.py     # WebDriver configuration
│   ├── config_manager.py   # Environment configuration (NEW)
│   ├── exceptions.py       # Custom exceptions (NEW)
│   ├── error_handler.py    # Enhanced error handling (NEW)
│   ├── security.py         # Security utilities (NEW)
│   └── validators.py       # Input validation
├── tests/                  # Testing framework (NEW)
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── akun/                   # Account data (see .gitignore)
│   └── akun.xlsx.example   # Account template
├── results/                # Output Excel files (see .gitignore)
├── logs/                   # Automation logs (see .gitignore)
├── env.example             # Environment variables template (NEW)
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
└── README.md               # This file
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
- **tests/** - Unit dan integration testing framework

## 📊 Features in Detail

### Core Automation Features

- **Multi-Account Support**: Process multiple merchant accounts secara batch
- **Date Filtering**: Filter reports by specific date ranges
- **Progress Tracking**: Real-time progress monitoring dengan detailed logging
- **Export Options**: Excel export dengan conditional formatting

### Enhanced Enterprise Features (v2.0)

- **Environment Configuration**: Flexible configuration via `.env` files
- **Advanced Error Handling**: Custom exceptions dengan retry mechanism dan exponential backoff
- **Security Features**: Credential encryption dan input sanitization
- **Testing Framework**: Comprehensive unit dan integration tests
- **Structured Logging**: Rotating log files dengan proper error tracking

## 🆕 What's New in v2.0

### Enterprise-Grade Improvements

Project ini telah ditingkatkan dengan 4 major enhancements untuk mencapai standar perusahaan:

1. **🌍 Environment Configuration Management**

   - Configuration via environment variables (`.env` file)
   - YAML configuration support untuk advanced settings
   - Fallback strategy untuk backward compatibility

2. **🛡️ Comprehensive Error Handling**

   - Custom exception classes (`AuthenticationError`, `NavigationError`, etc.)
   - Retry mechanism dengan exponential backoff
   - Context logging untuk operation tracking

3. **🔒 Security Improvements**

   - Credential encryption dengan Fernet cryptography
   - Input sanitization untuk mencegah injection attacks
   - PIN validation dengan weak PIN detection

4. **🧪 Basic Testing Framework**
   - Unit tests untuk validator functions
   - Integration tests untuk configuration management
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
