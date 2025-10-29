# Tremr - Overview

## What is This?

**Tremr** is your personal earthquake early warning system that monitors PHIVOLCS (Philippine Institute of Volcanology and Seismology) data in real-time and alerts you immediately when earthquakes occur near your location.

## Why Use This?

- ⚡ **Real-time alerts** - Know about earthquakes as they happen
- 🎯 **Location-based** - Only alerts for earthquakes near you
- 🔊 **Impossible to miss** - Loud sound + bright popup notification
- 🖥️ **Easy to use** - Simple GUI, no technical knowledge needed
- 🚀 **Auto-start** - Can monitor 24/7 automatically
- 🌍 **Works anywhere** - Monitor any location in the Philippines (or worldwide)

## Two Ways to Use

### 1. GUI Application (Recommended)

**Best for:** Everyone, especially non-technical users

**Features:**
- Clean, modern interface
- Type address, app finds coordinates automatically
- All settings in one place
- Visual status indicator
- Activity log
- Enable auto-start with one click

**Start:** Double-click `start_gui.bat`

### 2. Command Line

**Best for:** Advanced users, servers, always-on systems

**Features:**
- Runs in background
- Minimal resource usage
- Can be scripted
- Detailed logging

**Start:** Double-click `start_listener.bat`

## How It Works

```
┌─────────────────┐
│  PHIVOLCS API   │  ← Real earthquake data
│  (Government)   │
└────────┬────────┘
         │
         │ Checks every 60 seconds
         │
         ▼
┌─────────────────┐
│  The Big One    │  ← Your computer
│    Listener     │
└────────┬────────┘
         │
         │ When earthquake detected nearby
         │
         ▼
┌─────────────────┐
│  🔊 ALERT! 🚨   │  ← You get notified!
│  Magnitude 4.5  │
│  45 km away     │
└─────────────────┘
```

## File Structure

```
tremr/
├── 📱 GUI Files
│   ├── start_gui.bat          ← Launch GUI (EASIEST)
│   ├── gui.py                 ← GUI application code
│   └── GUI_GUIDE.md           ← GUI documentation
│
├── 💻 Command Line Files
│   ├── start_listener.bat     ← Launch monitoring
│   ├── start_background.bat   ← Launch in background
│   ├── main.py                ← Main monitoring code
│   └── README.md              ← Full documentation
│
├── 🧪 Testing Files
│   ├── run_test.bat           ← Test with mock data
│   ├── test_monitor.py        ← Test script
│   ├── mock_data.json         ← Sample earthquakes
│   └── TESTING.md             ← Testing guide
│
├── ⚙️ Setup Files
│   ├── setup.bat              ← Easy installation
│   ├── setup.py               ← Setup script
│   ├── requirements.txt       ← Required packages
│   └── QUICKSTART.md          ← Quick start guide
│
├── 🎨 Resources
│   ├── create_icon.py         ← Creates warning icon
│   ├── create_sound.py        ← Creates warning sounds
│   └── earthquake_warning.png ← Warning icon (auto-created)
│
└── 📝 Generated Files
    ├── config.json            ← Your settings
    ├── earthquake_monitor.log ← Activity log
    └── seen_earthquakes.json  ← Tracks alerts sent
```

## What Happens When Earthquake Detected?

1. **Sound Alert** 🔊
   - Triple beep (urgent system alert sound)
   - Plays automatically
   - Impossible to miss!

2. **Visual Alert** 🚨
   - Bright red/orange warning icon
   - Popup notification with:
     - Magnitude
     - Location
     - Distance from you
     - Depth
     - Time

3. **Logged** 📝
   - All details saved to log file
   - Won't alert again for same earthquake

## Example Alert

```
🚨 EARTHQUAKE ALERT - Magnitude 4.5

Location: 005 km S 52° W of Nasugbu (Batangas)
Distance: 45.2 km away
Depth: 075 kilometers
Time: 2025-10-28 14:30:45
```

## Configuration Options

All configurable through GUI or `config.json`:

