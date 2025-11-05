# SnapFlux Automation v2.0 - GUI Interface

GUI (Graphical User Interface) untuk SnapFlux Automation yang menyediakan antarmuka yang user-friendly untuk semua fitur otomatisasi.

## 📋 Tentang GUI

GUI SnapFlux dibuat menggunakan Python Tkinter dan menyediakan antarmuka visual untuk menjalankan semua fitur automation tanpa perlu menggunakan command line. Interface ini dirancang untuk memudahkan pengguna dalam mengelola automation tasks.

## 🚀 Quick Start

### Metode 1: Menggunakan Launcher (Recommended)

```bash
# Double-click file berikut atau jalankan dari command prompt:
SnapFlux_GUI.bat

# Atau jalankan dengan Python:
python launch_gui.py
```

### Metode 2: Direct Launch

```bash
python gui.py
```

## 📸 Interface Overview

### Main Window Components

1. **Control Panel (Kiri)**
   - Manajemen Akun (Load Excel files)
   - Date Selection untuk filtering
   - Tombol fitur utama (Check Stock, Cancel Input, Catat Penjualan)
   - Konfigurasi automation (headless mode, delays, dll)
   - Quick actions (buka folder, stop processes)

2. **Status & Logs Panel (Kanan)**
   - Real-time status indicator
   - Log area dengan timestamps
   - Auto-scroll log viewer
   - Log management (clear, save, auto-scroll toggle)

3. **Progress Panel (Bawah)**
   - Progress indicator dan status
   - Summary statistics (processed, success, failed)
   - Execution time tracking

## 🛠️ Fitur GUI

### Core Features

#### 1. 🔍 Check Stock
- **Fungsi**: Monitoring stok dan tracking penjualan
- **Input**: File akun Excel, tanggal filter (opsional)
- **Output**: Excel file dengan data stok dan penjualan
- **Real-time**: Progress tracking untuk setiap akun

#### 2. ❌ Cancel Input
- **Fungsi**: Navigasi ke Sales Summary dan batalkan transaksi
- **Input**: File akun Excel, tanggal filter
- **Output**: Display customer list di terminal/logs
- **Features**: Date filtering untuk pencarian data spesifik

#### 3. 📝 Catat Penjualan
- **Fungsi**: Auto-fill NIK dan proses penjualan lengkap
- **Input**: File akun Excel, file NIK Excel
- **Process**: Auto-login → Catat Penjualan → Fill NIK → CEK PESANAN → PROSES PENJUALAN
- **Features**: Rotasi NIK otomatis, direct selectors untuk performa optimal

### GUI-Specific Features

#### File Management
- **Load Akun Excel**: Browse dan load file akun merchant
- **Load NIK Excel**: Browse dan load file NIK untuk Catat Penjualan
- **Account Counter**: Display jumlah akun yang loaded

#### Configuration Options
- **Headless Mode**: Toggle browser headless mode on/off
- **Auto Export**: Automatic Excel export setelah selesai
- **Delay Configuration**: Adjustable delay (0.5-10 detik) antar aksi
- **Date Picker**: Easy date selection dengan tombol "Hari Ini"

#### Real-time Monitoring
- **Live Logs**: Timestamps dan level logging (INFO, WARNING, ERROR)
- **Status Indicator**: Visual indicator (●) merah/hijau untuk status
- **Progress Tracking**: Progress bar dan counter untuk automation
- **Statistics**: Real-time update processed/success/failed counts

#### Log Management
- **Auto Scroll**: Otomatis scroll ke log terbaru
- **Clear Logs**: Bersihkan log area
- **Save Logs**: Export logs ke file .txt
- **Log Levels**: Color-coded messages (green=success, red=error, orange=warning)

#### Quick Actions
- **Open Results Folder**: Langsung buka folder results
- **Open Logs Folder**: Langsung buka folder logs  
- **Stop All Processes**: Emergency stop untuk semua automation
- **Menu Bar**: File, Tools, dan Help menu

## 📁 File Structure

```
Snapflux v2.0/
├── gui.py                 # Main GUI application
├── gui_integration.py     # Integration dengan automation functions
├── launch_gui.py          # Launcher script dengan dependency checking
├── SnapFlux_GUI.bat      # Windows batch launcher
├── GUI_README.md         # Documentation ini
├── main.py               # Original console application
└── src/                  # Source modules
    ├── utils.py
    ├── driver_setup.py
    ├── login_handler.py
    └── ...
```

## ⚙️ Configuration

### Environment Variables

GUI menggunakan konfigurasi yang sama dengan console version:

```bash
# .env file
CHROME_BINARY_PATH=D:\path\to\chrome.exe
CHROMEDRIVER_PATH=D:\path\to\chromedriver.exe
LOGIN_URL=https://subsiditepatlpg.mypertamina.id/merchant-login
DEFAULT_DELAY=2.0
HEADLESS_MODE=true
```

### Account Files

- **akun/akun.xlsx**: File akun merchant (Pangkalan, Username, PIN)
- **akun/NIK.xlsx**: File NIK untuk Catat Penjualan (kolom 'NIK')

