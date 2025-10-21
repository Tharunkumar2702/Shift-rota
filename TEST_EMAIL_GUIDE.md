# 🧪 Email Reset Testing Guide

## 📋 Pre-Test Checklist
- [x] Email reset button added to department modal
- [x] Backend email functions implemented
- [x] Password reset route created
- [x] Email configuration set up

## 🔧 Test Setup (Optional - for real emails)

### Step 1: Configure Email Settings
Create a `.env` file in the project root with your email settings:

```env
# For Gmail (recommended for testing)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-test-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Note**: For Gmail, you need an "App Password" not your regular password:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for this application
3. Use that password in the .env file

### Step 2: Update Admin Emails (Optional)
Edit `app.py` and update the `DEPARTMENT_ADMIN_EMAILS` with real email addresses if you want to receive actual emails.

## 🎯 Manual Testing Steps

### Test 1: Button Visibility
1. ✅ Start your Flask app: `python app.py`
2. ✅ Go to: `http://localhost:5000`
3. ✅ Click on "Service Desk" (or any department)
4. ✅ Click "🔑 Admin Login"  
5. ✅ Click "🔓 Forgot Password?" at the bottom
6. ✅ **VERIFY**: You should see "📧 Email Password Reset" as the first option with a blue border

### Test 2: Token Generation (Backend)
1. ✅ Click the "Send Reset Email" button
2. ✅ Check your browser's developer console (F12) for any errors
3. ✅ Check if `data/password_reset_tokens.json` file is created
4. ✅ **VERIFY**: File should contain a token entry like:
   ```json
   {
     "abc123...": {
       "department": "Service Desk",
       "expiry": "2025-10-15T09:00:00.000000",
       "created": "2025-10-15T08:30:00.000000"
     }
   }
   ```

### Test 3: Email Sending (if configured)
1. ✅ Configure real email settings (see Step 1 above)
2. ✅ Update admin emails to your test email address
3. ✅ Click "Send Reset Email" button
4. ✅ **VERIFY**: Check your email inbox for the reset email
5. ✅ **VERIFY**: Email should contain a reset link like: `http://localhost:5000/reset-password/abc123...`

### Test 4: Password Reset Flow
1. ✅ If you received an email, click the reset link
2. ✅ OR manually go to: `http://localhost:5000/reset-password/[TOKEN]` (replace [TOKEN] with actual token from the JSON file)
3. ✅ **VERIFY**: You should see the password reset form
4. ✅ Enter a new password and confirm it
5. ✅ Click "Update Password"
6. ✅ **VERIFY**: Success message should appear
7. ✅ **VERIFY**: Token should be removed from the JSON file

### Test 5: Token Expiry
1. ✅ Wait 30 minutes after creating a token
2. ✅ Try to use the reset link
3. ✅ **VERIFY**: Should show "Invalid or expired reset token" message

## 🔍 Troubleshooting

### Problem: No email received
- Check spam/junk folder
- Verify email configuration in .env file
- Check that SENDER_PASSWORD is an app password (for Gmail)
- Look for error messages in the browser console

### Problem: Token file not created
- Check write permissions in the `data/` directory
- Look for errors in the browser console
- Verify the Flask app is running without errors

### Problem: Reset link doesn't work
- Check that the token exists in `password_reset_tokens.json`
- Verify the token hasn't expired (30 minutes)
- Check the URL format is correct

## ✅ Expected Results

### Successful Test Results:
- ✅ Button appears in modal with blue highlighting
- ✅ Clicking button shows success/error message
- ✅ Token file is created with valid JSON structure  
- ✅ Email is sent (if configured)
- ✅ Reset link works and updates password
- ✅ Token is deleted after use
- ✅ Expired tokens are rejected

### Files Created During Testing:
- `data/password_reset_tokens.json` - Contains active tokens
- `data/department_config.json` - Updated when password changes

## 🎉 Success Indicators

You'll know the system is working when:
1. 📧 Email reset button appears prominently in the modal
2. 🔗 Clicking it generates tokens (visible in JSON file)
3. 📨 Emails are sent successfully (if configured)
4. 🔐 Reset links work and update passwords
5. ⏰ Expired tokens are properly rejected

## 📝 Quick Test Without Email Setup

Even without email configuration, you can test:
1. Button functionality (should show success/error messages)
2. Token generation (check the JSON file)
3. Manual reset link testing (copy token from JSON file)

The core functionality works regardless of email setup!