| Setting | Default | Description |
|---------|---------|-------------|
| **Address** | Manila, Philippines | Your monitoring location |
| **Alert Radius** | 100 km | How far to detect earthquakes |
| **Min Magnitude** | 3.0 | Minimum earthquake strength |
| **Check Interval** | 60 sec | How often to check for new data |
| **Auto-start** | Off | Start monitoring on boot |

## Use Cases

### Home Safety
```
Location: Your home address
Radius: 50 km
Min Magnitude: 3.0
Auto-start: ON
```
→ Always know if earthquake affects your home

### Office Monitoring
```
Location: Your office address
Radius: 100 km
Min Magnitude: 3.5
Auto-start: OFF
```
→ Monitor while at work

### Family Safety
```
Location: Parents' home
Radius: 150 km
Min Magnitude: 3.0
Auto-start: ON
```
→ Get alerted even if family members don't

### Wide Area Monitoring
```
Location: Manila
Radius: 300 km
Min Magnitude: 5.0
```
→ Track major earthquakes in entire region

## System Requirements

### Minimum
- Windows 7 or higher
- Python 3.7+
- 100 MB free space
- Internet connection

### Recommended
- Windows 10/11
- Python 3.9+
- Always-on computer or laptop
- Reliable internet

## Installation Steps

1. **Download** → Get the folder
2. **Setup** → Double-click `setup.bat`
3. **Configure** → Open GUI with `start_gui.bat`
4. **Test** → Use `run_test.bat`
5. **Monitor** → Start monitoring!

Total time: ~5 minutes

## Benefits

✅ **Free** - No subscription, no ads
✅ **Private** - All processing on your computer
✅ **Reliable** - Uses official PHIVOLCS data
✅ **Customizable** - Adjust all settings
✅ **Open Source** - See exactly what it does
✅ **No Account Needed** - Just download and run

## Limitations

⚠ **Not an official PHIVOLCS product**
⚠ **Requires internet connection**
⚠ **Depends on PHIVOLCS API availability**
⚠ **Not a substitute for official warnings**
⚠ **Your computer must be on to monitor**

## Safety Disclaimer

This is an **informational tool** to supplement, not replace, official earthquake warning systems.

**Always:**
- Follow official PHIVOLCS advisories
- Have an earthquake preparedness plan
- Know your evacuation routes
- Practice "Drop, Cover, and Hold On"

**Official Resources:**
- PHIVOLCS: https://www.phivolcs.dost.gov.ph/
- NDRRMC: https://ndrrmc.gov.ph/

## Getting Started

### Complete Beginner?
1. Read: [QUICKSTART.md](QUICKSTART.md)
2. Run: `setup.bat`
3. Launch: `start_gui.bat`
4. Learn: [GUI_GUIDE.md](GUI_GUIDE.md)

### Want to Test First?
1. Run: `setup.bat`
2. Test: `run_test.bat`
3. Verify: See notification popup
4. Start: `start_gui.bat`

### Technical User?
1. Read: [README.md](README.md)
2. Setup: `pip install -r requirements.txt`
3. Configure: Edit `config.json`
4. Run: `python main.py`

## Support & Documentation

- **Quick Start**: QUICKSTART.md
- **GUI Guide**: GUI_GUIDE.md
- **Full Documentation**: README.md
- **Testing Guide**: TESTING.md
- **This Overview**: OVERVIEW.md

## Statistics

- **Lines of Code**: ~1500
- **Dependencies**: 5 Python packages
- **Files**: 20+
- **Documentation**: 6 guides
- **Setup Time**: 5 minutes
- **Learning Curve**: 10 minutes

## Philosophy

**Keep It Simple** - Complex technology, simple interface
**Safety First** - Clear, urgent alerts you can't miss
**Privacy Matters** - All data stays on your computer
**Everyone Can Use It** - No tech skills required

---

**Ready to get started?**

1. Double-click `setup.bat`
2. Double-click `start_gui.bat`
3. Enter your address
4. Click Start Monitoring

**That's it!**

You're now protected by your personal earthquake early warning system.

---

🌋 **Tremr** - *Be Prepared. Stay Informed.*
