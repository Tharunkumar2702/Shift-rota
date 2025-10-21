@echo off
echo 🚀 Starting Shift Rota App for Email Reset Testing
echo ===============================================
echo.
echo 📧 Testing the 2FA Email Reset System
echo.
echo 🎯 Quick Test Steps:
echo 1. Go to: http://localhost:5000
echo 2. Click any department (e.g., Service Desk)
echo 3. Click "🔑 Admin Login"
echo 4. Click "🔓 Forgot Password?"
echo 5. Look for "📧 Email Password Reset" (blue border)
echo 6. Click "Send Reset Email" button
echo.
echo 📁 Check these files after testing:
echo - data/password_reset_tokens.json (should be created)
echo.
echo ⚠️  Note: Emails won't actually send without .env configuration
echo    But token generation and UI should work!
echo.
echo Starting Flask server...
echo ===============================================
echo.

python app.py

echo.
echo ===============================================
echo Server stopped. Check TEST_EMAIL_GUIDE.md for detailed testing instructions.
pause