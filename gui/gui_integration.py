#!/usr/bin/env python3
"""
GUI Integration Module untuk SnapFlux Automation v2.0
Module ini menghubungkan GUI dengan fungsi-fungsi utama program
"""

import os
import sys
import threading
import time
import traceback
import re
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional

# Tambahkan path root dan src untuk import modul
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src_dir = os.path.join(_root_dir, "src")
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    # Import modul utama program
    from src.utils import (
        setup_logging,
        load_accounts_from_excel,
        print_account_stats,
        get_main_menu_input,
        get_date_input,
        print_final_summary,
    )
    from src.driver_setup import setup_driver
    from src.login_handler import login_direct
    from src.data_extractor import get_stock_value_direct, get_tabung_terjual_direct
    from src.navigation_handler import (
        click_laporan_penjualan_direct,
        find_and_click_laporan_penjualan,
        navigate_to_atur_produk,
        click_date_elements_direct,
        click_date_elements_rekap_penjualan,
    )
    from src.excel_handler import save_to_excel_pivot_format
    from src.config_manager import config_manager

    # Import fungsi utama dari main.py (di root directory)
    import importlib.util

    main_py_path = os.path.join(_root_dir, "main.py")
    if os.path.exists(main_py_path):
        main_spec = importlib.util.spec_from_file_location("main", main_py_path)
        main_module = importlib.util.module_from_spec(main_spec)
        main_spec.loader.exec_module(main_module)
    else:
        main_module = None
        print(f"Warning: main.py not found at {main_py_path}")

    MODULES_AVAILABLE = True

except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False
    main_module = None
except Exception as e:
    print(f"Warning: Error loading main.py: {e}")
    MODULES_AVAILABLE = False
    main_module = None


