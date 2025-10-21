#!/usr/bin/env python3
"""
Test script for email functionality in the Shift Rota app
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the email functions from our app
try:
    from app import (
        create_reset_token, 
        validate_reset_token, 
        send_reset_email,
        cleanup_expired_tokens,
        DEPARTMENT_ADMIN_EMAILS,
        EMAIL_CONFIG
    )
    print("✅ Successfully imported email functions from app.py")
except ImportError as e:
    print(f"❌ Error importing functions: {e}")
    sys.exit(1)

def test_token_creation_and_validation():
    """Test token creation and validation"""
    print("\n🧪 Testing token creation and validation...")
    
    # Test token creation
    department = "Service Desk"
    token = create_reset_token(department, expiry_minutes=1)  # Short expiry for testing
    print(f"✅ Created token: {token[:20]}...")
    
    # Test token validation
    validated_dept = validate_reset_token(token)
    if validated_dept == department:
        print(f"✅ Token validation successful: {validated_dept}")
    else:
        print(f"❌ Token validation failed: expected '{department}', got '{validated_dept}'")
    
    # Test invalid token
    invalid_dept = validate_reset_token("invalid_token_123")
    if invalid_dept is None:
        print("✅ Invalid token correctly rejected")
    else:
        print(f"❌ Invalid token incorrectly validated: {invalid_dept}")
    
    return token

def test_email_configuration():
    """Test email configuration"""
    print("\n📧 Testing email configuration...")
    
    print(f"SMTP Server: {EMAIL_CONFIG['smtp_server']}")
    print(f"SMTP Port: {EMAIL_CONFIG['smtp_port']}")
    print(f"Sender Email: {EMAIL_CONFIG['sender_email']}")
    print(f"Password Set: {'Yes' if EMAIL_CONFIG['sender_password'] else 'No (using default/empty)'}")
    
    print("\n👥 Department Admin Emails:")
    for dept, emails in DEPARTMENT_ADMIN_EMAILS.items():
        print(f"  {dept}: {', '.join(emails)}")

def test_email_sending():
    """Test email sending (simulation mode)"""
    print("\n📨 Testing email sending...")
    
    department = "Service Desk"
    token = create_reset_token(department)
    
    # Try to send email
    try:
        success, message = send_reset_email(department, token)
        if success:
            print(f"✅ Email send simulation successful: {message}")
        else:
            print(f"⚠️  Email send failed (expected if no real SMTP configured): {message}")
    except Exception as e:
        print(f"⚠️  Email send error (expected if no real SMTP configured): {e}")

def test_token_expiry():
    """Test token expiry"""
    print("\n⏰ Testing token expiry...")
    
    # Create a token that expires very quickly
    department = "Service Desk"
    
    # Create token with 0 minutes (immediately expired)
    token = create_reset_token(department, expiry_minutes=0)
    
    # Wait a moment and test
    import time
    time.sleep(1)
    
    validated_dept = validate_reset_token(token)
    if validated_dept is None:
        print("✅ Expired token correctly rejected")
    else:
        print(f"❌ Expired token incorrectly validated: {validated_dept}")

def test_cleanup():
    """Test token cleanup"""
    print("\n🧹 Testing token cleanup...")
    
    # Create some expired tokens
    for i in range(3):
        create_reset_token("Test Department", expiry_minutes=0)
    
    # Run cleanup
    cleaned_count = cleanup_expired_tokens()
    print(f"✅ Cleaned up {cleaned_count} expired tokens")

if __name__ == "__main__":
    print("🚀 Starting Shift Rota Email System Tests")
    print("=" * 50)
    
    try:
        test_email_configuration()
        test_token_creation_and_validation()
        test_token_expiry()
        test_cleanup()
        test_email_sending()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n📝 Next Steps:")
        print("1. Configure real email settings in .env file (optional)")
        print("2. Update admin email addresses in app.py")
        print("3. Test the 'Send Reset Email' button in your browser")
        print("4. Check that tokens are created in data/password_reset_tokens.json")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()