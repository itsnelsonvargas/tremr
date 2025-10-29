# GUI Guide - Tremr

## Quick Start

1. **Double-click** `start_gui.bat`
2. The GUI window will open
3. Configure your settings
4. Click "▶ Start Monitoring"

That's it!

## GUI Overview

The application features a clean, minimalist interface with all essential controls:

```
┌─────────────────────────────────────┐
│    🌋 Tremr          │
├─────────────────────────────────────┤
│ Status: ● Stopped / ● Monitoring    │
├─────────────────────────────────────┤
│ Monitoring Location                 │
│  Address: [Manila, Philippines   ]  │
│           [Search]                  │
│  Coordinates: 14.5995, 120.9842     │
├─────────────────────────────────────┤
│ Alert Settings                      │
│  Alert Radius (km):        [100 ]   │
│  Min Magnitude:            [3.0 ]   │
│  Check Interval (sec):     [60  ]   │
├─────────────────────────────────────┤
│ System Settings                     │
│  ☐ Start automatically on boot      │
├─────────────────────────────────────┤
│ [▶ Start Monitoring] [■ Stop]       │
├─────────────────────────────────────┤
│ Activity Log                        │
│ [log messages here...]              │
└─────────────────────────────────────┘
```

## Features

### 1. Status Indicator
- **Red ●**: Monitoring stopped
- **Green ●**: Monitoring active

### 2. Address Search
Instead of manually entering latitude/longitude coordinates:

**How to use:**
1. Type any address in the address field
2. Click "Search"
3. The app will find the location and set coordinates automatically

**Examples:**
- `Quezon City, Philippines`
- `Makati, Metro Manila`
- `Cebu City, Cebu, Philippines`
- `BGC, Taguig`
- `Mall of Asia, Pasay`

**Tips:**
- Be specific: Include city and country
- If not found, try a nearby landmark or main area
- You can search addresses worldwide!

### 3. Alert Settings

#### Alert Radius (10-500 km)
- Distance from your location to receive alerts
- **Recommended settings:**
  - **Metro Manila**: 100 km
  - **Provincial**: 150 km
  - **Wide coverage**: 200-300 km

#### Min Magnitude (1.0-10.0)
- Minimum earthquake strength to alert
- **Recommended settings:**
  - **Normal**: 3.0 (noticeable shaking)
  - **Sensitive**: 2.5 (minor tremors)
  - **Major only**: 4.0+ (moderate to strong)

#### Check Interval (30-300 seconds)
- How often to check PHIVOLCS for new data
- **Recommended settings:**
  - **Normal**: 60 seconds (every minute)
  - **Frequent**: 30 seconds
  - **Conservative**: 120 seconds (saves bandwidth)

### 4. Auto-Start on Boot

Enable this to have the monitoring start automatically when Windows boots.

**When enabled:**
- App opens when computer starts
- You can set it to start monitoring automatically
- Great for 24/7 monitoring

**To enable:**
1. Check the box "Start automatically on boot"
2. Confirm the permission dialog
3. Done!

**To disable:**
1. Uncheck the box
2. Confirm
3. App won't start on boot anymore

### 5. Activity Log

Real-time display of:
- When monitoring starts/stops
- Address searches
- Earthquake detections
- Any errors or warnings

Scroll through to see recent activity.

## Usage Scenarios

### Scenario 1: First Time Setup

1. **Launch**: Double-click `start_gui.bat`
2. **Set Location**:
   - Type your address (e.g., "Makati, Philippines")
   - Click "Search"
   - Confirm the location is correct
3. **Adjust Settings** (optional):
   - Radius: 100 km
   - Magnitude: 3.0
   - Interval: 60 sec
4. **Start**: Click "▶ Start Monitoring"
5. **Enable Auto-start** (optional): Check the auto-start box

### Scenario 2: Testing First

1. Launch GUI
2. Set your location
3. Click "▶ Start Monitoring"
4. In another window, run: `python test_monitor.py`
5. You should hear beeps and see a notification!
6. Check the Activity Log for details

### Scenario 3: Different Locations

**Monitoring your home:**
```
Address: [Your home address]
Radius: 50 km
Min Magnitude: 3.0
```

**Monitoring your workplace:**
```
Address: [Your office address]
Radius: 100 km
Min Magnitude: 3.0
```

Simply change the address, click Search, and restart monitoring!

### Scenario 4: 24/7 Monitoring

1. Set up your location and settings
2. Check "Start automatically on boot"
3. Click "▶ Start Monitoring"
4. Minimize the window
5. The app will:
   - Run in background
   - Alert you of earthquakes
   - Restart automatically when computer reboots

