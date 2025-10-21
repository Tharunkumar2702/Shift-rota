@echo off
echo ===============================================
echo Setting up REAL SMS with Twilio
echo ===============================================

REM Replace these with your actual Twilio credentials from console.twilio.com
REM !! IMPORTANT: Replace the values below with your real credentials !!

set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
set TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
set SMS_PROVIDER=twilio

echo.
echo Current settings:
echo TWILIO_ACCOUNT_SID: %TWILIO_ACCOUNT_SID%
echo TWILIO_AUTH_TOKEN: %TWILIO_AUTH_TOKEN%
echo TWILIO_PHONE_NUMBER: %TWILIO_PHONE_NUMBER%
echo SMS_PROVIDER: %SMS_PROVIDER%
echo.

if "%TWILIO_ACCOUNT_SID%"=="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" (
    echo ==========================================
    echo ERROR: Please update this file with your real Twilio credentials!
    echo ==========================================
    echo 1. Go to https://console.twilio.com/
    echo 2. Copy your Account SID, Auth Token, and Phone Number
    echo 3. Replace the xxxxxxx values in this file
    echo 4. Save and run this file again
    echo.
    pause
    exit /b 1
)

echo Starting Flask server with real SMS enabled...
echo Your phone +916360747770 should receive real SMS messages!
echo.

"C:\Users\100641093\AppData\Local\Programs\Python\Python314\python.exe" app.py

pause