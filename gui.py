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
import tkintermapview

class EarthquakeMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tremr")
        self.root.geometry("450x750")  # 50% width (450) x increased height for vertical layout
        self.root.resizable(False, False)

        # Dark theme colors
        self.bg_color = "#0a0a0a"
        self.card_bg = "#1a1a1a"
        self.text_color = "#ffffff"
        self.text_secondary = "#aaaaaa"
        self.accent_color = "#00d4ff"

        # Set dark background
        self.root.configure(bg=self.bg_color)

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
                # Resize logo to fit nicely in UI (200x200 pixels for larger display)
                logo_pil = logo_pil.resize((200, 200), Image.Resampling.LANCZOS)
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

        # Map variables
        self.map_widget = None
        self.location_marker = None

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
        """Setup the user interface - 100% matching the reference image"""
        # Create canvas for starfield background
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Add stars to background
        self.create_starfield()

        # Main container with dark background (minimal padding for narrow view)
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=12, pady=8)
        main_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Logo and Title (smaller logo for narrow view)
        if self.logo_image:
            # Create smaller logo for narrow window
            from PIL import Image, ImageTk
            logo_pil = Image.open('tremr_logo.png')
            logo_pil = logo_pil.resize((80, 80), Image.Resampling.LANCZOS)  # Further reduced for narrow view
            self.logo_image_small = ImageTk.PhotoImage(logo_pil)
            logo_label = tk.Label(main_frame, image=self.logo_image_small, bg=self.bg_color)
            logo_label.pack(pady=(3, 5))

        title_label = tk.Label(
            main_frame,
            text="🔔 Tremr",
            font=("Segoe UI", 18, "bold"),  # Further reduced for narrow view
            foreground=self.text_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 2))

        subtitle_label = tk.Label(
            main_frame,
            text="Real-time Earthquake Monitoring System",
            font=("Segoe UI", 9),  # Further reduced
            foreground=self.text_secondary,
            bg=self.bg_color
        )
        subtitle_label.pack(pady=(0, 8))

        # Status Section Header
        status_header = tk.Label(
            main_frame,
            text="📊 Status",
            font=("Segoe UI", 8, "bold"),
            foreground=self.text_secondary,
            bg=self.bg_color
        )
        status_header.pack(anchor=tk.W, pady=(0, 4))

        # Status Card (vertical layout for narrow window)
        status_card = tk.Frame(main_frame, bg=self.card_bg, highlightbackground="#2a5a7a", highlightthickness=1)
        status_card.pack(fill=tk.X, pady=(0, 6))

        status_inner = tk.Frame(status_card, bg=self.card_bg, padx=10, pady=8)
        status_inner.pack(fill=tk.X)

        # Monitoring Status
        status_row = tk.Frame(status_inner, bg=self.card_bg)
        status_row.pack(anchor=tk.W, pady=(0, 6))

        self.status_indicator = tk.Label(
            status_row,
            text="●",
            font=("Segoe UI", 14, "bold"),
            foreground="#FF4444",
            bg=self.card_bg
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 6))

        self.status_label = tk.Label(
            status_row,
            text="Monitoring Stopped",
            font=("Segoe UI", 11, "bold"),
            foreground="#FF4444",
            bg=self.card_bg
        )
        self.status_label.pack(side=tk.LEFT)

        # PHIVOLCS Connection
        conn_header_row = tk.Frame(status_inner, bg=self.card_bg)
        conn_header_row.pack(anchor=tk.W, pady=(0, 3))

        tk.Label(
            conn_header_row,
            text="🌐 PHIVOLCS:",
            font=("Segoe UI", 8),
            foreground=self.text_secondary,
            bg=self.card_bg
        ).pack(side=tk.LEFT)

        self.connection_status_label = tk.Label(
            conn_header_row,
            text=" ● Connected",
            font=("Segoe UI", 8, "bold"),
            foreground="#4CAF50",
            bg=self.card_bg
        )
        self.connection_status_label.pack(side=tk.LEFT)

        # Connection detail text
        self.connection_detail_label = tk.Label(
            status_inner,
            text="API responding normally",
            font=("Segoe UI", 7),
            foreground="#4CAF50",
            bg=self.card_bg
        )
        self.connection_detail_label.pack(anchor=tk.W)

        # Map widget (full width for narrow window)
        try:
            self.map_widget = tkintermapview.TkinterMapView(
                main_frame,
                width=426,  # Full width minus padding (450 - 24 = 426)
                height=140,  # Adjusted height for better visibility
                corner_radius=3
            )
            self.map_widget.pack(pady=(0, 8))

            # Set initial position to user's location
            lat = self.config.get('latitude', 14.6994)
            lon = self.config.get('longitude', 121.0824)

            # Set position and zoom to show Philippines
            self.map_widget.set_position(lat, lon)
            self.map_widget.set_zoom(6)

            # Add red circle marker
            self.location_marker = self.map_widget.set_marker(
                lat,
                lon,
                text="",
                marker_color_circle="red",
                marker_color_outside="darkred"
            )
        except Exception as e:
            logging.error(f"Error creating map widget: {e}")

        # Monitoring Location Section
        location_header = tk.Label(
            main_frame,
            text="📍 Monitoring Location",
            font=("Segoe UI", 8, "bold"),
            foreground=self.text_secondary,
            bg=self.bg_color
        )
        location_header.pack(anchor=tk.W, pady=(0, 5))

        location_card = tk.Frame(main_frame, bg=self.card_bg, highlightbackground="#2a5a7a", highlightthickness=1)
        location_card.pack(fill=tk.X, pady=(0, 8))

        location_inner = tk.Frame(location_card, bg=self.card_bg, padx=10, pady=8)
        location_inner.pack(fill=tk.X)

        # Address label
        tk.Label(
            location_inner,
            text="Address:",
            font=("Segoe UI", 8),
            foreground=self.text_secondary,
            bg=self.card_bg
        ).pack(anchor=tk.W, pady=(0, 4))

        # Address input and search button
        address_row = tk.Frame(location_inner, bg=self.card_bg)
        address_row.pack(fill=tk.X, pady=(0, 5))

        self.address_var = tk.StringVar(value=self.config.get('address', 'commonwealth, Quezon city'))
        self.address_entry = tk.Entry(
            address_row,
            textvariable=self.address_var,
            font=("Segoe UI", 8),
            bg="#0d0d0d",
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            highlightthickness=0,
            bd=0
        )
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=3)

        self.search_btn = tk.Button(
            address_row,
            text="Search",
            command=self.search_address,
            font=("Segoe UI", 8),
            bg="#1a1a1a",
            fg=self.text_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=12,
            pady=3,
            highlightthickness=1,
            highlightbackground="#3a3a3a",
            activebackground="#2a2a2a",
            bd=0
        )
        self.search_btn.pack(side=tk.RIGHT)

        # Coordinates display
        self.coords_label = tk.Label(
            location_inner,
            text=f"Coordinates: {self.config['latitude']:.4f}, {self.config['longitude']:.4f}",
            font=("Segoe UI", 7),
            foreground="#666666",
            bg=self.card_bg
        )
        self.coords_label.pack(anchor=tk.W)

        # Alert Settings Section
        settings_header = tk.Label(
            main_frame,
            text="⚙️ Alert Settings",
            font=("Segoe UI", 8, "bold"),
            foreground=self.text_secondary,
            bg=self.bg_color
        )
        settings_header.pack(anchor=tk.W, pady=(0, 5))

        settings_card = tk.Frame(main_frame, bg=self.card_bg, highlightbackground="#2a5a7a", highlightthickness=1)
        settings_card.pack(fill=tk.X, pady=(0, 10))

        settings_inner = tk.Frame(settings_card, bg=self.card_bg, padx=10, pady=8)
        settings_inner.pack(fill=tk.X)

        # Alert Radius header with value
        radius_header = tk.Frame(settings_inner, bg=self.card_bg)
        radius_header.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            radius_header,
            text="Alert Radius (km):",
            font=("Segoe UI", 8),
            foreground=self.text_secondary,
            bg=self.card_bg
        ).pack(side=tk.LEFT)

        # Value and spinbox controls
        radius_controls = tk.Frame(radius_header, bg=self.card_bg)
        radius_controls.pack(side=tk.RIGHT)

        # Up/down buttons
        btn_frame = tk.Frame(radius_controls, bg=self.card_bg)
        btn_frame.pack(side=tk.RIGHT, padx=(5, 0))

        up_btn = tk.Button(
            btn_frame,
            text="▲",
            font=("Arial", 5),
            bg="#1a1a1a",
            fg="#888888",
            relief=tk.FLAT,
            cursor="hand2",
            width=2,
            command=lambda: self.adjust_radius(50),
            bd=0
        )
        up_btn.pack()

        down_btn = tk.Button(
            btn_frame,
            text="▼",
            font=("Arial", 5),
            bg="#1a1a1a",
            fg="#888888",
            relief=tk.FLAT,
            cursor="hand2",
            width=2,
            command=lambda: self.adjust_radius(-50),
            bd=0
        )
        down_btn.pack()

        # Ensure radius is within new bounds (50-12000)
        initial_radius = max(50, min(12000, self.config.get('radius_km', 100)))

        # Value display in circle (smaller for narrow view)
        value_display = tk.Frame(radius_controls, bg=self.card_bg)
        value_display.pack(side=tk.RIGHT, padx=(0, 2))

        circle_canvas = tk.Canvas(value_display, width=35, height=35, bg=self.card_bg, highlightthickness=0)
        circle_canvas.pack()
        circle_canvas.create_oval(2, 2, 33, 33, outline=self.accent_color, width=2)

        self.radius_value_label = tk.Label(
            value_display,
            text=f"{int(initial_radius)}",
            font=("Segoe UI", 8, "bold"),
            foreground=self.text_color,
            bg=self.card_bg
        )
        self.radius_value_label.place(x=17, y=17, anchor="center")

        # Aesthetic cyan slider (30% width)
        slider_container = tk.Frame(settings_inner, bg=self.card_bg)
        slider_container.pack(fill=tk.X, pady=(3, 0))

        self.radius_var = tk.DoubleVar(value=initial_radius)
        radius_slider = tk.Scale(
            slider_container,
            from_=50,
            to=12000,
            resolution=10,  # Increment by 10km for smoother scrolling
            orient=tk.HORIZONTAL,
            variable=self.radius_var,
            showvalue=0,
            bg=self.card_bg,
            fg="#00d4ff",  # Cyan slider handle
            troughcolor="#0a2a3a",  # Dark cyan trough
            highlightthickness=1,
            highlightbackground="#00d4ff",  # Cyan border
            highlightcolor="#00d4ff",
            relief=tk.FLAT,
            activebackground="#00ffff",  # Bright cyan when active
            sliderrelief=tk.RAISED,
            sliderlength=20,  # Longer handle for better grip
            width=8,  # Thicker slider bar
            bd=0,
            length= 420, 
            command=self.update_radius_label
        )
        radius_slider.pack(side=tk.LEFT, pady=(0, 3))

        # Hidden settings for compatibility
        self.magnitude_var = tk.DoubleVar(value=self.config.get('min_magnitude', 3.0))
        self.interval_var = tk.IntVar(value=self.config.get('check_interval_seconds', 60))

        # Add sparkle decoration in bottom right
        self.add_sparkle_decoration()

        # Load initial logs
        self.load_recent_logs()

    def create_starfield(self):
        """Create animated starfield background"""
        import random
        self.stars = []
        for _ in range(50):  # Increased stars for taller window
            x = random.randint(0, 450)  # Adjusted for 50% width
            y = random.randint(0, 750)  # Adjusted for taller height
            size = random.choice([1, 1, 1, 2, 2, 3])
            brightness = random.choice(['#444444', '#666666', '#888888', '#999999', '#aaaaaa'])
            star = self.canvas.create_oval(x, y, x+size, y+size, fill=brightness, outline='')
            self.stars.append((star, x, y))

    def add_sparkle_decoration(self):
        """Add sparkle/diamond decoration in bottom right corner"""
        # Position in bottom right area (adjusted for 50% width and taller height)
        sparkle_x = 410  # Adjusted for 450px width (450 - 40 = 410)
        sparkle_y = 710  # Adjusted for 750px height (750 - 40 = 710)

        # Create sparkle/star shape
        # Main diamond shape
        self.canvas.create_polygon(
            sparkle_x, sparkle_y - 30,      # top
            sparkle_x + 8, sparkle_y - 10,  # top right
            sparkle_x + 30, sparkle_y,      # right
            sparkle_x + 8, sparkle_y + 10,  # bottom right
            sparkle_x, sparkle_y + 30,      # bottom
            sparkle_x - 8, sparkle_y + 10,  # bottom left
            sparkle_x - 30, sparkle_y,      # left
            sparkle_x - 8, sparkle_y - 10,  # top left
            fill='#cccccc',
            outline='#ffffff',
            width=2
        )

        # Add smaller sparkles around it
        sparkles = [
            (sparkle_x - 50, sparkle_y - 40, 8),
            (sparkle_x + 45, sparkle_y - 35, 6),
            (sparkle_x + 50, sparkle_y + 30, 5),
        ]

        for sx, sy, ssize in sparkles:
            self.canvas.create_polygon(
                sx, sy - ssize,
                sx + ssize//2, sy,
                sx, sy + ssize,
                sx - ssize//2, sy,
                fill='#999999',
                outline='#aaaaaa',
                width=1
            )

    def adjust_radius(self, amount):
        """Adjust radius by amount"""
        current = self.radius_var.get()
        new_value = max(50, min(12000, current + amount))
        self.radius_var.set(new_value)
        self.update_radius_label(new_value)

    def update_radius_label(self, value):
        """Update the radius value label when slider changes"""
        # Format value based on size for better display
        val = float(value)
        if val >= 1000:
            # Show as integer for large values (e.g., "1200" instead of "1200.0")
            self.radius_value_label.configure(text=f"{int(val)}")
        else:
            # Show one decimal for smaller values
            self.radius_value_label.configure(text=f"{val:.0f}")

    def log(self, message):
        """Add message to log display - now just logs to file"""
        logging.info(message)

    def load_recent_logs(self):
        """Load recent logs from file - disabled in new design"""
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

                # Update map marker if map widget exists
                if self.map_widget:
                    try:
                        # Remove old marker if it exists
                        if self.location_marker:
                            self.location_marker.delete()

                        # Set new position on map
                        self.map_widget.set_position(location.latitude, location.longitude)
                        self.map_widget.set_zoom(6)

                        # Add new marker
                        self.location_marker = self.map_widget.set_marker(
                            location.latitude,
                            location.longitude,
                            text="",
                            marker_color_circle="red",
                            marker_color_outside="darkred"
                        )
                    except Exception as e:
                        logging.error(f"Error updating map: {e}")

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
        self.address_entry.configure(state=tk.NORMAL)
        self.search_btn.configure(state=tk.NORMAL)
        self.update_status(monitoring=False)
        self.log("Monitoring stopped.")

    def update_status(self, monitoring=False):
        """Update status display"""
        if monitoring:
            self.status_indicator.configure(foreground="#4CAF50")  # Green
            self.status_label.configure(
                text="Monitoring Active",
                foreground="#4CAF50"
            )
        else:
            self.status_indicator.configure(foreground="#FF5555")  # Red
            self.status_label.configure(
                text="Monitoring Stopped",
                foreground="#FF5555"
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
                text=" ● Connected",
                foreground="#4CAF50"
            )
            self.connection_detail_label.configure(
                text="PHIVOLCS API is responding normally",
                foreground="#4CAF50"
            )
        else:
            self.connection_status_label.configure(
                text=" ● Disconnected",
                foreground="#FF4444"
            )
            self.connection_detail_label.configure(
                text=f"Issue: {message}",
                foreground="#FF4444"
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
