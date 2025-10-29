"""
Setup script for Tremr
Installs dependencies and creates necessary files
"""

import subprocess
import sys
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")

    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✓ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        return False

def create_icon():
    """Create the earthquake warning icon"""
    print_header("Creating Earthquake Warning Icon")

    if os.path.exists('earthquake_warning.png'):
        print("Icon already exists, skipping creation.")
        return True

    try:
        import create_icon
        create_icon.create_earthquake_icon()
        print("\n✓ Earthquake warning icon created!")
        return True
    except Exception as e:
        print(f"\n⚠ Could not create icon: {e}")
        print("The app will create it automatically on first run.")
        return True  # Not a critical error

def test_notification():
    """Test if notifications work"""
    print_header("Testing Notification System")

    try:
        from plyer import notification
        print("Sending test notification...")

        notification.notify(
            title="Test Notification",
            message="If you see this, notifications are working!",
            app_name='Tremr',
            timeout=5
        )
        print("\n✓ Test notification sent!")
        print("Did you see the notification popup?")
        return True
    except Exception as e:
        print(f"\n⚠ Could not send test notification: {e}")
        print("Notifications might not work on your system.")
        return False

def main():
    """Run setup"""
    print_header("Tremr - Setup")

    print("This script will:")
    print("1. Install required dependencies")
    print("2. Create the earthquake warning icon")
    print("3. Test the notification system")
    print()

    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation.")
        return False

    # Step 2: Create icon
    create_icon()

    # Step 3: Test notification
    test_notification()

    # Final message
    print_header("Setup Complete!")
    print("✓ Tremr is ready to use!")
    print()
    print("Next steps:")
    print("1. Edit config.json to set your location")
    print("2. Run: python main.py")
    print("   or double-click: start_listener.bat")
    print()
    print("To test with mock data:")
    print("  python test_monitor.py")
    print("  or double-click: run_test.bat")
    print()

    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")