## 🎯 Usage Guide

### Step-by-step Usage

1. **Launch Application**
   ```bash
   # Double-click SnapFlux_GUI.bat atau:
   python launch_gui.py
   ```

2. **Load Account Data**
   - Click "Load Akun Excel"
   - Pilih file akun.xlsx dari folder akun/
   - Verifikasi account counter shows correct number

3. **Configure Settings**
   - Set headless mode (recommended: ON untuk performa)
   - Adjust delay if needed (default: 2.0 seconds)
   - Select date jika diperlukan filtering

4. **Select Feature**
   - **Check Stock**: Untuk monitoring stok dan penjualan
   - **Cancel Input**: Untuk pembatalan transaksi
   - **Catat Penjualan**: Load NIK file terlebih dahulu

5. **Monitor Progress**
   - Watch real-time logs di panel kanan
   - Monitor progress bar dan statistics
   - Use "Stop Semua" jika perlu menghentikan

6. **Check Results**
   - Results otomatis saved ke folder results/
   - Click "Buka Folder Results" untuk lihat output
   - Save logs jika diperlukan untuk troubleshooting

### Tips & Best Practices

#### Performance Tips
- **Use Headless Mode**: Significantly faster execution
- **Optimal Delay**: 2.0 seconds balance speed vs stability
- **Close Other Apps**: Free up system resources during automation

#### Troubleshooting
- **Check Logs**: Real-time logs show detailed error information
- **Save Logs**: Save logs untuk troubleshooting atau support
- **Stop/Restart**: Use stop button jika automation stuck
- **File Paths**: Pastikan file akun.xlsx dan NIK.xlsx accessible

#### File Management
- **Results Folder**: Automatically organized by date and feature
- **Backup Files**: Keep backup of account files
- **Log Retention**: Regularly save important logs

## 🔧 Advanced Features

### Integration dengan Console Version

GUI berjalan di atas automation functions yang sama dengan console version:
- Fungsi automation di `gui_integration.py`
- Real automation calls ke `main.py` functions
- Backward compatible dengan existing workflow

### Thread Management

- **Main Thread**: GUI interface
- **Worker Threads**: Automation processes 
- **Safe Threading**: Proper cleanup dan error handling
- **Emergency Stop**: Force stop untuk semua threads

### Error Handling

- **Graceful Degradation**: Fallback ke simulation mode jika modules tidak available
- **User-Friendly Messages**: Clear error messages dengan solutions
- **Log Integration**: Semua errors logged dengan timestamps
- **Recovery Options**: Stop/restart tanpa crash

## 🆚 GUI vs Console Comparison

| Feature | GUI Mode | Console Mode |
|---------|----------|--------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Real-time Monitoring** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **File Management** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Progress Tracking** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Error Handling** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Resource Usage** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Automation Scripts** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit)
- **Python**: 3.7+
- **RAM**: 4 GB
- **Display**: 1024x768 resolution
- **Network**: Stable internet connection

### Recommended
- **OS**: Windows 11
- **Python**: 3.9+
- **RAM**: 8+ GB
- **Display**: 1200x800+ resolution
- **Network**: ≥ 10 Mbps stable connection

## 🚨 Troubleshooting

### Common Issues

#### 1. GUI Won't Start
```bash
# Check Python installation
python --version

# Check tkinter availability
python -c "import tkinter; print('Tkinter available')"

# Install missing dependencies
pip install -r requirements.txt
```

#### 2. Module Import Errors
```bash
# Run dependency checker
python launch_gui.py --check

# Install missing modules
python launch_gui.py --install
```

#### 3. Automation Fails
- Check akun.xlsx format dan content
- Verify internet connection
- Check browser compatibility
- Review logs untuk detailed error

#### 4. Performance Issues
- Enable headless mode
- Close unnecessary applications
- Check system resources
- Adjust delay settings

### Error Messages

| Error | Solution |
|-------|----------|
| "Akun belum di-load" | Click "Load Akun Excel" first |
| "Module tidak tersedia" | Run `pip install -r requirements.txt` |
| "Browser error" | Check Chrome/ChromeDriver installation |
| "File tidak ditemukan" | Verify file paths dan permissions |

## 🔄 Updates & Maintenance

### Auto-Update Features
- GUI checks for module availability on startup
- Graceful fallback jika dependencies missing
- Compatible dengan console version updates

### Maintenance Tasks
- Regular log cleanup (manual)
- Results folder organization
- Account file backups
- Dependency updates via pip

## 📞 Support & Feedback

### Getting Help
1. Check logs untuk detailed error information
2. Save dan review log files
3. Check GitHub issues: https://github.com/ediiloupatty/SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina
4. Document steps to reproduce issues

### Reporting Bugs
- Include GUI version dan Python version
- Attach log files jika possible
- Describe expected vs actual behavior
- Include system information (OS, RAM, etc.)

---

**SnapFlux Automation v2.0 GUI** - Enhanced user experience untuk enterprise automation 🚀