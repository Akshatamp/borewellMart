"""
Test sending actual WhatsApp message
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from django.conf import settings
import requests
import json

print("="*60)
print("WhatsApp Message Sending Test")
print("="*60)

# Test phone number (vendor phone from enquiry)
test_phone = "+917411484528"

# Format phone number
def format_whatsapp_number(phone):
    """Format phone number for WhatsApp"""
    phone = phone.strip()
    # Remove all non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # If it's a 10-digit Indian number, add +91
    if len(phone) == 10:
        phone = '91' + phone
    # If it's already 12 digits and starts with 91, use as is
    elif len(phone) == 12 and phone.startswith('91'):
        pass
    # If it's 11 digits and starts with 0, remove 0 and add 91
    elif len(phone) == 11 and phone.startswith('0'):
        phone = '91' + phone[1:]
    
    return phone

to_number = format_whatsapp_number(test_phone)
print(f"\nTest phone number: {test_phone}")
print(f"Formatted for WhatsApp: {to_number}")

# Try sending a simple text message
url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
headers = {
    'Authorization': f'Bearer {settings.WHATSAPP_CLOUD_TOKEN}',
    'Content-Type': 'application/json',
}

# Test with template
template_name = settings.WHATSAPP_TEMPLATE_NAME
payload = {
    'messaging_product': 'whatsapp',
    'to': to_number,
    'type': 'template',
    'template': {
        'name': template_name,
        'language': {'code': settings.WHATSAPP_TEMPLATE_LANGUAGE},
        'components': [
            {
                'type': 'body',
                'parameters': [
                    {'type': 'text', 'text': 'Test Customer'},
                    {'type': 'text', 'text': 'Test Service'},
                    {'type': 'text', 'text': 'Test message content'},
                    {'type': 'text', 'text': 'Test Vendor'},
                ],
            }
        ],
    },
}

print(f"\nSending template message: {template_name}")
print(f"URL: {url}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.ok:
        print(f"\n✓ Message sent successfully!")
        response_data = response.json()
        print(f"Message ID: {response_data.get('messages', [{}])[0].get('id')}")
    else:
        print(f"\n✗ Message sending failed")
        error_data = response.json() if response.content else {}
        print(f"Error: {error_data}")
        
except Exception as e:
    print(f"\n✗ Exception occurred: {e}")

print("\n" + "="*60)
