#!/usr/bin/env python
"""
Test script to verify forgot password page is accessible
"""
import requests
import sys

def test_forgot_password_page():
    """Test that the forgot password page loads correctly"""
    print("🔍 Testing Forgot Password Page")
    print("=" * 40)
    
    try:
        # Test the forgot password page
        response = requests.get('http://localhost:5000/forgot-password', timeout=10)
        
        if response.status_code == 200:
            print("✅ Page loads successfully!")
            
            # Check if SMS OTP content is present
            page_content = response.text.lower()
            
            checks = [
                ("SMS OTP Password Reset", "sms otp password reset" in page_content),
                ("📱 Icon", "📱" in response.text),
                ("Send OTP via SMS button", "send otp via sms" in page_content),
                ("OTP verification form", "otp-verification" in page_content),
                ("Service Desk department", "service desk" in page_content),
            ]
            
            print("\n📋 Content Checks:")
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("\n🎉 All SMS OTP content is present on the page!")
                print("\n🌐 Visit: http://localhost:5000/forgot-password")
                print("   Select 'Service Desk' department to test your number")
            else:
                print("\n⚠️  Some SMS OTP content might be missing")
                
        else:
            print(f"❌ Page failed to load: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is Flask running on http://localhost:5000?")
        print("💡 Run: python app.py")
    except Exception as e:
        print(f"❌ Error testing page: {str(e)}")

if __name__ == "__main__":
    test_forgot_password_page()