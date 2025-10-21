# 📧 Email Setup Guide for Testing

## ✅ Configuration Complete!
Service Desk admin emails are now set to:
- ✅ pruthvi.rajavarmaman@intertrustgroup.com
- ✅ vinay.simhav@intertrustgroup.com  
- ✅ naveen.panchakshari@intertrustgroup.com
- ✅ tarun.kumar@intertrustgroup.com

## 🚀 Quick Start - Email Testing

### Step 1: Choose Your Email Setup Method

#### Option A: Gmail (Recommended - Easiest)
1. **Create/Copy .env file**:
   ```bash
   copy .env.example .env
   ```
2. **Edit `.env` file** and set:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-gmail@gmail.com
   SENDER_PASSWORD=your-app-password
   ```
3. **Get Gmail App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password (format: `abcd-efgh-ijkl-mnop`)
   - Use this in SENDER_PASSWORD (not your regular Gmail password)

#### Option B: Company Email (If Available)
If InterTrust Group provides SMTP settings, use:
```env
SMTP_SERVER=mail.intertrustgroup.com
SMTP_PORT=587  # or 25, 465
SENDER_EMAIL=your-email@intertrustgroup.com
SENDER_PASSWORD=your-company-password
```

#### Option C: Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

### Step 2: Test the Email System

1. **Start the app**:
   ```bash
   python app.py
   ```

2. **Test the email reset**:
   - Go to: http://localhost:5000
   - Click "Service Desk"
   - Click "🔑 Admin Login" 
   - Click "🔓 Forgot Password?"
   - Click "Send Reset Email" button

3. **Check your emails**:
   - All four InterTrust Group email addresses should receive the reset email
   - Check spam/junk folders too
   - Email subject: "Password Reset Request - Service Desk Department"

### Step 3: Test the Reset Link

1. **Find the email** in one of the three inboxes
2. **Click the reset link** in the email
3. **Set new password** (minimum 6 characters)
4. **Verify success** - password should be updated

## 🔍 Troubleshooting

### Problem: "Failed to send reset email"
**Gmail Issues:**
- ✅ Make sure you're using an App Password, not regular password
- ✅ Enable 2-factor authentication on Gmail first
- ✅ Check the App Password is exactly 16 characters with dashes

**General Issues:**
- ✅ Check .env file exists and has correct format
- ✅ No extra spaces in email addresses
- ✅ Internet connection working
- ✅ Firewall/antivirus not blocking Python

### Problem: No emails received
- ✅ Check spam/junk folders in all four email accounts
- ✅ Verify email addresses are correct
- ✅ Check if company firewall blocks outgoing SMTP

### Problem: "Invalid SMTP credentials"
- ✅ Double-check username/password in .env file
- ✅ For Gmail: Must use App Password
- ✅ For company email: Confirm SMTP server address

## 📝 Testing Checklist

### Before Testing:
- [ ] .env file created with email credentials
- [ ] Email credentials tested (Gmail App Password set up)
- [ ] Flask app started successfully

### During Testing:
- [ ] "Send Reset Email" button clicked
- [ ] Success message appears
- [ ] No error messages in browser console

### After Testing:
- [ ] All four email addresses received the reset email
- [ ] Reset link in email works
- [ ] Password can be changed successfully
- [ ] New password works for login

## 🎯 Expected Email Content

You should receive an email like this:

**Subject:** Password Reset Request - Service Desk Department

**Body:**
```
A password reset has been requested for the Service Desk department 
in the Shift Rota application.

Click the link below to reset the password:
http://localhost:5000/reset-password/abc123...

This link will expire in 30 minutes.

If you did not request this reset, please ignore this email.

Best regards,
Shift Rota System
```

## 🔧 Alternative Testing (Without Email Setup)

Even without email configuration, you can test:

1. **Click "Send Reset Email"** - should show error message
2. **Check token generation** - look for `data/password_reset_tokens.json`
3. **Manual reset testing** - copy token from JSON file and go to:
   `http://localhost:5000/reset-password/[TOKEN]`

The core system works regardless of email setup!

## 📞 Need Help?

If you encounter issues:
1. Check the browser console (F12) for error messages
2. Look at the Flask console output for detailed errors
3. Verify .env file format and credentials
4. Try with a personal Gmail account first (easiest setup)