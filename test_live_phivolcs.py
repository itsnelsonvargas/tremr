"""
Test script to verify live PHIVOLCS data fetching
"""

from main import EarthquakeMonitor
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("="*60)
print("Testing Live PHIVOLCS Connection")
print("="*60)

# Create monitor
monitor = EarthquakeMonitor()

# Test connection
print("\n1. Testing connection...")
is_connected, message = monitor.test_connection()
print(f"   Status: {'CONNECTED' if is_connected else 'DISCONNECTED'}")
print(f"   Message: {message}")

# Fetch earthquake data
print("\n2. Fetching earthquake data...")
data = monitor.fetch_earthquake_data()

if data and 'earthquakes' in data:
    earthquakes = data['earthquakes']
    print(f"   Found {len(earthquakes)} earthquakes")

    print("\n3. Latest 5 earthquakes:")
    for i, eq in enumerate(earthquakes[:5], 1):
        print(f"\n   Earthquake #{i}:")
        print(f"   - Date/Time: {eq.get('date')} {eq.get('time')}")
        print(f"   - Location: {eq.get('location')}")
        print(f"   - Magnitude: {eq.get('magnitude')}")
        print(f"   - Coordinates: {eq.get('latitude')}, {eq.get('longitude')}")
        print(f"   - Depth: {eq.get('depth')}")

        # Calculate distance
        try:
            lat = float(eq.get('latitude', 0))
            lon = float(eq.get('longitude', 0))
            distance = monitor.calculate_distance(lat, lon)
            print(f"   - Distance from you: {distance:.1f} km")
        except:
            print(f"   - Distance: Could not calculate")

    print(f"\n4. Checking for nearby earthquakes (within {monitor.config['radius_km']}km)...")
    nearby_count = 0
    for eq in earthquakes:
        try:
            lat = float(eq.get('latitude', 0))
            lon = float(eq.get('longitude', 0))
            magnitude = float(eq.get('magnitude', 0))
            distance = monitor.calculate_distance(lat, lon)

            if distance <= monitor.config['radius_km'] and magnitude >= monitor.config['min_magnitude']:
                nearby_count += 1
                print(f"   - Found: Magnitude {magnitude}, {distance:.1f}km away - {eq.get('location')}")
        except:
            continue

    if nearby_count == 0:
        print(f"   - No earthquakes found within {monitor.config['radius_km']}km with magnitude >= {monitor.config['min_magnitude']}")
    else:
        print(f"\n   Total nearby earthquakes: {nearby_count}")

else:
    print("   ERROR: Could not fetch earthquake data")

print("\n" + "="*60)
print("Test Complete")
print("="*60)
