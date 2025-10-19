# SnapFlux Automation v2

Automation script untuk mengambil data transaksi dari platform Snapflux menggunakan Selenium WebDriver.

## 📋 Description

SnapFlux adalah aplikasi untuk automated web scraping dan data extraction dari portal [subsiditepatlpg.mypertamina.id](https://subsiditepatlpg.mypertamina.id).  
Aplikasi ini mengotomatisasi login, navigasi, dan pengambilan laporan menggunakan Selenium WebDriver.

## 🚀 Key Features

- **Automated Login & Navigation** - Login otomatis ke portal merchant
- **Data Extraction** - Ekstraksi data penjualan dengan status dan timestamp  
- **Stock Monitoring** - Automatic stock data retrieval jika data penjualan tidak ada
- **Excel Export** - Export hasil ke format Excel dengan struktur yang rapi
- **Headless Mode** - Mode tanpa GUI untuk performa optimal
- **Batch Processing** - Support multiple akun dalam satu run

## 🛠️ Technical Stack

- **Language**: Python 3.7+
- **Framework**: Selenium WebDriver
- **Browser**: Chrome/Chromium (bundled)
- **Data Export**: pandas + openpyxl
- **Platform**: Cross-platform (Windows/Linux/macOS)

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/ediiloupatty/SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina.git
cd SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Setup configuration
cp config.yaml.example config.yaml

# Setup account data (edit with your credentials)
cp akun/akun.xlsx.example akun/akun.xlsx
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
│   └── driver_setup.py     # WebDriver configuration
├── akun/                   # Account data (see .gitignore)
│   └── akun.xlsx.example   # Account template
├── results/                # Output Excel files (see .gitignore)
├── logs/                   # Automation logs (see .gitignore)
├── config.yaml.example     # Configuration template
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## ⚙️ Configuration

Edit `config.yaml` untuk mengatur:
- Login URL dan retry settings
- Delay dan timeout configurations
- Log file settings

Edit `akun/akun.xlsx` dengan:
- Nama pangkalan
- Username (email/phone)
- PIN credentials

## 💻 System Requirements

### Minimum
- **OS**: Windows 10 (64-bit) / Linux / macOS
- **Python**: 3.7+
- **RAM**: 4 GB
- **Storage**: 1–2 GB free space
- **Network**: ≥ 5 Mbps stable connection

### Recommended
- **OS**: Windows 11 / Latest Linux / macOS  
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
pip install selenium pandas requests openpyxl
```

### Key Components
- **Selenium WebDriver** - Browser automation
- **pandas** - Data processing and Excel export
- **requests** - HTTP client for API calls
- **openpyxl** - Excel file operations

## 📊 Features in Detail

- **Multi-Account Support**: Process multiple merchant accounts
- **Date Filtering**: Filter reports by specific date ranges
- **Error Handling**: Robust error handling with retry mechanism
- **Progress Tracking**: Real-time progress monitoring
- **Export Options**: Multiple export formats (Excel)

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