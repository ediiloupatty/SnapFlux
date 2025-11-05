#!/usr/bin/env python3
"""
SnapFlux GUI Launcher v2.0
Launcher script untuk menjalankan SnapFlux Automation dengan GUI
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ["selenium", "pandas", "openpyxl", "pyyaml", "python-dotenv"]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    return missing_packages


def install_dependencies(packages):
    """Install missing dependencies"""
    try:
        for package in packages:
            print(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"Failed to install {package}: {result.stderr}")
                return False
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


def check_required_folders():
    """Check and create required folders"""
    required_folders = ["src", "akun", "results", "logs", "chrome"]

    for folder in required_folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"Created folder: {folder}")
            except Exception as e:
                print(f"Failed to create folder {folder}: {e}")
                return False

    return True


def check_required_files():
    """Check if required files exist"""
    required_files = ["main.py", "gui.py", "gui_integration.py", "requirements.txt"]

    missing_files = []

    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    return missing_files


def show_startup_dialog():
    """Show startup dialog with options"""
    root = tk.Tk()
    root.withdraw()  # Hide main window

    result = messagebox.askyesnocancel(
        "SnapFlux Automation v2.0",
        "Selamat datang di SnapFlux Automation v2.0!\n\n"
        "Pilihan:\n"
        "• YES - Jalankan GUI Mode (Recommended)\n"
        "• NO - Jalankan Console Mode\n"
        "• CANCEL - Keluar\n\n"
        "Apakah Anda ingin menggunakan GUI Mode?",
        icon="question",
    )

    root.destroy()
    return result


def launch_gui():
    """Launch GUI mode"""
    try:
        print("🚀 Starting SnapFlux GUI...")
        from gui import main as gui_main

        gui_main()
    except ImportError as e:
        print(f"❌ Error importing GUI: {e}")
        messagebox.showerror(
            "Import Error",
            f"Tidak dapat import GUI module:\n{e}\n\n"
            "Pastikan semua file ada dan dependencies terinstall.",
        )
        return False
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        messagebox.showerror("Launch Error", f"Error menjalankan GUI:\n{e}")
        return False

    return True


def launch_console():
    """Launch console mode"""
    try:
        print("🚀 Starting SnapFlux Console Mode...")
        import main

        # Run main console application
        main.main()
    except ImportError as e:
        print(f"❌ Error importing main: {e}")
        return False
    except Exception as e:
        print(f"❌ Error launching console: {e}")
        return False

    return True


def show_help():
    """Show help information"""
    help_text = """
═══════════════════════════════════════════
    SnapFlux Automation v2.0 - Launcher
═══════════════════════════════════════════

Usage: python launch_gui.py [options]

Options:
  --gui          Launch GUI mode (default)
  --console      Launch console mode
  --check        Check system requirements
  --install      Install missing dependencies
  --help, -h     Show this help

Examples:
  python launch_gui.py           # Launch with dialog
  python launch_gui.py --gui     # Direct GUI launch
  python launch_gui.py --console # Direct console launch
  python launch_gui.py --check   # Check requirements

Features:
• 🔍 Check Stock - Monitor stock and sales tracking
• ❌ Cancel Input - Transaction cancellation workflow
• 📝 Catat Penjualan - Auto-fill NIK and complete sales process

For more information, visit:
https://github.com/ediiloupatty/SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina

═══════════════════════════════════════════
"""
    print(help_text)


def main():
    """Main launcher function"""
    print("═══════════════════════════════════════════")
    print("    SnapFlux Automation v2.0 - Launcher")
    print("═══════════════════════════════════════════")

    # Parse command line arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if "--help" in args or "-h" in args:
        show_help()
        return

    if "--check" in args:
        print("🔍 Checking system requirements...")

        # Check dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        else:
            print("✅ All dependencies are installed")

        # Check folders
        if check_required_folders():
            print("✅ All required folders are present")
        else:
            print("❌ Some required folders are missing")

        # Check files
        missing_files = check_required_files()
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
        else:
            print("✅ All required files are present")

        return

    if "--install" in args:
        print("📦 Installing missing dependencies...")
        missing_deps = check_dependencies()
        if missing_deps:
            if install_dependencies(missing_deps):
                print("✅ All dependencies installed successfully")
            else:
                print("❌ Failed to install some dependencies")
        else:
            print("✅ All dependencies already installed")
        return

    # Check system requirements
    print("🔍 Checking system requirements...")

    # Check and create folders
    if not check_required_folders():
        print("❌ Failed to create required folders")
        return

    # Check missing files
    missing_files = check_required_files()
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all files are present before running.")
        return

    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"⚠️ Missing dependencies: {', '.join(missing_deps)}")
        choice = input("Install missing dependencies? (y/n): ").lower()
        if choice == "y":
            if not install_dependencies(missing_deps):
                print("❌ Failed to install dependencies. Please install manually:")
                print(f"pip install {' '.join(missing_deps)}")
                return
        else:
            print("⚠️ Some features may not work without required dependencies.")

    # Determine launch mode
    if "--gui" in args:
        launch_gui()
    elif "--console" in args:
        launch_console()
    else:
        # Show dialog for user choice
        try:
            choice = show_startup_dialog()

            if choice is True:  # Yes - GUI
                launch_gui()
            elif choice is False:  # No - Console
                launch_console()
            else:  # Cancel or closed
                print("👋 Goodbye!")

        except Exception as e:
            print(f"❌ Error showing dialog: {e}")
            print("Fallback: Launching console mode...")
            launch_console()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
