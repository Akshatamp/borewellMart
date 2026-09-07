"""
Test sending WhatsApp text message (fallback)
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from django.conf import settings
import requests

print("="*60)
print("WhatsApp Text Message Test (Fallback)")
print("="*60)

test_phone = "+917411484528"

def format_whatsapp_number(phone):
    phone = phone.strip()
    phone = ''.join(filter(str.isdigit, phone))
    if len(phone) == 10:
        phone = '91' + phone
    elif len(phone) == 12 and phone.startswith('91'):
        pass
    elif len(phone) == 11 and phone.startswith('0'):
        phone = '91' + phone[1:]
    return phone

to_number = format_whatsapp_number(test_phone)
print(f"\nTest phone: {test_phone}")
print(f"Formatted: {to_number}")

url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
headers = {
    'Authorization': f'Bearer {settings.WHATSAPP_CLOUD_TOKEN}',
    'Content-Type': 'application/json',
}

# Send text message
payload = {
    'messaging_product': 'whatsapp',
    'to': to_number,
    'type': 'text',
    'text': {
        'body': 'Test message from BoreWell platform. This is a test enquiry notification.'
    }
}

print(f"\nSending text message...")
try:
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.ok:
        print(f"\n✓ Text message sent successfully!")
    else:
        print(f"\n✗ Text message failed")
except Exception as e:
    print(f"\n✗ Exception: {e}")

print("\n" + "="*60)
