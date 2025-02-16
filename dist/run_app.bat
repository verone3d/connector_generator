@echo off
echo Starting Connector Generator...
"%~dp0ConnectorApp.exe"
if errorlevel 1 (
    echo Application encountered an error
    pause
) else (
    echo Application closed successfully
    pause
)
