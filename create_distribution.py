"""
Create Distribution Package
Packages Tremr for easy distribution to other systems
"""

import os
import shutil
from pathlib import Path
import zipfile
from datetime import datetime

def create_distribution_package():
    """Create a distribution package"""

    print("="*70)
    print("  CREATING DISTRIBUTION PACKAGE")
    print("="*70)

    # Get current directory
    source_dir = Path(__file__).parent

    # Create distribution folder name
    version = datetime.now().strftime("%Y%m%d")
    dist_name = f"Tremr_v{version}"
    dist_dir = source_dir / "dist" / dist_name

    # Create dist directory
    print(f"\nCreating distribution folder: {dist_name}")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # List of files to include
    files_to_include = [
        # Core application files
        'gui.py',
        'main.py',
        'phivolcs_scraper.py',

        # Configuration and data
        'requirements.txt',
        'config.json',
        'mock_data.json',

        # Installation files
        'install.py',
        'Launch_Tremr.bat',
        'INSTALL.txt',

        # Test files
        'test_monitor.py',
        'test_full_system.py',

        # Documentation
        'README.md',
        'QUICKSTART.md',
        'OVERVIEW.md',
    ]

    # Copy files
    print("\nCopying files:")
    copied_count = 0
    for filename in files_to_include:
        src_file = source_dir / filename
        if src_file.exists():
            dst_file = dist_dir / filename
            shutil.copy2(src_file, dst_file)
            print(f"  [+] {filename}")
            copied_count += 1
        else:
            print(f"  [-] {filename} (not found, skipping)")

    # Create a README for the distribution
    readme_content = f"""
================================================================================
  TREMR - Distribution Package
  Version: {version}
  Earthquake Early Warning System
================================================================================

CONTENTS OF THIS PACKAGE
================================================================================

Core Application:
  - gui.py                  Main application GUI
  - main.py                 Core earthquake monitoring logic
  - phivolcs_scraper.py     PHIVOLCS data fetcher

Installation:
  - install.py              Automated installer
  - Launch_Tremr.bat   Quick launcher
  - INSTALL.txt             Installation instructions
  - requirements.txt        Python dependencies

Configuration:
  - config.json             Default configuration
  - mock_data.json          Test data

Testing:
  - test_monitor.py         Test with mock data
  - test_full_system.py     Comprehensive system test

Documentation:
  - README.md               Full documentation
  - QUICKSTART.md           Quick start guide
  - OVERVIEW.md             System overview


INSTALLATION INSTRUCTIONS
================================================================================

STEP 1: Install Python
   - Download Python 3.8+ from https://www.python.org/downloads/
   - IMPORTANT: Check "Add Python to PATH" during installation

STEP 2: Run Installer
   - Double-click "install.py"
   - OR run in command prompt: python install.py

STEP 3: Launch Application
   - Use the desktop shortcut
   - OR double-click "Launch_Tremr.bat"

STEP 4: Configure
   - Set your location
   - Adjust alert settings
   - Click "Start Monitoring"


QUICK START
================================================================================

For systems with Python already installed:

1. Extract this folder
2. Double-click "Launch_Tremr.bat"
3. If prompted, run "install.py" first


SYSTEM REQUIREMENTS
================================================================================

- Windows 7 or higher
- Python 3.8 or higher
- Internet connection
- 100 MB free disk space


FEATURES
================================================================================

[+] Real-time PHIVOLCS earthquake monitoring
[+] Desktop notifications with sound alerts
[+] System tray operation
[+] Auto-start on Windows boot
[+] Single instance (no duplicate alerts)
[+] Connection status indicator
[+] Customizable alert radius and magnitude


SUPPORT
================================================================================

- Read INSTALL.txt for detailed installation help
- Run test_full_system.py to verify installation
- Check earthquake_monitor.log for error messages


SAFETY NOTICE
================================================================================

This application monitors PHIVOLCS earthquake data and provides early warnings.
Keep it running 24/7 for continuous protection.

Always follow official emergency procedures during earthquakes.


Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================================================
"""

    # Write distribution README (with UTF-8 encoding)
    with open(dist_dir / "README_DISTRIBUTION.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"  [+] README_DISTRIBUTION.txt")

    # Create ZIP file
    zip_path = dist_dir.parent / f"{dist_name}.zip"
    print(f"\nCreating ZIP archive: {zip_path.name}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, arc_name)
                print(f"  [+] {arc_name}")

    # Calculate size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)

    print("\n" + "="*70)
    print("  DISTRIBUTION PACKAGE CREATED!")
    print("="*70)
    print(f"\nPackage: {zip_path}")
    print(f"Size: {zip_size_mb:.2f} MB")
    print(f"Files included: {copied_count + 1}")  # +1 for README_DISTRIBUTION

    print("\n" + "="*70)
    print("  READY FOR DISTRIBUTION")
    print("="*70)
    print("\nYou can now share this package with others:")
    print(f"  1. Share the ZIP file: {zip_path.name}")
    print("  2. Or share the folder: {dist_name}")
    print("\nRecipients just need to:")
    print("  1. Extract the package")
    print("  2. Run install.py")
    print("  3. Launch the application")
    print("\n" + "="*70)

    return True


if __name__ == '__main__':
    try:
        create_distribution_package()
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n[ERROR] Failed to create distribution: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
