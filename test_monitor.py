"""
Test script for Tremr
Uses mock data instead of live PHIVOLCS data
"""

import json
import os
from main import EarthquakeMonitor
import logging

class TestEarthquakeMonitor(EarthquakeMonitor):
    """Test version that uses mock data"""

    def __init__(self, mock_file='mock_data.json', config_file='config.json'):
        """Initialize with mock data file"""
        super().__init__(config_file)
        self.mock_file = mock_file
        logging.info(f"Test mode: Using mock data from {mock_file}")

    def fetch_earthquake_data(self):
        """Override to use mock data instead of live API"""
        try:
            if not os.path.exists(self.mock_file):
                logging.error(f"Mock data file not found: {self.mock_file}")
                return None

            with open(self.mock_file, 'r') as f:
                data = json.load(f)

            logging.info(f"Loaded mock data with {len(data.get('earthquakes', []))} earthquakes")
            return data
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing mock data: {e}")
            return None
        except Exception as e:
            logging.error(f"Error loading mock data: {e}")
            return None

def run_single_test():
    """Run a single test iteration"""
    print("\n" + "="*60)
    print("TESTING TREMR")
    print("="*60)

    # Clear previous test data
    if os.path.exists('seen_earthquakes.json'):
        os.remove('seen_earthquakes.json')
        print("Cleared previous test data")

    # Create test monitor
    monitor = TestEarthquakeMonitor()

    # Show configuration
    print(f"\nTest Configuration:")
    print(f"  Your Location: {monitor.config['latitude']}, {monitor.config['longitude']}")
    print(f"  Alert Radius: {monitor.config['radius_km']} km")
    print(f"  Min Magnitude: {monitor.config['min_magnitude']}")
    print("\n" + "-"*60)

    # Fetch and process mock data
    data = monitor.fetch_earthquake_data()

    if data:
        print(f"\nProcessing {len(data['earthquakes'])} mock earthquakes...\n")

        # Analyze each earthquake
        for i, earthquake in enumerate(data['earthquakes'], 1):
            lat = float(earthquake.get('latitude', 0))
            lon = float(earthquake.get('longitude', 0))
            magnitude = float(earthquake.get('magnitude', 0))
            distance = monitor.calculate_distance(lat, lon)

            print(f"Earthquake #{i}:")
            print(f"  Location: {earthquake.get('location', 'Unknown')}")
            print(f"  Magnitude: {magnitude}")
            print(f"  Distance: {distance:.1f} km")
            print(f"  Time: {earthquake.get('date')} {earthquake.get('time')}")

            # Check if it would trigger notification
            if (distance <= monitor.config['radius_km'] and
                magnitude >= monitor.config['min_magnitude']):
                print(f"  [+] WOULD TRIGGER ALERT (within {monitor.config['radius_km']}km and >= {monitor.config['min_magnitude']} magnitude)")
            else:
                if distance > monitor.config['radius_km']:
                    print(f"  [-] Too far (outside {monitor.config['radius_km']}km radius)")
                if magnitude < monitor.config['min_magnitude']:
                    print(f"  [-] Too weak (below {monitor.config['min_magnitude']} magnitude threshold)")
            print()

        # Process earthquakes (this will show notifications)
        print("-"*60)
        print("\nProcessing earthquakes (notifications will appear)...\n")
        monitor.process_earthquakes(data)

        print("-"*60)
        print("\n[+] Test completed!")
        print(f"\nCheck earthquake_monitor.log for detailed logs")
        print("\nTo test again with notifications, delete 'seen_earthquakes.json'")
        print("and run this script again.")

    else:
        print("[!] Failed to load mock data")

    print("\n" + "="*60 + "\n")

def create_custom_mock_data():
    """Helper function to create custom mock earthquake near your location"""
    print("\n" + "="*60)
    print("CREATE CUSTOM MOCK EARTHQUAKE")
    print("="*60)

    try:
        # Load current config
        with open('config.json', 'r') as f:
            config = json.load(f)

        user_lat = config['latitude']
        user_lon = config['longitude']

        print(f"\nYour configured location: {user_lat}, {user_lon}")
        print("\nEnter earthquake details (or press Enter for default):")

        # Get user input
        lat = input(f"Latitude [{user_lat}]: ").strip() or str(user_lat)
        lon = input(f"Longitude [{user_lon}]: ").strip() or str(user_lon)
        magnitude = input("Magnitude [5.0]: ").strip() or "5.0"
        location = input("Location description [Test Location]: ").strip() or "Test Location"
        depth = input("Depth [010 kilometers]: ").strip() or "010 kilometers"

        from datetime import datetime
        now = datetime.now()

        custom_data = {
            "earthquakes": [
                {
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "latitude": lat,
                    "longitude": lon,
                    "depth": depth,
                    "magnitude": magnitude,
                    "location": location
                }
            ]
        }

        # Save to custom file
        with open('custom_mock_data.json', 'w') as f:
            json.dump(custom_data, f, indent=4)

        print(f"\n[+] Created custom_mock_data.json")
        print("\nTo test with this data, run:")
        print("  python test_monitor.py custom")

    except Exception as e:
        print(f"[!] Error: {e}")

    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'custom':
            # Test with custom mock data
            if os.path.exists('custom_mock_data.json'):
                if os.path.exists('seen_earthquakes.json'):
                    os.remove('seen_earthquakes.json')
                monitor = TestEarthquakeMonitor(mock_file='custom_mock_data.json')
                data = monitor.fetch_earthquake_data()
                if data:
                    monitor.process_earthquakes(data)
                print("\n[+] Custom test completed!\n")
            else:
                print("[!] custom_mock_data.json not found. Run: python test_monitor.py create")

        elif sys.argv[1] == 'create':
            # Create custom mock data
            create_custom_mock_data()

        elif sys.argv[1] == 'help':
            print("\nUsage:")
            print("  python test_monitor.py         - Run test with default mock data")
            print("  python test_monitor.py custom  - Run test with custom mock data")
            print("  python test_monitor.py create  - Create custom mock earthquake data")
            print("  python test_monitor.py help    - Show this help\n")
    else:
        # Run default test
        run_single_test()
