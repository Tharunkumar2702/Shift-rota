#!/usr/bin/env python
"""
Quick test to verify phone number configuration
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import DEPARTMENT_ADMIN_PHONES, SMS_CONFIG

def test_phone_config():
    print("📱 SMS OTP Phone Number Configuration Test")
    print("=" * 50)
    
    target_number = '+916360747770'
    print(f"Looking for number: {target_number}")
    print()
    
    found = False
    for dept_name, phone_numbers in DEPARTMENT_ADMIN_PHONES.items():
        if target_number in phone_numbers:
            print(f"✅ Found your number in department: {dept_name}")
            print(f"📞 Phone numbers for {dept_name}: {phone_numbers}")
            found = True
            break
    
    if not found:
        print(f"❌ Number {target_number} not found in any department")
        print("Available phone numbers by department:")
        for dept_name, phone_numbers in DEPARTMENT_ADMIN_PHONES.items():
            print(f"  {dept_name}: {phone_numbers}")
    
    print(f"\n🔧 SMS Configuration:")
    print(f"  Provider: {SMS_CONFIG.get('provider', 'Not set')}")
    
    if SMS_CONFIG.get('provider') == 'twilio':
        print("  Twilio settings:")
        print(f"    Account SID: {'Set' if SMS_CONFIG.get('twilio_account_sid') else 'NOT SET'}")
        print(f"    Auth Token: {'Set' if SMS_CONFIG.get('twilio_auth_token') else 'NOT SET'}")
        print(f"    Phone Number: {'Set' if SMS_CONFIG.get('twilio_phone_number') else 'NOT SET'}")
    
    print("\n📋 Next Steps:")
    if found and SMS_CONFIG.get('provider') == 'mock':
        print("1. ✅ Your number is configured")
        print("2. ⚠️  Currently using mock mode - OTP will appear in web response")
        print("3. 🔧 To receive real SMS, set up Twilio credentials and change provider to 'twilio'")
    elif found and SMS_CONFIG.get('provider') == 'twilio':
        if not all([SMS_CONFIG.get('twilio_account_sid'), SMS_CONFIG.get('twilio_auth_token'), SMS_CONFIG.get('twilio_phone_number')]):
            print("1. ✅ Your number is configured")
            print("2. ⚠️  Twilio provider selected but credentials not set")
            print("3. 🔧 Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER environment variables")
        else:
            print("1. ✅ Your number is configured") 
            print("2. ✅ Twilio provider configured")
            print("3. 🚀 Ready to send real SMS! Test via the web interface")
    
    return found

if __name__ == "__main__":
    test_phone_config()