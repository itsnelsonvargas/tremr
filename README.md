<div align="center">
  <img src="tremr_logo.png" alt="Tremr Logo" width="200"/>
  <h1>Tremr</h1>
</div>

A Python application that monitors PHIVOLCS (Philippine Institute of Volcanology and Seismology) earthquake data in real-time and sends desktop notifications when nearby earthquakes occur.

## ⚡ Quick Start (GUI)

**Easiest way to use:**
1. Double-click `setup.bat` (first time only)
2. Double-click `start_gui.bat`
3. Enter your address and click "Search"
4. Click "▶ Start Monitoring"

See [GUI_GUIDE.md](GUI_GUIDE.md) for detailed GUI instructions.

## Features

### GUI Application
- ✨ **Modern, professional interface** with enhanced UI/UX
- 🎨 **Beautiful card-based layout** with smooth animations
- 🖱️ **Interactive hover effects** on all buttons
- 📍 **Smart address search** - Type any address, no need for coordinates
- 🚀 **Auto-start on boot** - Start monitoring when computer starts
- ⚫ **Animated status indicator** with color-coded states
- 📋 **Real-time activity log** with emoji indicators
- ⚙️ **Easy configuration** - All settings in one clean interface
- 🎯 **Larger window (600x750)** - More space, better visibility

See [UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md) for detailed UI enhancements.

### Monitoring & Alerts
- Real-time monitoring of PHIVOLCS earthquake data
- Desktop popup notifications for nearby earthquakes
- **Bright, eye-catching earthquake warning icon**
- **Urgent warning sound alerts** (triple beep on Windows)
- Configurable location, radius, and magnitude thresholds
- Runs in the background
- Prevents duplicate notifications
- Detailed logging

## Requirements

- Python 3.7 or higher
- Internet connection

## Installation

### Easy Setup (Recommended)

Double-click `setup.bat` - This will automatically:
- Install all required dependencies
- Create the earthquake warning icon
- Test the notification system

### Manual Setup

1. Open Command Prompt or PowerShell and navigate to the project directory:
```bash
cd C:\Users\user\Desktop\tremr
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Create the warning icon:
```bash
python create_icon.py
```

## Configuration

Edit the `config.json` file to customize your settings:

```json
{
    "latitude": 14.5995,         // Your location latitude (default: Manila)
    "longitude": 120.9842,       // Your location longitude
    "radius_km": 100,            // Alert radius in kilometers
    "min_magnitude": 3.0,        // Minimum earthquake magnitude to alert
    "check_interval_seconds": 60, // How often to check for updates
    "phivolcs_url": "..."        // PHIVOLCS data source
}
```

### How to Find Your Coordinates

1. Go to [Google Maps](https://www.google.com/maps)
2. Right-click on your location
3. Click on the coordinates to copy them
4. Update `latitude` and `longitude` in `config.json`

### Configuration Options

- **latitude/longitude**: Your location coordinates
- **radius_km**: Distance in kilometers - earthquakes within this radius will trigger alerts
- **min_magnitude**: Minimum earthquake magnitude (Richter scale) to notify about
- **check_interval_seconds**: How often to check PHIVOLCS for new data (default: 60 seconds)

## Usage

### Running the Application

```bash
python main.py
```

The application will:
1. Start monitoring PHIVOLCS earthquake data
2. Check for new earthquakes every 60 seconds (configurable)
3. Show a popup notification when a nearby earthquake occurs
4. Log all activity to `earthquake_monitor.log`

### Running in Background (Windows)

To run the application in the background without keeping a console window open:

1. Create a batch file `start_listener.bat`:
```batch
@echo off
start /B pythonw main.py
```

2. Run the batch file by double-clicking it

### Stopping the Application

- If running in console: Press `Ctrl+C`
- If running in background: Use Task Manager to end the Python process

## Files

- `main.py` - Main application code
- `config.json` - Configuration file (auto-created on first run)
- `requirements.txt` - Python dependencies
- `setup.bat` / `setup.py` - Easy installation script
- `create_icon.py` - Creates the earthquake warning icon
- `test_monitor.py` - Test script with mock data
- `run_test.bat` - Easy testing
- `earthquake_monitor.log` - Log file (auto-created)
- `seen_earthquakes.json` - Tracks processed earthquakes (auto-created)
- `earthquake_warning.png` - Warning icon (auto-created)

## Notification Example

When a nearby earthquake is detected, you'll:
1. **Hear** an urgent triple-beep warning sound
2. **See** a bright popup notification with red warning icon

```
🚨 EARTHQUAKE ALERT - Magnitude 4.5

Location: 005 km S 52° W of Nasugbu (Batangas)
Distance: 45.2 km away
Depth: 075 kilometers
Time: 2025-10-28 14:30:45
```

The notification includes:
- **Visual**: Bright red/orange warning icon with exclamation mark
- **Audio**: Triple-beep warning sound (system alert sound on Windows)
- **Details**: Location, distance, depth, and time of earthquake

## Troubleshooting

### No notifications appearing

1. Check that the application is running
2. Verify your coordinates in `config.json` are correct
3. Check if `radius_km` is large enough
4. Lower `min_magnitude` to receive alerts for smaller earthquakes
5. Check `earthquake_monitor.log` for errors

### "ModuleNotFoundError"

Run: `pip install -r requirements.txt`

### Connection errors

- Check your internet connection
- PHIVOLCS server might be temporarily unavailable
- The application will retry automatically

## Data Source

This application uses real-time earthquake data from:
- PHIVOLCS (Philippine Institute of Volcanology and Seismology)
- Official website: https://www.phivolcs.dost.gov.ph/

## Notes

- First run will create all necessary configuration files
- The app remembers earthquakes it has already notified you about
- Logs are saved to `earthquake_monitor.log` for troubleshooting
- The app only notifies once per earthquake event

## Safety Information

This is an informational tool. For official earthquake alerts and safety information, always refer to:
- PHIVOLCS official website: https://www.phivolcs.dost.gov.ph/
- NDRRMC (National Disaster Risk Reduction and Management Council)
- Local government emergency services

## License

Free to use and modify.
"# tremr" 