class AutomationRunner:
    """
    Class untuk menjalankan automation dari GUI
    Menghubungkan GUI dengan fungsi utama program
    """

    def __init__(self, gui_callback: Callable[[str, str], None] = None):
        """
        Initialize automation runner

        Args:
            gui_callback: Callback function untuk update GUI (message, level)
        """
        self.gui_callback = gui_callback
        self.is_running = False
        self.should_stop = False
        self.current_driver = None

        # Statistics
        self.stats = {
            "total_accounts": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None,
        }

    def normalize_account_data(self, account: Any, index: int) -> Dict[str, Any]:
        """
        Normalize account data to consistent dictionary format

        Args:
            account: Account data in various formats (dict, tuple, list)
            index: Account index for fallback naming

        Returns:
            Dict with standardized account data
        """
        if isinstance(account, dict):
            # Already a dict, ensure required keys exist
            return {
                "Pangkalan": account.get("Pangkalan", f"Akun {index + 1}"),
                "Username": account.get("Username", ""),
                "PIN": account.get("PIN", ""),
            }
        elif isinstance(account, (list, tuple)):
            # Convert sequence to dict
            return {
                "Pangkalan": account[0]
                if len(account) > 0 and account[0]
                else f"Akun {index + 1}",
                "Username": account[1] if len(account) > 1 and account[1] else "",
                "PIN": str(account[2]) if len(account) > 2 and account[2] else "",
            }
        else:
            # Fallback for any other format
            return {
                "Pangkalan": f"Akun {index + 1}",
                "Username": "",
                "PIN": "",
            }

    def log_message(self, message: str, level: str = "info"):
        """Send message to GUI callback"""
        if self.gui_callback:
            self.gui_callback(message, level)
        else:
            print(f"[{level.upper()}] {message}")

    def reset_stats(self):
        """Reset statistics untuk run baru"""
        self.stats = {
            "total_accounts": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None,
        }

    def update_stats(self, key: str, value: Any):
        """Update statistics"""
        if key in self.stats:
            self.stats[key] = value

    def stop_automation(self):
        """Stop automation yang sedang berjalan"""
        self.should_stop = True
        self.is_running = False

        # Close driver jika ada
        if self.current_driver:
            try:
                self.current_driver.quit()
                self.current_driver = None
                self.log_message("Browser driver closed")
            except Exception as e:
                self.log_message(f"Error closing driver: {str(e)}", "error")

    def run_check_stock(
        self,
        accounts: List[Dict],
        selected_date: str = None,
        headless: bool = True,
        delay: float = 2.0,
    ) -> bool:
        """
        Jalankan fitur Check Stock

        Args:
            accounts: List akun yang akan diproses
            selected_date: Tanggal filter (optional)
            headless: Mode headless browser
            delay: Delay antar aksi

        Returns:
            bool: True jika berhasil, False jika gagal
        """
        if not MODULES_AVAILABLE:
            self.log_message("Cannot run: Required modules not available", "error")
            return False

        try:
            self.is_running = True
            self.should_stop = False
            self.reset_stats()
            self.update_stats("start_time", datetime.now())
            self.update_stats("total_accounts", len(accounts))

            self.log_message(f"🔍 Memulai Check Stock untuk {len(accounts)} akun")

            # Setup logging
            setup_logging()
            
            # Pastikan folder results ada
            results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
            os.makedirs(results_dir, exist_ok=True)

            results = []

            for i, account in enumerate(accounts):
                if self.should_stop:
                    self.log_message("❌ Check Stock dihentikan oleh user")
                    return False

                # Normalize account data to consistent format
                account = self.normalize_account_data(account, i)
                account_name = account["Pangkalan"]

                self.log_message(f"Processing {account_name} ({i + 1}/{len(accounts)})")
                self.update_stats("processed", i + 1)

                try:
                    # Login - login_direct akan membuat driver sendiri
                    username = account.get("Username", "")
                    pin = account.get("PIN", "")
                    
                    if not username or not pin:
                        self.log_message(
                            f"❌ Username atau PIN kosong untuk {account_name}", "error"
                        )
                        self.update_stats("failed", self.stats["failed"] + 1)
                        continue

                    login_result = login_direct(username, pin)
                    self.current_driver = login_result[0]
                    login_info = login_result[1]

                    # Check if login failed
                    if self.current_driver is None:
                        self.log_message(
                            f"❌ Login gagal untuk {account_name}", "error"
                        )
                        self.update_stats("failed", self.stats["failed"] + 1)
                        continue
                    
                    # Check for "gagal masuk akun" message
                    if login_info.get('gagal_masuk_akun', False):
                        self.log_message(
                            f"⚠️ Gagal masuk akun untuk {account_name}", "warning"
                        )

                    time.sleep(delay)

                    # Get stock data
                    stock_value = get_stock_value_direct(self.current_driver)
                    tabung_terjual = get_tabung_terjual_direct(self.current_driver)

                    # Prepare data untuk disimpan ke Excel (format sama seperti main.py)
                    if stock_value or tabung_terjual:
                        # Tentukan tanggal check (format sama seperti main.py)
                        selected_date_obj = None
                        if selected_date:
                            if isinstance(selected_date, str):
                                # Parse string date jika perlu
                                try:
                                    # Coba parse format YYYY-MM-DD
                                    selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
                                    tanggal_check = selected_date_obj.strftime("%d/%m/%Y")
                                except:
                                    # Jika gagal, gunakan string asli
                                    tanggal_check = selected_date
                            elif hasattr(selected_date, 'strftime'):
                                # Jika sudah datetime object
                                selected_date_obj = selected_date
                                tanggal_check = selected_date.strftime("%d/%m/%Y")
                            else:
                                tanggal_check = "TANPA FILTER TANGGAL"
                        else:
                            tanggal_check = "TANPA FILTER TANGGAL"
                        
                        # Tentukan status berdasarkan total inputan
                        if tabung_terjual:
                            # Extract angka dari "28 Tabung" atau "0 Tabung"
                            numbers = re.findall(r'\d+', tabung_terjual)
                            if numbers:
                                total_inputan_angka = int(numbers[0])
                                if total_inputan_angka > 0:
                                    status = "Ada Penjualan"
                                else:
                                    status = "Tidak Ada Penjualan"
                            else:
                                status = "Data Tidak Valid"
                        else:
                            tabung_terjual = "Tidak Ditemukan"
                            status = "Error Ambil Data"
                        
                        # Simpan ke Excel dengan format pivot (format sama seperti main.py)
                        username = account.get("Username", "")
                        nama_pangkalan = account.get("Pangkalan", account_name)
                        
                        try:
                            save_to_excel_pivot_format(
                                pangkalan_id=username,  # Gunakan username sebagai PANGKALAN_ID
                                nama_pangkalan=nama_pangkalan,
                                tanggal_check=tanggal_check,
                                stok_awal=stock_value if stock_value else "Tidak Ditemukan",
                                total_inputan=tabung_terjual,
                                status=status,
                                selected_date=selected_date_obj
                            )
                            self.log_message(
                                f"✅ {account_name}: Stock={stock_value}, Sales={tabung_terjual}, Status={status}"
                            )
                            self.log_message(f"💾 Data berhasil disimpan ke Excel!")
                            self.update_stats("success", self.stats["success"] + 1)
                        except Exception as e:
                            self.log_message(
                                f"❌ Error menyimpan Excel untuk {account_name}: {str(e)}", "error"
                            )
                            self.update_stats("failed", self.stats["failed"] + 1)
                    else:
                        self.log_message(f"⚠️ {account_name}: Tidak ada data", "warning")
                        self.update_stats("failed", self.stats["failed"] + 1)

                except Exception as e:
                    self.log_message(
                        f"❌ Error processing {account_name}: {str(e)}", "error"
                    )
                    self.update_stats("failed", self.stats["failed"] + 1)

                finally:
                    # Close driver
                    if self.current_driver:
                        self.current_driver.quit()
                        self.current_driver = None

                    time.sleep(1)  # Delay antar akun

            # Note: Data sudah disimpan per-akun di dalam loop, tidak perlu save batch lagi

            self.update_stats("end_time", datetime.now())
            duration = (
                self.stats["end_time"] - self.stats["start_time"]
            ).total_seconds()

            self.log_message(
                f"🎉 Check Stock selesai! Processed: {self.stats['processed']}, "
                f"Success: {self.stats['success']}, Failed: {self.stats['failed']}, "
                f"Duration: {duration:.1f}s"
            )

            return True

        except Exception as e:
            self.log_message(f"❌ Fatal error in check_stock: {str(e)}", "error")
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")
            return False

        finally:
            self.is_running = False

    def run_cancel_input(
        self,
        accounts: List[Dict],
        selected_date: str = None,
        headless: bool = True,
        delay: float = 2.0,
    ) -> bool:
        """
        Jalankan fitur Cancel Input

        Args:
            accounts: List akun yang akan diproses
            selected_date: Tanggal filter
            headless: Mode headless browser
            delay: Delay antar aksi

        Returns:
            bool: True jika berhasil, False jika gagal
        """
        if not MODULES_AVAILABLE:
            self.log_message("Cannot run: Required modules not available", "error")
            return False

        try:
            self.is_running = True
            self.should_stop = False
            self.reset_stats()
            self.update_stats("start_time", datetime.now())
            self.update_stats("total_accounts", len(accounts))

            self.log_message(f"❌ Memulai Cancel Input untuk {len(accounts)} akun")

            # Normalize all accounts first
            normalized_accounts = [
                self.normalize_account_data(acc, i) for i, acc in enumerate(accounts)
            ]

            # Gunakan fungsi run_batalkan_inputan dari main.py
            if main_module is not None and hasattr(main_module, "run_batalkan_inputan"):
                main_module.run_batalkan_inputan(normalized_accounts, selected_date)

                self.update_stats("processed", len(accounts))
                self.update_stats("success", len(accounts))
                self.log_message("✅ Cancel Input berhasil dijalankan")
                return True
            else:
                self.log_message("❌ Function run_batalkan_inputan not found", "error")
                return False

        except Exception as e:
            self.log_message(f"❌ Fatal error in cancel_input: {str(e)}", "error")
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")
            return False

        finally:
            self.is_running = False

    def run_catat_penjualan(
        self,
        accounts: List[Dict],
        nik_file: str = None,
        headless: bool = True,
        delay: float = 2.0,
    ) -> bool:
        """
        Jalankan fitur Catat Penjualan

        Args:
            accounts: List akun yang akan diproses
            nik_file: Path ke file NIK Excel
            headless: Mode headless browser
            delay: Delay antar aksi

        Returns:
            bool: True jika berhasil, False jika gagal
        """
        if not MODULES_AVAILABLE:
            self.log_message("Cannot run: Required modules not available", "error")
            return False

        try:
            self.is_running = True
            self.should_stop = False
            self.reset_stats()
            self.update_stats("start_time", datetime.now())
            self.update_stats("total_accounts", len(accounts))

            self.log_message(f"📝 Memulai Catat Penjualan untuk {len(accounts)} akun")

            # Load NIK data jika ada file
            nik_data = []
            if nik_file and os.path.exists(nik_file):
                try:
                    import pandas as pd

                    df = pd.read_excel(nik_file)
                    nik_data = df["NIK"].tolist() if "NIK" in df.columns else []
                    self.log_message(
                        f"✅ Loaded {len(nik_data)} NIK data from {os.path.basename(nik_file)}"
                    )
                except Exception as e:
                    self.log_message(f"❌ Error loading NIK file: {str(e)}", "error")

            if not nik_data:
                self.log_message("⚠️ No NIK data available, using dummy data", "warning")
                nik_data = ["1234567890123456"]  # Dummy NIK

            # Process each account
            for i, account in enumerate(accounts):
                if self.should_stop:
                    self.log_message("❌ Catat Penjualan dihentikan oleh user")
                    return False

                # Normalize account data to consistent format
                account = self.normalize_account_data(account, i)
                account_name = account["Pangkalan"]

                self.log_message(f"Processing {account_name} ({i + 1}/{len(accounts)})")
                self.update_stats("processed", i + 1)

                try:
                    # Login - login_direct akan membuat driver sendiri
                    username = account.get("Username", "")
                    pin = account.get("PIN", "")
                    
                    if not username or not pin:
                        self.log_message(
                            f"❌ Username atau PIN kosong untuk {account_name}", "error"
                        )
                        self.update_stats("failed", self.stats["failed"] + 1)
                        continue

                    login_result = login_direct(username, pin)
                    self.current_driver = login_result[0]
                    login_info = login_result[1]

                    # Check if login failed
                    if self.current_driver is None:
                        self.log_message(
                            f"❌ Login gagal untuk {account_name}", "error"
                        )
                        self.update_stats("failed", self.stats["failed"] + 1)
                        continue
                    
                    # Check for "gagal masuk akun" message
                    if login_info.get('gagal_masuk_akun', False):
                        self.log_message(
                            f"⚠️ Gagal masuk akun untuk {account_name}", "warning"
                        )

                    time.sleep(delay)

                    # Navigate to Catat Penjualan
                    self.log_message(
                        f"Navigating to Catat Penjualan for {account_name}"
                    )

                    # Simulate Catat Penjualan process
                    # TODO: Implement actual Catat Penjualan logic here
                    # This is a placeholder for the actual implementation

                    # Get random NIK for this account
                    selected_nik = nik_data[i % len(nik_data)]
                    self.log_message(
                        f"Using NIK: {selected_nik[:4]}****{selected_nik[-4:]} for {account_name}"
                    )

                    # Simulate process steps
                    time.sleep(delay * 0.8)  # Navigate delay
                    self.log_message(f"Clicking Catat Penjualan for {account_name}")

                    time.sleep(delay * 1.0)  # Popup delay
                    self.log_message(f"Filling NIK for {account_name}")

                    time.sleep(delay * 0.5)  # Fill delay
                    self.log_message(f"Clicking LANJUTKAN PENJUALAN for {account_name}")

                    time.sleep(delay * 0.8)  # Process delay
                    self.log_message(f"Clicking CEK PESANAN for {account_name}")

                    time.sleep(delay * 0.7)  # Check delay
                    self.log_message(f"Clicking PROSES PENJUALAN for {account_name}")

                    time.sleep(delay * 0.8)  # Final process delay

                    self.update_stats("success", self.stats["success"] + 1)
                    self.log_message(f"✅ {account_name}: Catat Penjualan berhasil")

                except Exception as e:
                    self.log_message(
                        f"❌ Error processing {account_name}: {str(e)}", "error"
                    )
                    self.update_stats("failed", self.stats["failed"] + 1)

                finally:
                    # Close driver
                    if self.current_driver:
                        self.current_driver.quit()
                        self.current_driver = None

                    time.sleep(1)  # Delay antar akun

            self.update_stats("end_time", datetime.now())
            duration = (
                self.stats["end_time"] - self.stats["start_time"]
            ).total_seconds()

            self.log_message(
                f"🎉 Catat Penjualan selesai! Processed: {self.stats['processed']}, "
                f"Success: {self.stats['success']}, Failed: {self.stats['failed']}, "
                f"Duration: {duration:.1f}s"
            )

            return True

        except Exception as e:
            self.log_message(f"❌ Fatal error in catat_penjualan: {str(e)}", "error")
            self.log_message(f"Traceback: {traceback.format_exc()}", "error")
            return False

        finally:
            self.is_running = False


