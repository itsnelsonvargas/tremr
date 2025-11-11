"""
Tremr - GUI Application
Minimalist interface for earthquake monitoring
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
import sys
import winreg
from geopy.geocoders import Nominatim
from main import EarthquakeMonitor
import logging
from PIL import Image, ImageTk
import pystray
import tempfile

class EarthquakeMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tremr")
        self.root.geometry("500x750")
        self.root.resizable(False, False)

        # Set icon if available
        self.icon_path = None
        try:
            if os.path.exists('earthquake_warning.ico'):
                self.icon_path = 'earthquake_warning.ico'
                # For Windows, use .ico directly
                self.root.iconbitmap(self.icon_path)
            elif os.path.exists('earthquake_warning.png'):
                icon = tk.PhotoImage(file='earthquake_warning.png')
                self.root.iconphoto(True, icon)
        except:
            pass

        # Load logo for display
        self.logo_image = None
        try:
            if os.path.exists('tremr_logo.png'):
                logo_pil = Image.open('tremr_logo.png')
                # Resize logo to fit nicely in UI (150x150 pixels)
                logo_pil = logo_pil.resize((150, 150), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(logo_pil)
        except Exception as e:
            logging.error(f"Error loading logo: {e}")

        # Variables
        self.monitor = None
        self.monitor_thread = None
        self.is_monitoring = False
        self.config_file = 'config.json'
        self.config = self.load_config()

        # System tray variables
        self.tray_icon = None
        self.is_minimized_to_tray = False

        # Connection status variables
        self.connection_check_interval = 30000  # Check every 30 seconds
        self.last_connection_status = None

        # Initialize geocoder
        self.geolocator = Nominatim(user_agent="tremr")

        # Setup GUI
        self.setup_ui()
        self.update_status()

        # Setup system tray
        self.setup_tray_icon()

        # Start connection status checking
        self.check_phivolcs_connection()

    def load_config(self):
        """Load configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Default config
            return {
                "latitude": 14.5995,
                "longitude": 120.9842,
                "radius_km": 100,
                "min_magnitude": 3.0,
                "check_interval_seconds": 60,
                "phivolcs_url": "https://earthquake.phivolcs.dost.gov.ph/2007EQLatest/latestEQ.json",
                "address": "Manila, Philippines"
            }

    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def setup_tray_icon(self):
        """Setup system tray icon"""
        if not self.icon_path or not os.path.exists(self.icon_path):
            return

        try:
            # Load icon image
            image = Image.open(self.icon_path)

            # Create menu for tray icon
            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window, default=True),
                pystray.MenuItem("Hide", self.hide_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start Monitoring", self.tray_start_monitoring,
                               visible=lambda item: not self.is_monitoring),
                pystray.MenuItem("Stop Monitoring", self.tray_stop_monitoring,
                               visible=lambda item: self.is_monitoring),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.quit_application)
            )

            # Create system tray icon
            self.tray_icon = pystray.Icon(
                "earthquake_monitor",
                image,
                "Earthquake Alert",
                menu
            )

        except Exception as e:
            logging.error(f"Error setting up tray icon: {e}")

    def show_window(self, icon=None, item=None):
        """Show the main window"""
        self.root.after(0, self._show_window)

    def _show_window(self):
        """Internal method to show window in main thread"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_minimized_to_tray = False

    def hide_window(self, icon=None, item=None):
        """Hide window to system tray"""
        self.root.after(0, self._hide_window)

    def _hide_window(self):
        """Internal method to hide window in main thread"""
        self.root.withdraw()
        self.is_minimized_to_tray = True

        # Start tray icon if not already running
        if self.tray_icon and not self.tray_icon._running:
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def tray_start_monitoring(self, icon=None, item=None):
        """Start monitoring from tray menu"""
        self.root.after(0, self.start_monitoring)

    def tray_stop_monitoring(self, icon=None, item=None):
        """Stop monitoring from tray menu"""
        self.root.after(0, self.stop_monitoring)

    def quit_application(self, icon=None, item=None):
        """Quit application completely"""
        self.root.after(0, self._quit_application)

    def _quit_application(self):
        """Internal method to quit in main thread"""
        if self.is_monitoring:
            self.stop_monitoring()

        if self.tray_icon:
            self.tray_icon.stop()

        self.root.destroy()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Logo and Title
        if self.logo_image:
            logo_label = ttk.Label(main_frame, image=self.logo_image)
            logo_label.pack(pady=(0, 10))

        title_label = ttk.Label(
            main_frame,
            text="Tremr",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 15))

        # Monitoring status
        self.status_label = ttk.Label(
            status_frame,
            text="● Stopped",
            font=("Segoe UI", 11),
            foreground="red"
        )
        self.status_label.pack()

        # PHIVOLCS connection status
        connection_frame = ttk.Frame(status_frame)
        connection_frame.pack(pady=(10, 0))

        ttk.Label(
            connection_frame,
            text="PHIVOLCS Connection:",
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.connection_status_label = ttk.Label(
            connection_frame,
            text="● Checking...",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.connection_status_label.pack(side=tk.LEFT)

        self.connection_detail_label = ttk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        self.connection_detail_label.pack(pady=(2, 0))

        # Location Frame
        location_frame = ttk.LabelFrame(main_frame, text="Monitoring Location", padding="10")
        location_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(location_frame, text="Address:", font=("Segoe UI", 9)).pack(anchor=tk.W)

        # Address input
        address_input_frame = ttk.Frame(location_frame)
        address_input_frame.pack(fill=tk.X, pady=(5, 5))

        self.address_var = tk.StringVar(value=self.config.get('address', 'Manila, Philippines'))
        self.address_entry = ttk.Entry(
            address_input_frame,
            textvariable=self.address_var,
            font=("Segoe UI", 10)
        )
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.search_btn = ttk.Button(
            address_input_frame,
            text="Search",
            command=self.search_address,
            width=10
        )
        self.search_btn.pack(side=tk.RIGHT)

        # Coordinates display
        self.coords_label = ttk.Label(
            location_frame,
            text=f"Coordinates: {self.config['latitude']:.4f}, {self.config['longitude']:.4f}",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        self.coords_label.pack(anchor=tk.W, pady=(5, 0))

        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Alert Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 15))

        # Radius
        radius_frame = ttk.Frame(settings_frame)
        radius_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(radius_frame, text="Alert Radius (km):", width=20).pack(side=tk.LEFT)
        self.radius_var = tk.StringVar(value=str(self.config['radius_km']))
        radius_spinbox = ttk.Spinbox(
            radius_frame,
            from_=10,
            to=500,
            textvariable=self.radius_var,
            width=15
        )
        radius_spinbox.pack(side=tk.RIGHT)

        # Magnitude
        magnitude_frame = ttk.Frame(settings_frame)
        magnitude_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(magnitude_frame, text="Min Magnitude:", width=20).pack(side=tk.LEFT)
        self.magnitude_var = tk.StringVar(value=str(self.config['min_magnitude']))
        magnitude_spinbox = ttk.Spinbox(
            magnitude_frame,
            from_=1.0,
            to=10.0,
            increment=0.1,
            textvariable=self.magnitude_var,
            width=15
        )
        magnitude_spinbox.pack(side=tk.RIGHT)

        # Check interval
        interval_frame = ttk.Frame(settings_frame)
        interval_frame.pack(fill=tk.X)

        ttk.Label(interval_frame, text="Check Interval (sec):", width=20).pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value=str(self.config['check_interval_seconds']))
        interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=30,
            to=300,
            increment=10,
            textvariable=self.interval_var,
            width=15
        )
        interval_spinbox.pack(side=tk.RIGHT)

        # Auto-start Frame
        autostart_frame = ttk.LabelFrame(main_frame, text="System Settings", padding="10")
        autostart_frame.pack(fill=tk.X, pady=(0, 15))

        self.autostart_var = tk.BooleanVar(value=self.check_autostart())
        autostart_check = ttk.Checkbutton(
            autostart_frame,
            text="Start monitoring automatically when computer starts",
            variable=self.autostart_var,
            command=self.toggle_autostart
        )
        autostart_check.pack(anchor=tk.W)

        # Control Buttons Frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))

        self.start_btn = ttk.Button(
            buttons_frame,
            text="▶ Start Monitoring",
            command=self.start_monitoring,
            style="Accent.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.stop_btn = ttk.Button(
            buttons_frame,
            text="■ Stop Monitoring",
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

        # Minimize to Tray Button
        tray_frame = ttk.Frame(main_frame)
        tray_frame.pack(fill=tk.X, pady=(0, 15))

        self.tray_btn = ttk.Button(
            tray_frame,
            text="↓ Minimize to Tray (Run in Background)",
            command=self.hide_window
        )
        self.tray_btn.pack(fill=tk.X)

        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 8),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Load initial logs
        self.load_recent_logs()

    def log(self, message):
        """Add message to log display"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def load_recent_logs(self):
        """Load recent logs from file"""
        if os.path.exists('earthquake_monitor.log'):
            try:
                with open('earthquake_monitor.log', 'r') as f:
                    lines = f.readlines()
                    recent = lines[-20:] if len(lines) > 20 else lines
                    for line in recent:
                        self.log_text.configure(state=tk.NORMAL)
                        self.log_text.insert(tk.END, line)
                        self.log_text.configure(state=tk.DISABLED)
                    self.log_text.see(tk.END)
            except:
                pass

    def search_address(self):
        """Search for address and get coordinates"""
        address = self.address_var.get().strip()

        if not address:
            messagebox.showwarning("Empty Address", "Please enter an address to search.")
            return

        self.log(f"Searching for: {address}")
        self.search_btn.configure(state=tk.DISABLED, text="Searching...")
        self.root.update()

        try:
            # Search in a thread to avoid freezing GUI
            location = self.geolocator.geocode(address, timeout=10)

            if location:
                self.config['latitude'] = location.latitude
                self.config['longitude'] = location.longitude
                self.config['address'] = address

                self.coords_label.configure(
                    text=f"Coordinates: {location.latitude:.4f}, {location.longitude:.4f}"
                )
                self.log(f"[+] Found: {location.address}")
                self.log(f"  Coordinates: {location.latitude:.4f}, {location.longitude:.4f}")

                messagebox.showinfo(
                    "Location Found",
                    f"Location set to:\n{location.address}\n\n"
                    f"Coordinates: {location.latitude:.4f}, {location.longitude:.4f}"
                )
            else:
                messagebox.showerror(
                    "Location Not Found",
                    "Could not find the address. Please try:\n"
                    "- A more specific address\n"
                    "- Including city and country\n"
                    "- Example: 'Quezon City, Philippines'"
                )
                self.log("[-] Location not found")

        except Exception as e:
            messagebox.showerror("Error", f"Error searching address:\n{str(e)}")
            self.log(f"[-] Error: {str(e)}")

        finally:
            self.search_btn.configure(state=tk.NORMAL, text="Search")

    def start_monitoring(self):
        """Start earthquake monitoring"""
        # Save current settings
        try:
            self.config['radius_km'] = float(self.radius_var.get())
            self.config['min_magnitude'] = float(self.magnitude_var.get())
            self.config['check_interval_seconds'] = int(self.interval_var.get())
            self.save_config()
        except ValueError as e:
            messagebox.showerror("Invalid Settings", f"Please check your settings:\n{str(e)}")
            return

        self.log("=" * 50)
        self.log("Starting earthquake monitoring...")
        self.log(f"Location: {self.config.get('address', 'Unknown')}")
        self.log(f"Coordinates: {self.config['latitude']:.4f}, {self.config['longitude']:.4f}")
        self.log(f"Radius: {self.config['radius_km']} km")
        self.log(f"Min Magnitude: {self.config['min_magnitude']}")
        self.log("=" * 50)

        # Start monitoring in separate thread
        self.is_monitoring = True
        self.monitor = EarthquakeMonitor(self.config_file)

        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Update UI
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.address_entry.configure(state=tk.DISABLED)
        self.search_btn.configure(state=tk.DISABLED)
        self.update_status(monitoring=True)

    def monitor_loop(self):
        """Monitoring loop running in separate thread"""
        try:
            while self.is_monitoring:
                data = self.monitor.fetch_earthquake_data()
                if data:
                    self.monitor.process_earthquakes(data)

                # Check at regular intervals
                for _ in range(self.config['check_interval_seconds']):
                    if not self.is_monitoring:
                        break
                    import time
                    time.sleep(1)

        except Exception as e:
            self.log(f"Error in monitoring: {str(e)}")
            self.is_monitoring = False
            self.root.after(0, self.stop_monitoring)

    def stop_monitoring(self):
        """Stop earthquake monitoring"""
        self.log("Stopping monitoring...")
        self.is_monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)

        self.monitor = None
        self.monitor_thread = None

        # Update UI
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.address_entry.configure(state=tk.NORMAL)
        self.search_btn.configure(state=tk.NORMAL)
        self.update_status(monitoring=False)
        self.log("Monitoring stopped.")

    def update_status(self, monitoring=False):
        """Update status display"""
        if monitoring:
            self.status_label.configure(
                text="● Monitoring Active",
                foreground="green"
            )
        else:
            self.status_label.configure(
                text="● Stopped",
                foreground="red"
            )

    def check_phivolcs_connection(self):
        """Check PHIVOLCS connection status"""
        def check_in_thread():
            try:
                # Create a temporary monitor instance to test connection
                from main import EarthquakeMonitor
                temp_monitor = EarthquakeMonitor(self.config_file)
                is_connected, message = temp_monitor.test_connection()

                # Update UI in main thread
                self.root.after(0, self.update_connection_status, is_connected, message)

            except Exception as e:
                self.root.after(0, self.update_connection_status, False, f"Error: {str(e)}")

        # Run check in background thread to avoid blocking UI
        threading.Thread(target=check_in_thread, daemon=True).start()

        # Schedule next check
        self.root.after(self.connection_check_interval, self.check_phivolcs_connection)

    def update_connection_status(self, is_connected, message):
        """Update connection status display"""
        if is_connected:
            self.connection_status_label.configure(
                text="● Connected",
                foreground="green"
            )
            self.connection_detail_label.configure(
                text="PHIVOLCS API is responding normally",
                foreground="green"
            )
        else:
            self.connection_status_label.configure(
                text="● Disconnected",
                foreground="red"
            )
            self.connection_detail_label.configure(
                text=f"Issue: {message}",
                foreground="red"
            )

        # Log status change
        if self.last_connection_status != is_connected:
            if is_connected:
                self.log("[+] PHIVOLCS connection: OK")
            else:
                self.log(f"[-] PHIVOLCS connection failed: {message}")
            self.last_connection_status = is_connected

    def check_autostart(self):
        """Check if app is set to autostart"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, "Tremr")
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except:
            return False

    def toggle_autostart(self):
        """Toggle autostart on Windows boot"""
        app_path = os.path.abspath(sys.argv[0])

        # If running as .py file, use pythonw to launch GUI
        if app_path.endswith('.py'):
            python_path = sys.executable.replace('python.exe', 'pythonw.exe')
            command = f'"{python_path}" "{app_path}"'
        else:
            command = f'"{app_path}"'

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_WRITE
            )

            if self.autostart_var.get():
                # Enable autostart
                winreg.SetValueEx(key, "Tremr", 0, winreg.REG_SZ, command)
                self.log("[+] Auto-start enabled")
                messagebox.showinfo(
                    "Auto-start Enabled",
                    "Tremr will now start automatically when Windows starts."
                )
            else:
                # Disable autostart
                try:
                    winreg.DeleteValue(key, "Tremr")
                    self.log("[+] Auto-start disabled")
                    messagebox.showinfo(
                        "Auto-start Disabled",
                        "Tremr will no longer start automatically."
                    )
                except WindowsError:
                    pass

            winreg.CloseKey(key)

        except Exception as e:
            messagebox.showerror("Error", f"Could not modify auto-start settings:\n{str(e)}")
            self.autostart_var.set(not self.autostart_var.get())

    def on_closing(self):
        """Handle window closing"""
        if self.is_monitoring:
            # Ask if user wants to minimize to tray or exit
            response = messagebox.askyesnocancel(
                "Monitoring Active",
                "Earthquake monitoring is active.\n\n"
                "Yes = Minimize to tray (keep monitoring)\n"
                "No = Exit and stop monitoring\n"
                "Cancel = Stay open"
            )

            if response is True:  # Yes - minimize to tray
                self.hide_window()
            elif response is False:  # No - exit
                self.stop_monitoring()
                if self.tray_icon:
                    self.tray_icon.stop()
                self.root.destroy()
            # If None (Cancel), do nothing
        else:
            # Not monitoring, ask to minimize or exit
            response = messagebox.askyesno(
                "Exit Application",
                "Do you want to minimize to tray instead of exiting?\n\n"
                "Yes = Minimize to tray\n"
                "No = Exit completely"
            )

            if response:  # Yes - minimize to tray
                self.hide_window()
            else:  # No - exit
                if self.tray_icon:
                    self.tray_icon.stop()
                self.root.destroy()


def check_single_instance():
    """Check if another instance is already running"""
    lock_file = os.path.join(tempfile.gettempdir(), 'tremr.lock')

    # Check if lock file exists and process is still running
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process with this PID exists
            import psutil
            if psutil.pid_exists(pid):
                try:
                    process = psutil.Process(pid)
                    # Check if it's actually our application
                    if 'python' in process.name().lower() or 'earthquake' in process.name().lower():
                        return False, lock_file
                except:
                    pass
        except:
            pass

        # Lock file exists but process doesn't, remove stale lock
        try:
            os.remove(lock_file)
        except:
            pass

    # Create lock file with current PID
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        return True, lock_file
    except:
        return True, None


def main():
    """Main entry point"""
    # Check for single instance
    can_run, lock_file = check_single_instance()

    if not can_run:
        # Another instance is running
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        messagebox.showwarning(
            "Already Running",
            "Tremr is already running!\n\n"
            "Check your system tray for the earthquake icon.\n\n"
            "Only one instance can run at a time to prevent duplicate alerts."
        )
        root.destroy()
        sys.exit(0)

    # Continue with normal startup
    root = tk.Tk()

    # Set modern style
    style = ttk.Style()
    style.theme_use('vista')  # Modern Windows theme

    app = EarthquakeMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    try:
        root.mainloop()
    finally:
        # Cleanup lock file when app closes
        if lock_file and os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except:
                pass


if __name__ == '__main__':
    main()
