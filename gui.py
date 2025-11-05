#!/usr/bin/env python3
"""
GUI Interface untuk SnapFlux Automation v2.0
Antarmuka grafis untuk semua fitur otomatisasi SnapFlux
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
import sys
import json
from datetime import datetime, date
from pathlib import Path
import subprocess
import webbrowser

# Tambahkan path src untuk import modul
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from src.utils import load_accounts_from_excel, setup_logging
    from src.config_manager import config_manager
    from gui_integration import gui_integration

    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


class SnapFluxGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SnapFlux Automation v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Variables
        self.accounts = []
        self.is_running = False
        self.selected_date = None
        self.nik_file_path = None
        self.current_thread = None

        # Style configuration
        self.setup_styles()

        # Create main interface
        self.create_widgets()

        # Load initial data
        self.load_initial_data()

        # Setup GUI integration callbacks
        self.setup_integration_callbacks()

    def setup_styles(self):
        """Setup custom styles untuk GUI"""
        style = ttk.Style()

        # Configure main theme
        style.theme_use("clam")

        # Custom button styles
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Action.TButton", font=("Arial", 10, "bold"))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")
        style.configure("Warning.TLabel", foreground="orange")

    def create_widgets(self):
        """Membuat semua widget GUI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="SnapFlux Automation v2.0", style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Left panel - Controls
        self.create_control_panel(main_frame)

        # Right panel - Logs and Status
        self.create_status_panel(main_frame)

        # Bottom panel - Progress
        self.create_progress_panel(main_frame)

    def create_control_panel(self, parent):
        """Panel kontrol utama"""
        control_frame = ttk.LabelFrame(parent, text="Kontrol Utama", padding="10")
        control_frame.grid(
            row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5)
        )

        # Account Management
        account_frame = ttk.LabelFrame(
            control_frame, text="Manajemen Akun", padding="5"
        )
        account_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            account_frame, text="Load Akun Excel", command=self.load_accounts
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            account_frame, text="Load NIK Excel", command=self.load_nik_file
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.account_count_label = ttk.Label(account_frame, text="Akun: 0")
        self.account_count_label.pack(side=tk.RIGHT)

        # Date Selection
        date_frame = ttk.LabelFrame(control_frame, text="Pilih Tanggal", padding="5")
        date_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(date_frame, text="Tanggal:").pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
        self.date_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(
            date_frame,
            text="Hari Ini",
            command=lambda: self.date_var.set(datetime.now().strftime("%Y-%m-%d")),
        ).pack(side=tk.LEFT)

        # Main Features
        features_frame = ttk.LabelFrame(control_frame, text="Fitur Utama", padding="5")
        features_frame.pack(fill=tk.X, pady=(0, 10))

        # Feature buttons
        self.create_feature_buttons(features_frame)

        # Configuration
        config_frame = ttk.LabelFrame(control_frame, text="Konfigurasi", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_config_options(config_frame)

        # Quick Actions
        actions_frame = ttk.LabelFrame(control_frame, text="Aksi Cepat", padding="5")
        actions_frame.pack(fill=tk.X)

        ttk.Button(
            actions_frame, text="Buka Folder Results", command=self.open_results_folder
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Buka Logs", command=self.open_logs_folder).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(
            actions_frame, text="Stop Semua", command=self.stop_all_processes
        ).pack(side=tk.RIGHT)

    def create_feature_buttons(self, parent):
        """Membuat tombol untuk semua fitur utama"""
        # Check Stock
        stock_frame = ttk.Frame(parent)
        stock_frame.pack(fill=tk.X, pady=2)

        ttk.Button(
            stock_frame,
            text="🔍 Check Stock",
            command=self.run_check_stock,
            style="Action.TButton",
            width=20,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(stock_frame, text="Monitoring stok dan tracking penjualan").pack(
            side=tk.LEFT
        )

        # Cancel Input
        cancel_frame = ttk.Frame(parent)
        cancel_frame.pack(fill=tk.X, pady=2)

        ttk.Button(
            cancel_frame,
            text="❌ Cancel Input",
            command=self.run_cancel_input,
            style="Action.TButton",
            width=20,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(
            cancel_frame, text="Batalkan transaksi dan tampilkan customer list"
        ).pack(side=tk.LEFT)

        # Catat Penjualan
        sales_frame = ttk.Frame(parent)
        sales_frame.pack(fill=tk.X, pady=2)

        ttk.Button(
            sales_frame,
            text="📝 Catat Penjualan",
            command=self.run_catat_penjualan,
            style="Action.TButton",
            width=20,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(sales_frame, text="Auto-fill NIK dan proses penjualan lengkap").pack(
            side=tk.LEFT
        )

    def create_config_options(self, parent):
        """Membuat opsi konfigurasi"""
        # Headless mode
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            parent,
            text="Headless Mode (tanpa tampilan browser)",
            variable=self.headless_var,
        ).pack(anchor=tk.W)

        # Auto export
        self.auto_export_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            parent, text="Auto Export ke Excel", variable=self.auto_export_var
        ).pack(anchor=tk.W)

        # Delay configuration
        delay_frame = ttk.Frame(parent)
        delay_frame.pack(fill=tk.X, pady=2)

        ttk.Label(delay_frame, text="Delay (detik):").pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="2.0")
        delay_spin = ttk.Spinbox(
            delay_frame,
            from_=0.5,
            to=10.0,
            increment=0.5,
            textvariable=self.delay_var,
            width=8,
        )
        delay_spin.pack(side=tk.LEFT, padx=(5, 0))

    def create_status_panel(self, parent):
        """Panel status dan logs"""
        status_frame = ttk.LabelFrame(parent, text="Status & Logs", padding="10")
        status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))

        # Status indicators
        indicators_frame = ttk.Frame(status_frame)
        indicators_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            indicators_frame, text="Status: Siap", style="Success.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)

        self.running_indicator = ttk.Label(
            indicators_frame, text="●", foreground="red", font=("Arial", 20)
        )
        self.running_indicator.pack(side=tk.RIGHT)

        # Logs area
        logs_frame = ttk.Frame(status_frame)
        logs_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(logs_frame, height=20, width=50)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Log controls
        log_controls = ttk.Frame(status_frame)
        log_controls.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(log_controls, text="Clear Logs", command=self.clear_logs).pack(
            side=tk.LEFT
        )
        ttk.Button(log_controls, text="Save Logs", command=self.save_logs).pack(
            side=tk.LEFT, padx=(5, 0)
        )
        ttk.Button(
            log_controls, text="Auto Scroll", command=self.toggle_auto_scroll
        ).pack(side=tk.RIGHT)

        self.auto_scroll = True

    def create_progress_panel(self, parent):
        """Panel progress dan summary"""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="5")
        progress_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Progress bar
        self.progress_var = tk.StringVar(value="Siap untuk memulai...")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))

        # Summary labels
        summary_frame = ttk.Frame(progress_frame)
        summary_frame.pack(fill=tk.X, pady=(5, 0))

        self.summary_labels = {
            "processed": ttk.Label(summary_frame, text="Diproses: 0"),
            "success": ttk.Label(
                summary_frame, text="Berhasil: 0", style="Success.TLabel"
            ),
            "failed": ttk.Label(summary_frame, text="Gagal: 0", style="Error.TLabel"),
            "time": ttk.Label(summary_frame, text="Waktu: 0s"),
        }

        for i, label in enumerate(self.summary_labels.values()):
            label.pack(side=tk.LEFT, padx=(0, 20))

    def load_initial_data(self):
        """Load data awal"""
        self.log_message("SnapFlux GUI v2.0 siap digunakan!")
        self.log_message("Klik 'Load Akun Excel' untuk memulai.")

        # Check if modules are available
        if not MODULES_AVAILABLE:
            self.log_message(
                "⚠️ Warning: Beberapa modul tidak tersedia. Mode simulasi aktif.",
                "warning",
            )
        else:
            self.log_message("✅ Semua modul tersedia. Siap untuk automation!")

    def setup_integration_callbacks(self):
        """Setup callbacks untuk GUI integration"""
        if MODULES_AVAILABLE:
            callbacks = {
                "log_message": self.log_message,
                "update_progress": self.update_progress_callback,
                "update_status": self.update_status_callback,
                "update_summary": self.update_summary,
            }
            gui_integration.set_gui_callbacks(callbacks)

    def update_progress_callback(self, current, total):
        """Callback untuk update progress dari integration"""
        self.progress_var.set(f"Processing {current}/{total}")

    def update_status_callback(self, status):
        """Callback untuk update status dari integration"""
        self.status_label.config(text=f"Status: {status}")
        if "Selesai" in status:
            self.automation_finished()

    def reset_summary(self):
        """Reset summary counters"""
        for key in ["processed", "success", "failed"]:
            self.update_summary(key, 0)

    def load_accounts(self):
        """Load akun dari file Excel"""
        file_path = filedialog.askopenfilename(
            title="Pilih File Akun Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir=os.path.join(os.getcwd(), "akun"),
        )

        if file_path:
            try:
                if MODULES_AVAILABLE:
                    self.accounts = load_accounts_from_excel(file_path)
                    count = len(self.accounts)
                    self.account_count_label.config(text=f"Akun: {count}")
                    self.log_message(
                        f"✅ Berhasil load {count} akun dari {os.path.basename(file_path)}"
                    )
                else:
                    self.log_message(
                        "❌ Tidak dapat load akun: modul tidak tersedia", "error"
                    )
            except Exception as e:
                self.log_message(f"❌ Error load akun: {str(e)}", "error")

    def load_nik_file(self):
        """Load file NIK untuk Catat Penjualan"""
        file_path = filedialog.askopenfilename(
            title="Pilih File NIK Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir=os.path.join(os.getcwd(), "akun"),
        )

        if file_path:
            self.nik_file_path = file_path
            self.log_message(f"✅ File NIK dipilih: {os.path.basename(file_path)}")

    def run_check_stock(self):
        """Jalankan fitur Check Stock"""
        if not self.validate_before_run():
            return

        self.log_message("🔍 Memulai Check Stock...")
        self.start_automation("check_stock")

    def run_cancel_input(self):
        """Jalankan fitur Cancel Input"""
        if not self.validate_before_run():
            return

        self.log_message("❌ Memulai Cancel Input...")
        self.start_automation("cancel_input")

    def run_catat_penjualan(self):
        """Jalankan fitur Catat Penjualan"""
        if not self.validate_before_run():
            return

        self.log_message("📝 Memulai Catat Penjualan...")
        self.start_automation("catat_penjualan")

    def validate_before_run(self):
        """Validasi sebelum menjalankan automation"""
        if self.is_running:
            messagebox.showwarning("Peringatan", "Automation sedang berjalan!")
            return False

        if not self.accounts:
            messagebox.showerror("Error", "Silakan load akun terlebih dahulu!")
            return False

        return True

    def start_automation(self, feature_type):
        """Mulai proses automation di thread terpisah"""
        self.is_running = True
        self.update_running_status(True)
        self.progress_bar.start(10)
        self.reset_summary()

        # Dapatkan konfigurasi
        config = {
            "selected_date": self.date_var.get() if self.date_var.get() else None,
            "headless": self.headless_var.get(),
            "delay": float(self.delay_var.get()),
            "nik_file": self.nik_file_path,
        }

        # Jalankan menggunakan GUI integration
        if MODULES_AVAILABLE:
            self.current_thread = gui_integration.run_automation(
                feature_type, self.accounts, config
            )
            self.current_thread.start()
        else:
            # Fallback to simulation
            thread = threading.Thread(
                target=self.automation_worker,
                args=(feature_type, config["selected_date"]),
            )
            thread.daemon = True
            thread.start()

    def automation_worker(self, feature_type, selected_date):
        """Worker thread untuk menjalankan automation"""
        try:
            self.progress_var.set(f"Memulai {feature_type}...")

            # Simulate automation process
            if feature_type == "check_stock":
                self.simulate_check_stock()
            elif feature_type == "cancel_input":
                self.simulate_cancel_input()
            elif feature_type == "catat_penjualan":
                self.simulate_catat_penjualan()

            self.log_message(f"✅ {feature_type} selesai!")

        except Exception as e:
            self.log_message(f"❌ Error dalam {feature_type}: {str(e)}", "error")
        finally:
            self.root.after(0, self.automation_finished)

    def simulate_check_stock(self):
        """Simulasi proses Check Stock"""
        total_accounts = len(self.accounts)

        for i, account in enumerate(self.accounts):
            if not self.is_running:
                break

            account_name = account.get("Pangkalan", f"Akun {i + 1}")
            self.log_message(f"Processing {account_name}...")
            self.progress_var.set(
                f"Processing {account_name} ({i + 1}/{total_accounts})"
            )

            # Simulate work
            import time

            time.sleep(2)

            # Update summary
            self.update_summary("processed", i + 1)
            self.update_summary("success", i + 1)

    def simulate_cancel_input(self):
        """Simulasi proses Cancel Input"""
        total_accounts = len(self.accounts)

        for i, account in enumerate(self.accounts):
            if not self.is_running:
                break

            account_name = account.get("Pangkalan", f"Akun {i + 1}")
            self.log_message(f"Navigating to Sales Summary for {account_name}...")
            self.progress_var.set(
                f"Processing {account_name} ({i + 1}/{total_accounts})"
            )

            # Simulate work
            import time

            time.sleep(1.5)

            # Update summary
            self.update_summary("processed", i + 1)
            self.update_summary("success", i + 1)

    def simulate_catat_penjualan(self):
        """Simulasi proses Catat Penjualan"""
        total_accounts = len(self.accounts)

        for i, account in enumerate(self.accounts):
            if not self.is_running:
                break

            account_name = account.get("Pangkalan", f"Akun {i + 1}")
            self.log_message(f"Auto-filling NIK for {account_name}...")
            self.progress_var.set(
                f"Processing {account_name} ({i + 1}/{total_accounts})"
            )

            # Simulate work
            import time

            time.sleep(2.5)

            # Update summary
            self.update_summary("processed", i + 1)
            self.update_summary("success", i + 1)

    def automation_finished(self):
        """Cleanup setelah automation selesai"""
        self.is_running = False
        self.update_running_status(False)
        self.progress_bar.stop()
        self.progress_var.set("Selesai!")

    def update_running_status(self, is_running):
        """Update indikator status running"""
        if is_running:
            self.running_indicator.config(foreground="green")
            self.status_label.config(text="Status: Berjalan", style="Warning.TLabel")
        else:
            self.running_indicator.config(foreground="red")
            self.status_label.config(text="Status: Siap", style="Success.TLabel")

    def update_summary(self, key, value):
        """Update summary labels"""
        if key in self.summary_labels:
            texts = {
                "processed": f"Diproses: {value}",
                "success": f"Berhasil: {value}",
                "failed": f"Gagal: {value}",
                "time": f"Waktu: {value}s",
            }
            self.summary_labels[key].config(text=texts[key])

    def log_message(self, message, level="info"):
        """Tambahkan pesan ke log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if level == "error":
            formatted_message = f"[{timestamp}] ERROR: {message}\n"
        elif level == "warning":
            formatted_message = f"[{timestamp}] WARNING: {message}\n"
        else:
            formatted_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, formatted_message)

        if self.auto_scroll:
            self.log_text.see(tk.END)

    def clear_logs(self):
        """Bersihkan area log"""
        self.log_text.delete(1.0, tk.END)

    def save_logs(self):
        """Simpan log ke file"""
        content = self.log_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("Info", "Tidak ada log untuk disimpan.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Simpan Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Sukses", f"Log disimpan ke {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan log: {str(e)}")

    def toggle_auto_scroll(self):
        """Toggle auto scroll untuk log area"""
        self.auto_scroll = not self.auto_scroll
        status = "ON" if self.auto_scroll else "OFF"
        self.log_message(f"Auto scroll: {status}")

    def open_results_folder(self):
        """Buka folder results"""
        results_path = os.path.join(os.getcwd(), "results")
        if os.path.exists(results_path):
            if sys.platform.startswith("win"):
                os.startfile(results_path)
            else:
                subprocess.run(
                    ["open" if sys.platform == "darwin" else "xdg-open", results_path]
                )
        else:
            messagebox.showinfo("Info", "Folder results belum ada.")

    def open_logs_folder(self):
        """Buka folder logs"""
        logs_path = os.path.join(os.getcwd(), "logs")
        if os.path.exists(logs_path):
            if sys.platform.startswith("win"):
                os.startfile(logs_path)
            else:
                subprocess.run(
                    ["open" if sys.platform == "darwin" else "xdg-open", logs_path]
                )
        else:
            messagebox.showinfo("Info", "Folder logs belum ada.")

    def stop_all_processes(self):
        """Stop semua proses yang sedang berjalan"""
        if self.is_running:
            result = messagebox.askyesno(
                "Konfirmasi", "Yakin ingin menghentikan semua proses?"
            )
            if result:
                self.is_running = False
                # Stop automation melalui integration
                if MODULES_AVAILABLE:
                    gui_integration.stop_automation()
                self.log_message("🛑 Proses dihentikan oleh user")
                self.automation_finished()
        else:
            messagebox.showinfo("Info", "Tidak ada proses yang sedang berjalan.")

    def run(self):
        """Jalankan GUI"""
        self.root.mainloop()


class AboutDialog:
    """Dialog About untuk informasi aplikasi"""

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Tentang SnapFlux Automation")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)

        # Center the dialog
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_about_content()

    def create_about_content(self):
        """Buat konten dialog about"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(
            main_frame, text="SnapFlux Automation v2.0", font=("Arial", 16, "bold")
        )
        title.pack(pady=(0, 10))

        # Description
        desc_text = """
Automated web scraping and data extraction tool
for SnapFlux merchant platform using Selenium WebDriver
with enterprise-grade features and optimized performance.

🚀 Fitur Utama:
• Check Stock - Monitoring stok dan tracking penjualan
• Cancel Input - Batalkan transaksi dan customer list
• Catat Penjualan - Auto-fill NIK dan proses lengkap

⚡ Enhanced Features v2.0:
• GUI Interface yang user-friendly
• Environment Configuration Management
• Performance Optimization dengan direct selectors
• Advanced Logging dan Error Handling
• Testing Framework untuk reliability

💻 Tech Stack:
• Python 3.7+ dengan Selenium WebDriver
• Chrome/Chromium untuk automation
• Excel export dengan pandas + openpyxl
• Tkinter untuk GUI interface
        """

        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(
            buttons_frame, text="GitHub Repository", command=self.open_github
        ).pack(side=tk.LEFT)
        ttk.Button(buttons_frame, text="Tutup", command=self.dialog.destroy).pack(
            side=tk.RIGHT
        )

    def open_github(self):
        """Buka GitHub repository"""
        url = "https://github.com/ediiloupatty/SnapFlux-Scraping-App-For-Merchant-Apps-Pertamina"
        webbrowser.open(url)


def create_menu_bar(root, gui_instance):
    """Buat menu bar untuk aplikasi"""
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load Akun Excel", command=gui_instance.load_accounts)
    file_menu.add_command(label="Load NIK Excel", command=gui_instance.load_nik_file)
    file_menu.add_separator()
    file_menu.add_command(label="Keluar", command=root.quit)

    # Tools menu
    tools_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(
        label="Buka Results", command=gui_instance.open_results_folder
    )
    tools_menu.add_command(label="Buka Logs", command=gui_instance.open_logs_folder)
    tools_menu.add_separator()
    tools_menu.add_command(label="Clear Logs", command=gui_instance.clear_logs)
    tools_menu.add_command(label="Save Logs", command=gui_instance.save_logs)

    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Tentang", command=lambda: AboutDialog(root))


def main():
    """Fungsi utama untuk menjalankan GUI"""
    try:
        # Buat instance GUI
        app = SnapFluxGUI()

        # Tambahkan menu bar
        create_menu_bar(app.root, app)

        # Jalankan aplikasi
        app.run()

    except Exception as e:
        messagebox.showerror("Error", f"Gagal menjalankan aplikasi: {str(e)}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
