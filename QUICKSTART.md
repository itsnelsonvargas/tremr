# Quick Start Guide

## Choose Your Method

### ⭐ GUI Method (Easiest - Recommended)

1. **Double-click** `setup.bat` (first time only)
2. **Double-click** `start_gui.bat`
3. **Enter your address** (e.g., "Makati, Philippines")
4. **Click "Search"** to find your location
5. **Click "▶ Start Monitoring"**

✓ No manual editing needed!
✓ Visual interface
✓ Easy to configure

See [GUI_GUIDE.md](GUI_GUIDE.md) for complete GUI documentation.

### 💻 Command Line Method

1. **Double-click** `setup.bat`
   - Installs all dependencies
   - Creates the earthquake warning icon
   - Tests notifications

2. **Edit** `config.json` with your location (optional)
   - Default is Manila (14.5995, 120.9842)

3. **Start monitoring**:
   - Double-click `start_listener.bat`

That's it! The app is now monitoring earthquake data.

## Testing First

Before running live monitoring, test with mock data:

1. **Double-click** `run_test.bat`
2. You should see:
   - Console output showing earthquakes
   - **Triple beep sound**
   - **Popup notification with red warning icon**

If you see and hear the notification, everything works!

## What You'll Experience

When a real nearby earthquake occurs:

### 🔊 Sound Alert
- **Triple beep** system alert sound
- Plays automatically
- Can't be missed!

### 🎨 Visual Alert
- **Bright red/orange icon** with yellow warning triangle
- **Bold notification popup**
- Shows magnitude, location, distance, and time

### Example Notification

```
🚨 EARTHQUAKE ALERT - Magnitude 4.5

Location: 005 km S 52° W of Nasugbu (Batangas)
Distance: 45.2 km away
Depth: 075 kilometers
Time: 2025-10-28 14:30:45
```

## Configuration Tips

Edit `config.json`:

```json
{
    "latitude": 14.5995,        // Your location
    "longitude": 120.9842,
    "radius_km": 100,           // Alert area (increase for wider coverage)
    "min_magnitude": 3.0,       // Minimum earthquake strength
    "check_interval_seconds": 60 // How often to check
}
```

**Recommendations:**
- **Metro Manila**: radius_km: 100, min_magnitude: 3.0
- **Near fault lines**: radius_km: 150, min_magnitude: 2.5
- **Sensitive**: radius_km: 200, min_magnitude: 2.0

## Files You'll See

After running, these files appear:

- `earthquake_warning.png` - The warning icon (auto-created)
- `earthquake_monitor.log` - Activity log
- `seen_earthquakes.json` - Prevents duplicate alerts

## Common Questions

**Q: How do I change the sound?**
A: The sound uses your system's alert sound. It's designed to be urgent and attention-grabbing.

**Q: Can I disable the sound?**
A: Yes, edit `main.py` and set `self.sound_enabled = False` in the `__init__` method.

**Q: The icon doesn't show**
A: Some notification systems don't support icons. The sound and message will still work.

**Q: Too many notifications?**
A: Increase `min_magnitude` in config.json (try 4.0 or 5.0)

**Q: Not enough notifications?**
A: Increase `radius_km` or decrease `min_magnitude`

## Stopping the App

- Console: Press `Ctrl+C`
- Background: Task Manager → End Python process

## Need Help?

Check these files:
- `README.md` - Full documentation
- `TESTING.md` - Testing guide
- `earthquake_monitor.log` - See what happened

## Safety Note

This is an **informational tool** only. For official alerts:
- PHIVOLCS: https://www.phivolcs.dost.gov.ph/
- Follow local emergency services
- Have an earthquake preparedness plan

---

**Remember**: Tremr helps you stay informed, but always follow official emergency protocols!
