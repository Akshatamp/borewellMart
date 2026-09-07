"""
Test Twilio SMS sending
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from django.conf import settings

print("="*60)
print("Twilio SMS Configuration Test")
print("="*60)

print(f"\nTwilio Settings:")
print(f"  Account SID: {settings.TWILIO_ACCOUNT_SID}")
print(f"  Auth Token configured: {bool(settings.TWILIO_AUTH_TOKEN)}")
print(f"  From Number: {settings.TWILIO_FROM_NUMBER}")

# Test sending SMS
test_phone = "+917411484528"
test_message = "Test message from BoreWell platform. This is a test SMS notification."

print(f"\nTest phone: {test_phone}")
print(f"Message: {test_message}")

if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER:
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        print(f"\nSending SMS...")
        message = client.messages.create(
            body=test_message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=test_phone
        )
        
        print(f"\n✓ SMS sent successfully!")
        print(f"  Message SID: {message.sid}")
        print(f"  Status: {message.status}")
        print(f"  To: {message.to}")
        print(f"  From: {message.from_}")
        
    except Exception as e:
        print(f"\n✗ SMS sending failed: {e}")
else:
    print(f"\n✗ Twilio credentials not configured")

print("\n" + "="*60)
