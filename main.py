"""
Tremr - PHIVOLCS Earthquake Monitor
Monitors PHIVOLCS earthquake data and alerts for nearby earthquakes
"""

import requests
import time
import json
import os
import sys
import platform
from datetime import datetime
from geopy.distance import geodesic
from plyer import notification
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('earthquake_monitor.log'),
        logging.StreamHandler()
    ]
)

class EarthquakeMonitor:
    def __init__(self, config_file='config.json'):
        """Initialize the earthquake monitor with configuration"""
        self.config = self.load_config(config_file)
        self.seen_earthquakes = set()
        self.load_seen_earthquakes()
        self.icon_path = self.ensure_icon_exists()
        self.sound_enabled = True

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        if not os.path.exists(config_file):
            # Default configuration
            default_config = {
                "latitude": 14.5995,  # Manila coordinates
                "longitude": 120.9842,
                "radius_km": 100,
                "min_magnitude": 3.0,
                "check_interval_seconds": 60,
                "phivolcs_url": "https://earthquake.phivolcs.dost.gov.ph/2007EQLatest/latestEQ.json"
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            logging.info(f"Created default config file: {config_file}")
            return default_config

        with open(config_file, 'r') as f:
            return json.load(f)

    def load_seen_earthquakes(self):
        """Load previously seen earthquakes from file"""
        if os.path.exists('seen_earthquakes.json'):
            with open('seen_earthquakes.json', 'r') as f:
                self.seen_earthquakes = set(json.load(f))
                logging.info(f"Loaded {len(self.seen_earthquakes)} previously seen earthquakes")

    def save_seen_earthquakes(self):
        """Save seen earthquakes to file"""
        with open('seen_earthquakes.json', 'w') as f:
            json.dump(list(self.seen_earthquakes), f)

    def test_connection(self):
        """Test connection to PHIVOLCS website"""
        try:
            # Import scraper
            from phivolcs_scraper import scrape_phivolcs_earthquakes

            # Try to scrape data
            data = scrape_phivolcs_earthquakes()

            if data and 'earthquakes' in data and len(data['earthquakes']) > 0:
                return True, "Connected"
            else:
                return False, "No earthquake data available"

        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to server"
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP Error: {e.response.status_code}"
        except requests.exceptions.SSLError:
            return False, "SSL certificate error"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def fetch_earthquake_data(self):
        """Fetch latest earthquake data from PHIVOLCS by scraping their website"""
        try:
            # Import scraper
            from phivolcs_scraper import scrape_phivolcs_earthquakes

            # Scrape earthquake data from PHIVOLCS website
            data = scrape_phivolcs_earthquakes()

            if data:
                logging.info(f"Successfully fetched {len(data.get('earthquakes', []))} earthquakes from PHIVOLCS")
                return data
            else:
                logging.error("Failed to scrape earthquake data from PHIVOLCS")
                return None

        except Exception as e:
            logging.error(f"Error fetching earthquake data: {e}")
            return None

    def calculate_distance(self, lat, lon):
        """Calculate distance from configured location to earthquake"""
        user_location = (self.config['latitude'], self.config['longitude'])
        earthquake_location = (lat, lon)
        return geodesic(user_location, earthquake_location).kilometers

    def create_earthquake_id(self, earthquake):
        """Create a unique ID for an earthquake"""
        # Use timestamp and location as unique identifier
        return f"{earthquake.get('date', '')}_{earthquake.get('time', '')}_{earthquake.get('latitude', '')}_{earthquake.get('longitude', '')}"

    def ensure_icon_exists(self):
        """Ensure the earthquake warning icon exists, create if not"""
        # On Windows, we need .ico format, on other platforms .png works
        is_windows = platform.system() == 'Windows'
        icon_path = 'earthquake_warning.ico' if is_windows else 'earthquake_warning.png'

        if os.path.exists(icon_path):
            return os.path.abspath(icon_path)

        try:
            # Try to create the icon
            from PIL import Image, ImageDraw
            logging.info("Creating earthquake warning icon...")

            size = 256
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            center = size // 2

            # Draw red circle with glow
            for i in range(5, 0, -1):
                alpha = 40 * i
                glow_color = (255, 0, 0, alpha)
                radius = center - (10 * (5 - i))
                draw.ellipse([center - radius, center - radius,
                            center + radius, center + radius],
                           fill=glow_color)

            # Main gradient circle
            for i in range(20, 0, -1):
                radius = center - 20 - i
                r = 255
                g = int(140 * (20 - i) / 20)
                color = (r, g, 0, 255)
                draw.ellipse([center - radius, center - radius,
                            center + radius, center + radius],
                           fill=color)

            # Warning triangle
            triangle_size = size // 3
            triangle_top = center - triangle_size // 2
            triangle_bottom = center + triangle_size // 2
            triangle_left = center - triangle_size // 2
            triangle_right = center + triangle_size // 2

            yellow = (255, 215, 0, 255)
            dark_red = (180, 0, 0, 255)

            outline_points = [
                (center, triangle_top - 3),
                (triangle_left - 3, triangle_bottom + 3),
                (triangle_right + 3, triangle_bottom + 3)
            ]
            triangle_points = [
                (center, triangle_top),
                (triangle_left, triangle_bottom),
                (triangle_right, triangle_bottom)
            ]

            draw.polygon(outline_points, fill=(0, 0, 0, 255))
            draw.polygon(triangle_points, fill=yellow)

            # Exclamation mark
            exclaim_width = size // 20
            exclaim_top = center - triangle_size // 3
            exclaim_middle = center + triangle_size // 6

            draw.rectangle([center - exclaim_width, exclaim_top,
                          center + exclaim_width, exclaim_middle],
                         fill=dark_red)

            dot_size = exclaim_width * 2
            dot_top = exclaim_middle + exclaim_width * 2
            draw.ellipse([center - dot_size, dot_top,
                         center + dot_size, dot_top + dot_size * 2],
                        fill=dark_red)

            # Save icon in appropriate format
            if is_windows:
                # Save as .ico for Windows
                img.save(icon_path, 'ICO', sizes=[(256, 256)])
                logging.info(f"Created earthquake warning icon: {icon_path}")
            else:
                # Save as .png for other platforms
                img.save(icon_path, 'PNG')
                logging.info(f"Created earthquake warning icon: {icon_path}")

            return os.path.abspath(icon_path)

        except Exception as e:
            logging.warning(f"Could not create icon: {e}")
            return None

    def play_warning_sound(self):
        """Play warning sound for earthquake alert"""
        if not self.sound_enabled:
            return

        try:
            # Try different sound methods based on platform
            system = platform.system()

            if system == 'Windows':
                # Use Windows built-in winsound
                import winsound
                # Play system exclamation sound multiple times for urgency
                for _ in range(3):
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                    time.sleep(0.3)
                logging.info("Played warning sound (Windows system beep)")

            elif system == 'Darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Sosumi.aiff')
                logging.info("Played warning sound (macOS)")

            else:  # Linux
                os.system('paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga 2>/dev/null || beep')
                logging.info("Played warning sound (Linux)")

        except Exception as e:
            logging.warning(f"Could not play sound: {e}")
            # Try basic beep as fallback
            try:
                print('\a' * 3)  # Terminal bell
            except:
                pass

    def show_notification(self, earthquake, distance):
        """Show desktop notification for earthquake with sound and icon"""
        magnitude = earthquake.get('magnitude', 'Unknown')
        location = earthquake.get('location', 'Unknown location')
        depth = earthquake.get('depth', 'Unknown')
        date_time = f"{earthquake.get('date', '')} {earthquake.get('time', '')}"

        title = f"EARTHQUAKE ALERT - Magnitude {magnitude}"
        message = (
            f"Location: {location}\n"
            f"Distance: {distance:.1f} km away\n"
            f"Depth: {depth}\n"
            f"Time: {date_time}"
        )

        try:
            # Play warning sound first
            self.play_warning_sound()

            # Show notification with icon
            notification.notify(
                title=title,
                message=message,
                app_name='Earthquake Alert',
                app_icon=self.icon_path if self.icon_path else None,
                timeout=15
            )
            logging.info(f"Notification sent with sound and icon: {title}")
        except Exception as e:
            logging.error(f"Error showing notification: {e}")

    def process_earthquakes(self, data):
        """Process earthquake data and check for nearby events"""
        if not data or 'earthquakes' not in data:
            logging.warning("No earthquake data to process")
            return

        earthquakes = data['earthquakes']
        new_earthquakes_found = 0

        for earthquake in earthquakes:
            # Create unique ID for this earthquake
            eq_id = self.create_earthquake_id(earthquake)

            # Skip if we've already processed this earthquake
            if eq_id in self.seen_earthquakes:
                continue

            # Get earthquake details
            try:
                lat = float(earthquake.get('latitude', 0))
                lon = float(earthquake.get('longitude', 0))
                magnitude = float(earthquake.get('magnitude', 0))
            except (ValueError, TypeError):
                logging.warning(f"Invalid earthquake data: {earthquake}")
                continue

            # Calculate distance
            distance = self.calculate_distance(lat, lon)

            # Check if earthquake is within radius and meets magnitude threshold
            if (distance <= self.config['radius_km'] and
                magnitude >= self.config['min_magnitude']):

                logging.info(
                    f"NEW EARTHQUAKE: Magnitude {magnitude}, "
                    f"Distance {distance:.1f}km, "
                    f"Location: {earthquake.get('location', 'Unknown')}"
                )

                # Show notification
                self.show_notification(earthquake, distance)
                new_earthquakes_found += 1

            # Mark as seen
            self.seen_earthquakes.add(eq_id)

        if new_earthquakes_found > 0:
            self.save_seen_earthquakes()
            logging.info(f"Processed {new_earthquakes_found} new nearby earthquake(s)")

    def run(self):
        """Main monitoring loop"""
        logging.info("=" * 60)
        logging.info("Tremr - Earthquake Monitor Started")
        logging.info(f"Monitoring location: {self.config['latitude']}, {self.config['longitude']}")
        logging.info(f"Alert radius: {self.config['radius_km']} km")
        logging.info(f"Minimum magnitude: {self.config['min_magnitude']}")
        logging.info(f"Check interval: {self.config['check_interval_seconds']} seconds")
        logging.info("=" * 60)

        while True:
            try:
                data = self.fetch_earthquake_data()
                if data:
                    self.process_earthquakes(data)

                time.sleep(self.config['check_interval_seconds'])

            except KeyboardInterrupt:
                logging.info("Monitoring stopped by user")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                time.sleep(self.config['check_interval_seconds'])

if __name__ == '__main__':
    monitor = EarthquakeMonitor()
    monitor.run()
