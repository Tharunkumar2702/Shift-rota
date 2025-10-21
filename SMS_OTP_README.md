# SMS OTP Password Reset Feature

## Overview

The SMS OTP (One-Time Password) feature allows department administrators to reset their passwords using a secure 6-digit code sent via SMS, without requiring email access. This provides a more user-friendly alternative to email-based password resets.

## Features

- **Secure OTP Generation**: 6-digit numeric codes with configurable expiry
- **Multiple SMS Providers**: Support for Twilio, AWS SNS, TextLocal, and mock mode
- **Attempt Limiting**: Maximum 3 attempts per OTP to prevent brute force attacks
- **Auto-cleanup**: Expired tokens are automatically removed
- **Department-specific**: Each department can have multiple admin phone numbers
- **User-friendly UI**: Integrated into the existing forgot password page

## How It Works

1. **Request OTP**: User selects their department and clicks "Send OTP via SMS"
2. **Send SMS**: System generates a 6-digit OTP and sends it to all configured admin phone numbers for that department
3. **Enter OTP**: User enters the received OTP code along with their new password
4. **Verify & Reset**: System validates the OTP and updates the department password if valid

## Configuration

### Department Phone Numbers

Phone numbers are configured in `app.py` in the `DEPARTMENT_ADMIN_PHONES` dictionary:

```python
DEPARTMENT_ADMIN_PHONES = {
    'Service Desk': ['+1234567890', '+0987654321'],
    'App Tools': ['+1111222233'],
    # Add more departments as needed
}
```

### SMS Providers

Configure your preferred SMS provider by setting the `SMS_PROVIDER` environment variable or updating `SMS_CONFIG` in `app.py`:

#### Twilio (Recommended)
```bash
export SMS_PROVIDER=twilio
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
export TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

#### AWS SNS
```bash
export SMS_PROVIDER=aws_sns
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=your_region
```

#### TextLocal
```bash
export SMS_PROVIDER=textlocal
export TEXTLOCAL_API_KEY=your_api_key
export TEXTLOCAL_SENDER=your_sender_name
```

#### Mock Mode (Development)
```bash
export SMS_PROVIDER=mock
```

## Usage

### For End Users

1. Go to the login page and click "Forgot Password"
2. Select "SMS OTP Password Reset" (the first option with 📱 icon)
3. Choose your department from the dropdown
4. Click "Send OTP via SMS"
5. Check your phone for the 6-digit code
6. Enter the OTP code and your new password
7. Click "Reset Password with OTP"

### For Administrators

1. Ensure department phone numbers are configured in `DEPARTMENT_ADMIN_PHONES`
2. Configure your SMS provider credentials
3. Test the functionality using the test script: `python test_sms_otp.py`

## Security Features

- **Time-limited OTPs**: Tokens expire after 10 minutes by default
- **Attempt limiting**: Maximum 3 validation attempts per OTP
- **Department validation**: OTP must match the selected department
- **Secure token storage**: Tokens are stored securely and cleaned up automatically
- **Password requirements**: Minimum 6 characters for new passwords

## Testing

Run the comprehensive test suite:

```bash
python test_sms_otp.py
```

This tests:
- OTP generation and validation
- Token creation and management
- Attempt tracking and limits
- SMS sending functionality
- Token consumption after use

## Files Modified

1. **`app.py`**: Added SMS OTP functions and route handlers
2. **`templates/forgot_password.html`**: Updated UI with SMS OTP option
3. **`test_sms_otp.py`**: Comprehensive test suite
4. **`SMS_OTP_README.md`**: This documentation

## Troubleshooting

### Common Issues

1. **"SMS OTP is not configured for [department]"**
   - Add the department to `DEPARTMENT_ADMIN_PHONES` dictionary

2. **"Twilio library not installed"**
   - Run: `pip install twilio` or switch to mock mode for testing

3. **"OTP verification failed: Invalid token"**
   - Check if OTP was entered correctly (6 digits)
   - Ensure OTP hasn't expired (10 minutes default)
   - Verify you haven't exceeded 3 attempts

4. **"OTP does not match the selected department"**
   - Make sure you're using the same department that you requested the OTP for

### Debug Mode

Set SMS provider to 'mock' to see OTP codes in the response message:

```python
SMS_CONFIG['provider'] = 'mock'
```

## Future Enhancements

Potential improvements:
- Rate limiting for OTP requests
- SMS delivery status tracking
- Multi-language SMS templates
- Integration with enterprise SMS gateways
- Audit logging for password reset activities

## Support

For issues or questions about the SMS OTP feature, check:
1. This documentation
2. The test script output
3. Flask application logs
4. SMS provider documentation