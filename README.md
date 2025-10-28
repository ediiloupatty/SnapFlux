# SnapFlux Automation v2.0

Automated web scraping and data extraction tool for SnapFlux merchant platform using Selenium WebDriver with enterprise-grade features and optimized performance.

## 📋 Description

SnapFlux is an automated web scraping and data extraction application for the [subsiditepatlpg.mypertamina.id](https://subsiditepatlpg.mypertamina.id) merchant platform. This application automates login, navigation, and report extraction using Selenium WebDriver with optimized performance and enterprise-grade features.

## 🚀 Key Features

### Core Automation Features

- **Automated Login & Navigation** - Automatic login to merchant portal with optimized selectors
- **Data Extraction** - Sales data extraction with status tracking and timestamps
- **Excel Export** - Export results to Excel format with clean structure
- **Headless Mode** - GUI-less mode for optimal performance
- **Optimized Performance** - Direct selectors and streamlined code for faster execution

### 📋 Main Menu Options

1. **Check Stok** - Automated stock monitoring and sales tracking
   - Automatic stock data retrieval from dashboard
   - Sales tracking with optional date filtering
   - Excel export with clean pivot format
2. **Batalkan Inputan** ⭐ NEW in v2
   - Navigate to Sales Summary (Rekap Penjualan)
   - Display customer list from the system
   - Support date filtering for specific data search
   - Transaction cancellation workflow for duplicate entries

### 🆕 Enhanced Enterprise Features (v2.0)

- **Environment Configuration Management** - Configuration via environment variables (optional YAML)
- **Streamlined Codebase** - Removed unused modules for better performance and maintainability
- **Direct Selector Optimization** - Hardcoded selectors for faster element detection
- **Advanced Logging** - Structured logging with rotating file handler
- **Comprehensive Error Handling** - Robust error handling with retry mechanisms

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
# Edit .env with your paths and configuration

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

Copy `env.example` to `.env` and edit with your configuration:

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

Edit `akun/akun.xlsx` with:

- Pangkalan name
- Username (email/phone)
- PIN credentials

### Advanced Configuration (Optional)

Edit `config.yaml` for advanced settings if needed.

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
- **Storage**: SSD with ≥ 5 GB free space
- **Network**: ≥ 10 Mbps stable connection

## 🔒 Security & Privacy

- **Account files** (`akun.xlsx`) are not committed for security
- **Browser profiles** and cache are not stored in Git
- **Log files** contain sensitive information and are not uploaded
- **Template files** (`.example`) are used for configuration

## 🛠️ Development

### Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Enhanced features dependencies (auto-included):
# - pyyaml>=6.0.0 (Configuration management)
# - python-dotenv>=0.19.0 (Environment variables)
```

### Key Components

#### Core Components

- **Selenium WebDriver** - Browser automation
- **pandas** - Data processing and Excel export
- **openpyxl** - Excel file operations

#### Enhanced Components (v2.0)

- **config_manager.py** - Environment & YAML configuration management
- **validators.py** - Input validation functions
- **tests/** - Unit testing framework
- **Streamlined Architecture** - Removed unused modules for better performance

## 📊 Features in Detail

### Feature 1: Check Stok

- **Stock Monitoring**: Automatic stock data retrieval from dashboard
- **Sales Tracking**: Sales data with "X Tabung" format
- **Date Filtering**: Filter reports by specific date ranges (optional)
- **Status Detection**: Auto-detect status (Ada Penjualan/Tidak Ada Penjualan)
- **Excel Export**: Export results to Excel with clean pivot format
- **Progress Tracking**: Real-time progress monitoring with detailed logging

### Feature 2: Batalkan Inputan (NEW in v2)

- **Sales Summary Navigation**: Automatic navigation to Sales Summary (Rekap Penjualan) page
- **Customer List Display**: Display customer list from Sales Summary
- **Date Filtering**: Support date filtering for specific data search
- **Transaction Cancellation**: Workflow for canceling duplicate transactions
- **Real-time Data**: Live data retrieval from merchant system
- **Terminal Display**: Display results directly in terminal with clean format
- **Status Tracking**: Track success/failure for each processed account

> **Note**: Batalkan Inputan feature is not available in v1 and is exclusive to v2.0

### Enhanced Enterprise Features (v2.0)

- **Environment Configuration**: Flexible configuration via `.env` files (optional YAML)
- **Streamlined Codebase**: Removed unused modules for better performance and maintainability
- **Direct Selector Optimization**: Hardcoded selectors for faster element detection
- **Testing Framework**: Unit tests with test fixtures
- **Structured Logging**: Rotating log files with proper error tracking

## 🆕 What's New in v2.0

### Major Features Added

1. **🆕 Batalkan Inputan Feature** - New feature for Sales Summary navigation and customer list display (not available in v1)
2. **🚀 Performance Optimization** - Streamlined codebase with removed unused modules
3. **⚡ Direct Selector Implementation** - Hardcoded selectors for faster element detection

### Enterprise-Grade Improvements

This project has been enhanced with major improvements to achieve enterprise standards:

1. **🌍 Environment Configuration Management**

   - Configuration via environment variables (`.env` file)
   - Optional YAML configuration support for advanced settings
   - Fallback strategy for backward compatibility

2. **🚀 Performance Optimization**

   - Removed unused modules (`error_handler.py`, `exceptions.py`, `security.py`, `selectors.py`)
   - Direct hardcoded selectors for faster element detection
   - Streamlined codebase for better maintainability

3. **🧪 Testing Framework**

   - Unit tests for validator functions
   - Test fixtures and mock objects for reliable testing

4. **📊 Advanced Logging**

   - Structured logging with rotating file handler
   - Comprehensive error tracking and debugging

### Backward Compatibility

All enhancement features are **optional** and do not change existing functionality. The project continues to work with original configuration if enhanced features are not used.

## 🚀 Performance Improvements (v2.0)

### Code Optimization

- **Removed Unused Modules**: Eliminated 4 unused files (`error_handler.py`, `exceptions.py`, `security.py`, `selectors.py`)
- **Direct Selectors**: Replaced dynamic selector classes with hardcoded selectors for faster element detection
- **Streamlined Architecture**: Reduced codebase complexity by ~500+ lines
- **Faster Execution**: Optimized element detection and navigation processes

### Performance Benefits

- **⚡ Faster Startup**: Reduced import time and memory usage
- **🎯 Direct Element Access**: Hardcoded selectors eliminate selector search overhead
- **🧹 Cleaner Codebase**: Easier maintenance and debugging
- **📦 Smaller Footprint**: Reduced file count and complexity

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
