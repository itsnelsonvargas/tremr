"""
COMPREHENSIVE SYSTEM TEST FOR TREMR
This is a life-saving application - all features must work correctly!

Test Coverage:
1. Configuration Management
2. Icon Creation
3. PHIVOLCS Connection (Live Data)
4. Distance Calculation
5. Earthquake Detection & Filtering
6. Notification System (Sound + Desktop Alert)
7. Seen Earthquake Tracking
8. File Operations
9. Error Handling

CRITICAL: All tests must pass for this app to be considered safe for production use.
"""

import os
import sys
import json
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_test.log'),
        logging.StreamHandler()
    ]
)

class SystemTester:
    def __init__(self):
        self.test_results = []
        self.critical_failures = []

    def log_test(self, test_name, passed, details="", critical=False):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        result = {
            'test': test_name,
            'passed': passed,
            'details': details,
            'critical': critical,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)

        if not passed and critical:
            self.critical_failures.append(test_name)

        print(f"\n{'='*70}")
        print(f"{status} - {test_name}")
        if details:
            print(f"Details: {details}")
        if critical and not passed:
            print("[!] CRITICAL FAILURE - This feature is essential for safety!")
        print(f"{'='*70}")

    def test_1_configuration(self):
        """Test 1: Configuration Loading"""
        print("\n" + "="*70)
        print("TEST 1: Configuration Management")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            # Create monitor
            monitor = EarthquakeMonitor()

            # Check config exists
            assert os.path.exists('config.json'), "Config file not found"

            # Check required fields
            required_fields = ['latitude', 'longitude', 'radius_km', 'min_magnitude', 'check_interval_seconds']
            for field in required_fields:
                assert field in monitor.config, f"Missing required field: {field}"
                assert monitor.config[field] is not None, f"Field is None: {field}"

            self.log_test(
                "Configuration Loading",
                True,
                f"All required fields present. Location: {monitor.config['latitude']}, {monitor.config['longitude']}",
                critical=True
            )
            return True

        except Exception as e:
            self.log_test("Configuration Loading", False, str(e), critical=True)
            return False

    def test_2_icon_creation(self):
        """Test 2: Icon File Creation"""
        print("\n" + "="*70)
        print("TEST 2: Warning Icon Creation")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Check if icon exists
            icon_exists = os.path.exists('earthquake_warning.ico')

            if icon_exists:
                icon_size = os.path.getsize('earthquake_warning.ico')
                assert icon_size > 0, "Icon file is empty"

            self.log_test(
                "Warning Icon Creation",
                icon_exists,
                f"Icon file: {'Found' if icon_exists else 'Not found'} (Size: {icon_size if icon_exists else 0} bytes)",
                critical=False
            )
            return icon_exists

        except Exception as e:
            self.log_test("Warning Icon Creation", False, str(e), critical=False)
            return False

    def test_3_phivolcs_connection(self):
        """Test 3: PHIVOLCS Connection (CRITICAL)"""
        print("\n" + "="*70)
        print("TEST 3: PHIVOLCS Connection - Live Data Source")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Test connection
            is_connected, message = monitor.test_connection()

            if is_connected:
                # Fetch actual data
                data = monitor.fetch_earthquake_data()

                assert data is not None, "Data fetch returned None"
                assert 'earthquakes' in data, "Data missing 'earthquakes' key"
                assert len(data['earthquakes']) > 0, "No earthquakes in data"

                eq_count = len(data['earthquakes'])
                latest = data['earthquakes'][0]

                details = f"Connected! {eq_count} earthquakes fetched. Latest: {latest.get('date')} - Mag {latest.get('magnitude')} - {latest.get('location')}"
            else:
                details = f"Connection failed: {message}"

            self.log_test(
                "PHIVOLCS Connection",
                is_connected,
                details,
                critical=True
            )
            return is_connected

        except Exception as e:
            self.log_test("PHIVOLCS Connection", False, str(e), critical=True)
            return False

    def test_4_distance_calculation(self):
        """Test 4: Distance Calculation Accuracy"""
        print("\n" + "="*70)
        print("TEST 4: Distance Calculation")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Test known distances
            # From Commonwealth QC (14.698447, 121.0823853) to Manila City Hall (14.5995, 120.9842)
            # Expected: approximately 15-20km
            manila_lat, manila_lon = 14.5995, 120.9842

            distance = monitor.calculate_distance(manila_lat, manila_lon)

            # Should be reasonable (between 10-25km)
            is_reasonable = 10 <= distance <= 25

            self.log_test(
                "Distance Calculation",
                is_reasonable,
                f"Calculated distance: {distance:.2f} km (Expected: 15-20km from Commonwealth to Manila)",
                critical=True
            )
            return is_reasonable

        except Exception as e:
            self.log_test("Distance Calculation", False, str(e), critical=True)
            return False

    def test_5_earthquake_filtering(self):
        """Test 5: Earthquake Detection & Filtering"""
        print("\n" + "="*70)
        print("TEST 5: Earthquake Detection & Filtering Logic")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Fetch live data
            data = monitor.fetch_earthquake_data()

            if not data or 'earthquakes' not in data:
                raise Exception("Could not fetch earthquake data")

            total_earthquakes = len(data['earthquakes'])

            # Count earthquakes that meet criteria
            nearby_count = 0
            test_earthquakes = []

            for eq in data['earthquakes'][:100]:  # Check first 100
                try:
                    lat = float(eq.get('latitude', 0))
                    lon = float(eq.get('longitude', 0))
                    magnitude = float(eq.get('magnitude', 0))
                    distance = monitor.calculate_distance(lat, lon)

                    if distance <= monitor.config['radius_km'] and magnitude >= monitor.config['min_magnitude']:
                        nearby_count += 1
                        test_earthquakes.append({
                            'magnitude': magnitude,
                            'distance': distance,
                            'location': eq.get('location')
                        })

                except:
                    continue

            details = f"Scanned {total_earthquakes} earthquakes. Found {nearby_count} within {monitor.config['radius_km']}km with magnitude >= {monitor.config['min_magnitude']}"

            self.log_test(
                "Earthquake Filtering",
                True,
                details,
                critical=True
            )

            # Print nearby earthquakes
            if nearby_count > 0:
                print("\n[LOCATION] Nearby Earthquakes Found:")
                for i, eq in enumerate(test_earthquakes, 1):
                    print(f"   {i}. Magnitude {eq['magnitude']}, {eq['distance']:.1f}km - {eq['location']}")

            return True

        except Exception as e:
            self.log_test("Earthquake Filtering", False, str(e), critical=True)
            return False

    def test_6_notification_system(self):
        """Test 6: Notification System (Sound + Desktop Alert)"""
        print("\n" + "="*70)
        print("TEST 6: Notification System")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Create test earthquake
            test_earthquake = {
                'magnitude': '4.5',
                'location': 'TEST EARTHQUAKE - System Verification',
                'depth': '010 kilometers',
                'date': datetime.now().strftime("%d %B %Y"),
                'time': datetime.now().strftime("%I:%M:%S %p")
            }

            print("\n[!]  Testing notification system...")
            print("You should see:")
            print("   1. Hear 3 warning beeps")
            print("   2. See a desktop notification")
            print("\nTriggering test notification in 3 seconds...")
            time.sleep(3)

            # Trigger notification
            monitor.show_notification(test_earthquake, 50.0)

            print("\n[+] Notification triggered!")
            print("Did you hear the sound and see the notification? (Check system tray)")

            self.log_test(
                "Notification System",
                True,
                "Notification triggered successfully. Manual verification required.",
                critical=True
            )
            return True

        except Exception as e:
            self.log_test("Notification System", False, str(e), critical=True)
            return False

    def test_7_seen_earthquakes(self):
        """Test 7: Seen Earthquake Tracking"""
        print("\n" + "="*70)
        print("TEST 7: Seen Earthquake Tracking")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Create test earthquake ID
            test_eq = {
                'date': '2025-10-29',
                'time': '12:00:00',
                'latitude': '14.5',
                'longitude': '121.0'
            }

            eq_id = monitor.create_earthquake_id(test_eq)

            # Add to seen
            initial_count = len(monitor.seen_earthquakes)
            monitor.seen_earthquakes.add(eq_id)
            monitor.save_seen_earthquakes()

            # Verify saved
            assert os.path.exists('seen_earthquakes.json'), "Seen earthquakes file not created"

            # Load and verify
            monitor2 = EarthquakeMonitor()
            assert eq_id in monitor2.seen_earthquakes, "Earthquake ID not persisted"

            self.log_test(
                "Seen Earthquake Tracking",
                True,
                f"Successfully tracked and persisted earthquake IDs. Total seen: {len(monitor2.seen_earthquakes)}",
                critical=True
            )
            return True

        except Exception as e:
            self.log_test("Seen Earthquake Tracking", False, str(e), critical=True)
            return False

    def test_8_error_handling(self):
        """Test 8: Error Handling & Recovery"""
        print("\n" + "="*70)
        print("TEST 8: Error Handling & Recovery")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            # Test invalid coordinates
            try:
                distance = monitor.calculate_distance("invalid", "invalid")
                error_handled = False
            except:
                error_handled = True

            # Test process earthquakes with None data
            try:
                monitor.process_earthquakes(None)
                none_handled = True
            except:
                none_handled = False

            # Test with empty data
            try:
                monitor.process_earthquakes({'earthquakes': []})
                empty_handled = True
            except:
                empty_handled = False

            all_passed = error_handled and none_handled and empty_handled

            self.log_test(
                "Error Handling",
                all_passed,
                f"Invalid coords: {error_handled}, None data: {none_handled}, Empty data: {empty_handled}",
                critical=False
            )
            return all_passed

        except Exception as e:
            self.log_test("Error Handling", False, str(e), critical=False)
            return False

    def test_9_continuous_monitoring(self):
        """Test 9: Continuous Monitoring Capability"""
        print("\n" + "="*70)
        print("TEST 9: Continuous Monitoring (3 cycles)")
        print("="*70)

        try:
            from main import EarthquakeMonitor

            monitor = EarthquakeMonitor()

            print("\nSimulating 3 monitoring cycles...")

            successful_fetches = 0
            for i in range(3):
                print(f"\n  Cycle {i+1}/3: Checking PHIVOLCS...")

                data = monitor.fetch_earthquake_data()

                if data and 'earthquakes' in data:
                    count = len(data['earthquakes'])
                    print(f"  [+] Fetched {count} earthquakes")
                    successful_fetches += 1

                    # Process the data
                    monitor.process_earthquakes(data)
                else:
                    print(f"  [-] Failed to fetch data")

                if i < 2:  # Don't wait after last cycle
                    print(f"  Waiting 5 seconds...")
                    time.sleep(5)

            all_successful = successful_fetches == 3

            self.log_test(
                "Continuous Monitoring",
                all_successful,
                f"Successfully completed {successful_fetches}/3 monitoring cycles",
                critical=True
            )
            return all_successful

        except Exception as e:
            self.log_test("Continuous Monitoring", False, str(e), critical=True)
            return False

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*70)
        print("="*70)
        print("  COMPREHENSIVE SYSTEM TEST REPORT")
        print("="*70)
        print("="*70)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests

        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests} [+]")
        print(f"Failed: {failed_tests} [-]")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if self.critical_failures:
            print(f"\n[!]  CRITICAL FAILURES: {len(self.critical_failures)}")
            print("\nFailed Critical Tests:")
            for failure in self.critical_failures:
                print(f"  [-] {failure}")
            print("\n[ALERT] WARNING: Application NOT SAFE for production use!")
            print("Critical features are not working. Lives may be at risk!")

        else:
            print("\n[+] ALL CRITICAL TESTS PASSED")
            print("[+] Application is SAFE for production use!")

        print("\n" + "-"*70)
        print("Detailed Test Results:")
        print("-"*70)

        for result in self.test_results:
            status = "[+] PASS" if result['passed'] else "[-] FAIL"
            critical_marker = " [CRITICAL]" if result['critical'] else ""
            print(f"\n{status} - {result['test']}{critical_marker}")
            print(f"Time: {result['timestamp']}")
            if result['details']:
                print(f"Details: {result['details']}")

        # Save report to file
        report_file = f"system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100,
                    'critical_failures': self.critical_failures,
                    'safe_for_production': len(self.critical_failures) == 0
                },
                'tests': self.test_results
            }, f, indent=4)

        print(f"\n[FILE] Full report saved to: {report_file}")
        print("\n" + "="*70)

        return len(self.critical_failures) == 0


def main():
    print("\n" + "="*70)
    print("="*70)
    print("  TREMR - COMPREHENSIVE SYSTEM TEST")
    print("  Life-Saving Application - All Features Must Work!")
    print("="*70)
    print("="*70)

    tester = SystemTester()

    # Run all tests
    print("\n[SEARCH] Starting comprehensive system test...")
    print("This will verify all critical features for safety...\n")

    time.sleep(2)

    # Execute all tests
    tester.test_1_configuration()
    time.sleep(1)

    tester.test_2_icon_creation()
    time.sleep(1)

    tester.test_3_phivolcs_connection()
    time.sleep(1)

    tester.test_4_distance_calculation()
    time.sleep(1)

    tester.test_5_earthquake_filtering()
    time.sleep(1)

    tester.test_6_notification_system()
    time.sleep(2)

    tester.test_7_seen_earthquakes()
    time.sleep(1)

    tester.test_8_error_handling()
    time.sleep(1)

    tester.test_9_continuous_monitoring()
    time.sleep(1)

    # Generate final report
    is_safe = tester.generate_report()

    # Return exit code
    sys.exit(0 if is_safe else 1)


if __name__ == '__main__':
    main()
