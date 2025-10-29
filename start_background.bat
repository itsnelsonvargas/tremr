@echo off
echo Starting Tremr in background...
start /B pythonw main.py
echo.
echo Tremr is now running in the background.
echo Check earthquake_monitor.log for activity.
echo To stop it, use Task Manager to end the Python process.
echo.
pause