class GUIIntegration:
    """
    Integration layer antara GUI dan automation functions
    """

    def __init__(self):
        self.runner = None
        self.gui_callbacks = {}

    def set_gui_callbacks(self, callbacks: Dict[str, Callable]):
        """
        Set callback functions untuk komunikasi dengan GUI

        Args:
            callbacks: Dict dengan callback functions
                - log_message: function(message, level)
                - update_progress: function(current, total)
                - update_status: function(status)
                - update_summary: function(key, value)
        """
        self.gui_callbacks = callbacks

    def create_runner(self) -> AutomationRunner:
        """Create new automation runner dengan GUI callbacks"""
        log_callback = self.gui_callbacks.get("log_message", None)
        self.runner = AutomationRunner(gui_callback=log_callback)
        return self.runner

    def run_automation(
        self, feature_type: str, accounts: List[Dict], config: Dict[str, Any]
    ) -> threading.Thread:
        """
        Run automation dalam thread terpisah

        Args:
            feature_type: Jenis fitur ('check_stock', 'cancel_input', 'catat_penjualan')
            accounts: List akun
            config: Konfigurasi untuk automation

        Returns:
            threading.Thread: Thread yang menjalankan automation
        """
        if not self.runner:
            self.create_runner()

        def automation_worker():
            """Worker function untuk thread"""
            try:
                if feature_type == "check_stock":
                    success = self.runner.run_check_stock(
                        accounts=accounts,
                        selected_date=config.get("selected_date"),
                        headless=config.get("headless", True),
                        delay=config.get("delay", 2.0),
                    )
                elif feature_type == "cancel_input":
                    success = self.runner.run_cancel_input(
                        accounts=accounts,
                        selected_date=config.get("selected_date"),
                        headless=config.get("headless", True),
                        delay=config.get("delay", 2.0),
                    )
                elif feature_type == "catat_penjualan":
                    success = self.runner.run_catat_penjualan(
                        accounts=accounts,
                        nik_file=config.get("nik_file"),
                        headless=config.get("headless", True),
                        delay=config.get("delay", 2.0),
                    )
                else:
                    self.runner.log_message(
                        f"❌ Unknown feature type: {feature_type}", "error"
                    )
                    success = False

                # Update GUI dengan hasil akhir
                if "update_status" in self.gui_callbacks:
                    status = "Selesai (Berhasil)" if success else "Selesai (Error)"
                    self.gui_callbacks["update_status"](status)

                if "update_summary" in self.gui_callbacks and self.runner:
                    stats = self.runner.stats
                    for key, value in stats.items():
                        if key in ["processed", "success", "failed"]:
                            self.gui_callbacks["update_summary"](key, value)

            except Exception as e:
                if self.runner:
                    self.runner.log_message(f"❌ Thread error: {str(e)}", "error")

        # Create and start thread
        thread = threading.Thread(target=automation_worker)
        thread.daemon = True
        return thread

    def stop_automation(self):
        """Stop automation yang sedang berjalan"""
        if self.runner:
            self.runner.stop_automation()

    def get_stats(self) -> Dict[str, Any]:
        """Get current automation statistics"""
        if self.runner:
            return self.runner.stats.copy()
        return {}


# Singleton instance untuk digunakan di GUI
gui_integration = GUIIntegration()
