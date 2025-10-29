"""
Tremr - Easy Installer
Automated installation script for Windows

This script will:
1. Check Python version
2. Install all required dependencies
3. Create desktop shortcut
4. Create Start Menu shortcut
5. Test the installation
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(step, text):
    """Print a step"""
    print(f"\n[STEP {step}] {text}")

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python version...")

    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro} detected")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   [ERROR] Python 3.8 or higher is required!")
        print("   Please install Python 3.8+ from https://www.python.org/downloads/")
        return False

    print("   [OK] Python version is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print_step(2, "Installing dependencies...")

    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("   [ERROR] requirements.txt not found!")
        return False

    try:
        print("   Installing packages (this may take a few minutes)...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("   [OK] All dependencies installed successfully")
            return True
        else:
            print(f"   [ERROR] Installation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"   [ERROR] Failed to install dependencies: {e}")
        return False

def create_shortcut(target, shortcut_path, description, icon_path=None):
    """Create a Windows shortcut"""
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(target)
        shortcut.WorkingDirectory = str(Path(target).parent)
        shortcut.Description = description
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = str(icon_path)
        shortcut.save()
        return True
    except ImportError:
        # pywin32 not installed, try alternative method
        try:
            import winshell
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(target)
            shortcut.WorkingDirectory = str(Path(target).parent)
            shortcut.Description = description
            if icon_path and os.path.exists(icon_path):
                shortcut.IconLocation = str(icon_path)
            shortcut.save()
            return True
        except:
            return False
    except Exception as e:
        print(f"   Warning: Could not create shortcut: {e}")
        return False

def create_batch_launcher():
    """Create a batch file to launch the application"""
    print_step(3, "Creating launcher...")

    app_dir = Path(__file__).parent
    batch_file = app_dir / "Launch_The_Big_One_Listener.bat"

    batch_content = f"""@echo off
title Tremr
cd /d "{app_dir}"
start "" pythonw.exe gui.py
"""

    try:
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        print(f"   [OK] Created launcher: {batch_file.name}")
        return batch_file
    except Exception as e:
        print(f"   [ERROR] Failed to create launcher: {e}")
        return None

def create_shortcuts(launcher_path):
    """Create desktop and start menu shortcuts"""
    print_step(4, "Creating shortcuts...")

    if not launcher_path or not launcher_path.exists():
        print("   [SKIP] No launcher to create shortcuts for")
        return False

    app_dir = Path(__file__).parent
    icon_path = app_dir / "earthquake_warning.ico"

    success_count = 0

    # Desktop shortcut
    try:
        desktop = Path.home() / "Desktop"
        desktop_shortcut = desktop / "Tremr.lnk"

        if create_shortcut(
            launcher_path,
            desktop_shortcut,
            "Earthquake Early Warning System",
            icon_path if icon_path.exists() else None
        ):
            print(f"   [OK] Desktop shortcut created")
            success_count += 1
        else:
            print(f"   [SKIP] Could not create desktop shortcut (pywin32 not installed)")
    except Exception as e:
        print(f"   [SKIP] Desktop shortcut: {e}")

    # Start Menu shortcut
    try:
        start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        start_menu_shortcut = start_menu / "Tremr.lnk"

        if create_shortcut(
            launcher_path,
            start_menu_shortcut,
            "Earthquake Early Warning System",
            icon_path if icon_path.exists() else None
        ):
            print(f"   [OK] Start Menu shortcut created")
            success_count += 1
        else:
            print(f"   [SKIP] Could not create Start Menu shortcut")
    except Exception as e:
        print(f"   [SKIP] Start Menu shortcut: {e}")

    return success_count > 0

def test_installation():
    """Test if the installation was successful"""
    print_step(5, "Testing installation...")

    try:
        # Try importing all required modules
        print("   Checking dependencies...")

        modules = [
            ('requests', 'HTTP requests'),
            ('geopy', 'Geographic calculations'),
            ('plyer', 'Desktop notifications'),
            ('PIL', 'Image processing'),
            ('pystray', 'System tray'),
            ('bs4', 'Web scraping'),
            ('psutil', 'Process management')
        ]

        all_ok = True
        for module_name, description in modules:
            try:
                __import__(module_name)
                print(f"   [OK] {description} ({module_name})")
            except ImportError:
                print(f"   [FAIL] {description} ({module_name}) - Not installed!")
                all_ok = False

        if all_ok:
            print("\n   [OK] All dependencies are working correctly!")
            return True
        else:
            print("\n   [ERROR] Some dependencies are missing!")
            return False

    except Exception as e:
        print(f"   [ERROR] Test failed: {e}")
        return False

def main():
    """Main installation process"""
    print_header("TREMR - INSTALLER")
    print("Automated Installation for Windows")
    print("\nThis will install and configure the earthquake monitoring system.")

    # Check if running on Windows
    if platform.system() != 'Windows':
        print("\n[ERROR] This installer is designed for Windows only.")
        input("\nPress Enter to exit...")
        return False

    # Step 1: Check Python
    if not check_python_version():
        input("\nPress Enter to exit...")
        return False

    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n[ERROR] Installation failed!")
        input("\nPress Enter to exit...")
        return False

    # Step 3: Create launcher
    launcher = create_batch_launcher()

    # Step 4: Create shortcuts
    create_shortcuts(launcher)

    # Step 5: Test installation
    if not test_installation():
        print("\n[WARNING] Installation completed with errors.")
        print("The application may not work correctly.")
    else:
        print_header("INSTALLATION COMPLETE!")
        print("\n[SUCCESS] Tremr is ready to use!")
        print("\nHow to start:")
        print("  1. Double-click 'Launch_The_Big_One_Listener.bat'")
        print("  2. Or use the desktop shortcut")
        print("  3. Or find it in your Start Menu")
        print("\nWhat's next:")
        print("  1. Configure your location in the app")
        print("  2. Set your alert radius and magnitude threshold")
        print("  3. Click 'Start Monitoring' to begin")
        print("\nThe app will run in the background and alert you of nearby earthquakes.")

    input("\nPress Enter to exit...")
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Installation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