## Notifications

When an earthquake is detected:

1. **Sound Alert**: Triple beep (urgent!)
2. **Visual Popup**:
   ```
   🚨 EARTHQUAKE ALERT - Magnitude 4.5

   Location: 005 km S 52° W of Nasugbu (Batangas)
   Distance: 45.2 km away
   Depth: 075 kilometers
   Time: 2025-10-28 14:30:45
   ```
3. **Activity Log**: Entry added to log

## Troubleshooting

### "Address not found"

**Problem**: Can't find your address

**Solutions:**
- Try a more specific address
- Include city and country
- Use a nearby landmark
- Try the municipality/city name
- Example: Instead of "BGC", try "Bonifacio Global City, Taguig, Philippines"

### "Search button stuck on 'Searching...'"

**Problem**: Address search taking too long

**Solutions:**
- Wait 10-15 seconds (it's searching online)
- Check your internet connection
- Restart the GUI and try again
- Try a simpler address

### "Cannot enable auto-start"

**Problem**: Auto-start checkbox doesn't work

**Solutions:**
- Run as Administrator (right-click start_gui.bat → Run as administrator)
- Check Windows security settings
- Manually add to startup folder:
  - Press `Win+R`
  - Type `shell:startup`
  - Create shortcut to `start_gui.bat` there

### GUI doesn't open

**Problem**: Double-clicking start_gui.bat does nothing

**Solutions:**
- Make sure Python is installed
- Run setup.bat first
- Try: `python gui.py` in command prompt
- Check if required packages are installed

### Monitoring stops unexpectedly

**Problem**: Status changes to "Stopped" automatically

**Solutions:**
- Check Activity Log for errors
- Verify internet connection
- PHIVOLCS server might be down (temporary)
- Check earthquake_monitor.log file
- Restart monitoring

## Keyboard Shortcuts

- `Alt+F4`: Close window (prompts if monitoring)
- `Tab`: Navigate between fields
- `Enter`: Activate focused button

## Window Controls

- **Minimize**: App continues monitoring in background
- **Close**: Prompts to confirm if monitoring is active
- **Not Resizable**: Fixed size for consistency

## Tips & Best Practices

### For Best Results:

1. **Test First**: Use test_monitor.py before relying on it
2. **Adjust Settings**: Tune radius and magnitude to your needs
3. **Check Logs**: Review Activity Log regularly
4. **Internet Required**: Keep computer connected
5. **Auto-start**: Enable for 24/7 protection

### Power Users:

- **Multiple Locations**: Change address as needed
- **Fine-tune Settings**: Adjust based on alert frequency
- **Log Files**: Check `earthquake_monitor.log` for detailed history
- **Config File**: Advanced users can edit `config.json` directly

### Safety:

- This is an **informational tool**
- Always follow official emergency protocols
- Have an earthquake preparedness plan
- Don't rely solely on this app

## Advanced

### Running Both GUI and Command Line

You can have:
- **GUI version**: For easy control (start_gui.bat)
- **Command line version**: For background service (main.py)

They use the same config file, so settings sync automatically.

### Portable Setup

The app is portable! Just copy the entire folder to another Windows PC:
1. Copy `tremr` folder
2. Run `setup.bat` on new PC
3. Launch `start_gui.bat`
4. Configure and go!

### Logs Location

All logs are in the app folder:
- `earthquake_monitor.log` - Detailed activity log
- `seen_earthquakes.json` - Prevents duplicate alerts
- `config.json` - Your settings

## FAQ

**Q: Does the GUI need to stay open?**
A: Yes, but you can minimize it. It will continue monitoring.

**Q: Can I close the GUI and keep monitoring?**
A: No. Closing stops monitoring. Use minimize instead.

**Q: How do I monitor multiple locations?**
A: Change address and restart monitoring. Or run multiple instances with different config files.

**Q: Does this work offline?**
A: No, internet connection required to fetch PHIVOLCS data.

**Q: Can I change the notification sound?**
A: Currently uses system alert sound. Custom sounds coming in future updates.

**Q: Is this official PHIVOLCS software?**
A: No, this is unofficial. It uses public PHIVOLCS data. For official alerts, visit phivolcs.dost.gov.ph

## Support

For issues:
1. Check `earthquake_monitor.log`
2. Review this guide
3. Check README.md and TESTING.md
4. Restart the application

---

**Stay Safe! Stay Informed!**

Tremr - Your personal earthquake monitoring companion.
