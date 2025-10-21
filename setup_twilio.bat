@echo off
REM Setup Twilio Environment Variables for SMS OTP Testing
echo Setting up Twilio credentials for SMS OTP testing...

REM Replace these with your actual Twilio credentials
REM Get these from your Twilio Console: https://console.twilio.com/

set TWILIO_ACCOUNT_SID=your_account_sid_here
set TWILIO_AUTH_TOKEN=your_auth_token_here
set TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
set SMS_PROVIDER=twilio

echo.
echo ==========================================
echo Twilio Environment Variables Set:
echo ==========================================
echo TWILIO_ACCOUNT_SID: %TWILIO_ACCOUNT_SID%
echo TWILIO_AUTH_TOKEN: %TWILIO_AUTH_TOKEN%
echo TWILIO_PHONE_NUMBER: %TWILIO_PHONE_NUMBER%
echo SMS_PROVIDER: %SMS_PROVIDER%
echo.
echo IMPORTANT: Replace the placeholder values above with your actual Twilio credentials!
echo.
echo To get your Twilio credentials:
echo 1. Go to https://console.twilio.com/
echo 2. Copy your Account SID and Auth Token
echo 3. Get a Twilio phone number from the Phone Numbers section
echo.
echo After updating the credentials, run this file before starting the Flask app.
echo.

REM Install Twilio package if not already installed
echo Installing Twilio Python package...
"C:\Users\100641093\AppData\Local\Programs\Python\Python314\python.exe" -m pip install twilio

echo.
echo Setup complete! Now start the Flask app with: start_server.bat
pause
