# Testing Guide - Tremr

This guide explains how to test the earthquake monitoring application with mock data.

## Quick Test

The easiest way to test is to use the provided test script:

```bash
python test_monitor.py
```

This will:
- Load mock earthquake data from `mock_data.json`
- Show which earthquakes would trigger notifications
- Display actual popup notifications for nearby earthquakes
- Create a test log in `earthquake_monitor.log`

## Test Files

### 1. `mock_data.json`
Contains 5 sample earthquakes with different:
- Locations (various distances from Manila)
- Magnitudes (2.8 to 6.2)
- Times and dates
- Depths

### 2. `test_monitor.py`
Test script with multiple testing modes:

**Default Test:**
```bash
python test_monitor.py
```
Tests with the default mock data file.

**Create Custom Mock Data:**
```bash
python test_monitor.py create
```
Interactive mode to create your own earthquake data for testing.

**Test with Custom Data:**
```bash
python test_monitor.py custom
```
Tests using your custom created earthquake data.

**Help:**
```bash
python test_monitor.py help
```
Shows all available test commands.

## Test Scenarios

### Scenario 1: Test Default Mock Data

```bash
# Run the test
python test_monitor.py
```

Expected output:
- Shows all 5 earthquakes in the mock data
- Displays distance calculations from your location
- Shows which would trigger alerts
- Displays popup notifications for nearby ones

### Scenario 2: Create a Custom Nearby Earthquake

```bash
# Create custom earthquake
python test_monitor.py create
```

When prompted:
- **Latitude**: Use your config.json latitude (or slightly different)
- **Longitude**: Use your config.json longitude (or slightly different)
- **Magnitude**: Enter a value >= your min_magnitude (e.g., 5.0)
- **Location**: Enter a description (e.g., "Near My Location")
- **Depth**: Enter depth (e.g., "010 kilometers")

```bash
# Test your custom earthquake
python test_monitor.py custom
```

You should see a notification popup!

### Scenario 3: Test Different Configurations

1. Edit `config.json` to change settings:
   ```json
   {
       "latitude": 14.5995,
       "longitude": 120.9842,
       "radius_km": 50,        // Change this
       "min_magnitude": 4.0,   // Change this
       ...
   }
   ```

2. Run the test again:
   ```bash
   python test_monitor.py
   ```

3. See how different settings affect which earthquakes trigger alerts.

### Scenario 4: Test Multiple Runs

First run (all earthquakes are new):
```bash
python test_monitor.py
```

Second run (earthquakes already seen):
```bash
python test_monitor.py
```

Notice: Second run shows no notifications (already processed).

To reset:
```bash
# Delete the tracking file
del seen_earthquakes.json

# Run again
python test_monitor.py
```

Now notifications appear again!

## Understanding Test Output

The test script shows detailed information:

```
Earthquake #1:
  Location: 005 km S 52° W of Nasugbu (Batangas)
  Magnitude: 4.5
  Distance: 45.2 km
  Time: 2025-10-28 14:30:45
  ✓ WOULD TRIGGER ALERT (within 100km and >= 3.0 magnitude)
```

**Symbols:**
- ✓ = Would trigger notification
- ✗ = Would NOT trigger (with reason)

**Reasons why earthquake might not trigger:**
- "Too far" = Outside your radius_km
- "Too weak" = Below your min_magnitude

## Creating Realistic Test Data

To create mock data that matches real PHIVOLCS format:

1. Visit real PHIVOLCS data: https://earthquake.phivolcs.dost.gov.ph/2007EQLatest/latestEQ.json

2. Copy the format and modify `mock_data.json`:

```json
{
    "earthquakes": [
        {
            "date": "2025-10-28",
            "time": "14:30:45",
            "latitude": "14.2500",
            "longitude": "120.8500",
            "depth": "025 kilometers",
            "magnitude": "4.5",
            "location": "Your custom location"
        }
    ]
}
```

## Manual Testing with Different Locations

### Test 1: Very Close Earthquake
```json
{
    "latitude": "14.5995",  // Same as your location
    "longitude": "120.9842", // Same as your location
    "magnitude": "5.0"
}
```
Distance: ~0 km - Should definitely trigger!

### Test 2: Edge of Radius
```json
{
    "latitude": "15.4995",  // ~100km north
    "longitude": "120.9842",
    "magnitude": "4.0"
}
```
Distance: ~100 km - Should trigger if radius_km >= 100

### Test 3: Too Far
```json
{
    "latitude": "16.5995",  // ~200km north
    "longitude": "120.9842",
    "magnitude": "6.0"
}
```
Distance: ~200 km - Should NOT trigger (if radius is 100km)

### Test 4: Too Weak
```json
{
    "latitude": "14.5995",
    "longitude": "120.9842",
    "magnitude": "2.5"
}
```
Distance: ~0 km - Should NOT trigger (if min_magnitude is 3.0)

## Troubleshooting Tests

### No notifications appearing

1. Check if earthquake is within radius:
   - Look at "Distance" in test output
   - Compare to your `radius_km` in config.json

2. Check if magnitude is high enough:
   - Look at "Magnitude" in test output
   - Compare to your `min_magnitude` in config.json

3. Check if already seen:
   - Delete `seen_earthquakes.json`
   - Run test again

### "Module not found" errors

Make sure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Notifications not showing on Windows

The `plyer` library should work on Windows. If issues occur:
1. Make sure no other app is blocking notifications
2. Check Windows notification settings
3. Try running as administrator

## Files Created During Testing

- `earthquake_monitor.log` - Detailed logs
- `seen_earthquakes.json` - Tracks processed earthquakes
- `custom_mock_data.json` - Your custom test data (if created)

Delete these files anytime to reset testing.

## Best Practices

1. **Start with default test**: Run `python test_monitor.py` first
2. **Check the output**: Understand which earthquakes would trigger
3. **Adjust config**: Modify settings to test different scenarios
4. **Create custom data**: Make earthquakes at exact locations you want
5. **Reset between tests**: Delete `seen_earthquakes.json` to see notifications again

## Next Steps

After testing successfully:

1. You're confident the app works
2. Update `config.json` with your actual location
3. Run the real app: `python main.py`
4. It will monitor real PHIVOLCS data

Happy testing!
