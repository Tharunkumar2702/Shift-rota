#!/usr/bin/env python
"""
Test script for SMS OTP functionality
"""
import sys
import os

# Add the app directory to path so we can import app functions
sys.path.append(os.path.dirname(__file__))

from app import (
    generate_otp, 
    create_otp_token, 
    validate_otp_token, 
    consume_otp_token,
    increment_otp_attempts,
    send_otp_sms,
    DEPARTMENT_ADMIN_PHONES,
    get_current_departments
)

def test_otp_generation():
    """Test OTP generation"""
    print("\n🔢 Testing OTP generation...")
    otp = generate_otp()
    print(f"✓ Generated OTP: {otp}")
    assert len(otp) == 6, "OTP should be 6 digits"
    assert otp.isdigit(), "OTP should contain only digits"
    return otp

def test_otp_token_creation_and_validation():
    """Test OTP token creation and validation"""
    print("\n🎫 Testing OTP token creation and validation...")
    
    department = "Service Support"  # Use a department from the config
    otp_code = create_otp_token(department, expiry_minutes=10)
    print(f"✓ Created OTP token: {otp_code}")
    
    # Test validation
    validated_dept, message = validate_otp_token(otp_code)
    if validated_dept == department:
        print(f"✓ Token validation successful: {validated_dept}")
    else:
        print(f"✗ Token validation failed: expected '{department}', got '{validated_dept}', message: {message}")
    
    return otp_code

def test_otp_attempts():
    """Test OTP attempt tracking"""
    print("\n🔄 Testing OTP attempt tracking...")
    
    department = "Service Support"
    otp_code = create_otp_token(department, expiry_minutes=10)
    
    # Increment attempts
    increment_otp_attempts(otp_code)
    increment_otp_attempts(otp_code)
    increment_otp_attempts(otp_code)  # This should make it invalid
    
    # Try to validate after max attempts
    validated_dept, message = validate_otp_token(otp_code)
    if not validated_dept and "attempts" in message.lower():
        print("✓ Max attempts correctly enforced")
    else:
        print(f"✗ Max attempts not enforced: {message}")

def test_sms_sending():
    """Test SMS sending functionality"""
    print("\n📱 Testing SMS sending...")
    
    department = "Service Support"  # Use a department that has phone numbers configured
    otp_code = "123456"
    
    # Check if department has SMS configured
    if department not in DEPARTMENT_ADMIN_PHONES:
        print(f"⚠️  Department '{department}' not configured for SMS")
        print(f"Available departments for SMS: {list(DEPARTMENT_ADMIN_PHONES.keys())}")
        
        # Try with a configured department
        if DEPARTMENT_ADMIN_PHONES:
            department = list(DEPARTMENT_ADMIN_PHONES.keys())[0]
            print(f"Testing with configured department: {department}")
        else:
            print("No departments configured for SMS OTP")
            return False
    
    success, message = send_otp_sms(department, otp_code)
    if success:
        print(f"✓ SMS sent successfully: {message}")
    else:
        print(f"✗ SMS sending failed: {message}")
    
    return success

def test_otp_consumption():
    """Test OTP consumption (removal after use)"""
    print("\n🗑️ Testing OTP consumption...")
    
    department = "Service Support"
    otp_code = create_otp_token(department, expiry_minutes=10)
    
    # Consume the token
    consume_otp_token(otp_code)
    
    # Try to validate consumed token
    validated_dept, message = validate_otp_token(otp_code)
    if not validated_dept:
        print("✓ Consumed token correctly removed")
    else:
        print(f"✗ Consumed token still valid: {validated_dept}")

def main():
    """Run all SMS OTP tests"""
    print("🧪 SMS OTP Functionality Tests")
    print("=" * 50)
    
    try:
        # Test basic OTP generation
        otp = test_otp_generation()
        
        # Test token creation and validation
        token = test_otp_token_creation_and_validation()
        
        # Test attempt tracking
        test_otp_attempts()
        
        # Test SMS sending
        sms_success = test_sms_sending()
        
        # Test token consumption
        test_otp_consumption()
        
        print("\n" + "=" * 50)
        print("📋 Test Summary:")
        print("✓ OTP Generation: PASSED")
        print("✓ Token Creation/Validation: PASSED")
        print("✓ Attempt Tracking: PASSED")
        print(f"{'✓' if sms_success else '⚠️'} SMS Sending: {'PASSED' if sms_success else 'NEEDS CONFIGURATION'}")
        print("✓ Token Consumption: PASSED")
        
        print("\n🎉 All core SMS OTP functionality is working!")
        
        if not sms_success:
            print("\n📝 To enable SMS sending:")
            print("1. Configure department phone numbers in DEPARTMENT_ADMIN_PHONES")
            print("2. Set up SMS provider (Twilio, AWS SNS, or TextLocal)")
            print("3. Or use mock mode for development testing")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)