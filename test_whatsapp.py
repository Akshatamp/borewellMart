"""
Test WhatsApp Cloud API Configuration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from django.conf import settings
import requests

print("="*60)
print("WhatsApp Cloud API Configuration Test")
print("="*60)

# Check settings
print(f"\nWhatsApp Settings:")
print(f"  API URL: {settings.WHATSAPP_CLOUD_API_URL}")
print(f"  Phone Number ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
print(f"  Business Account ID: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
print(f"  Token configured: {bool(settings.WHATSAPP_CLOUD_TOKEN)}")
print(f"  Template Name: {settings.WHATSAPP_TEMPLATE_NAME}")
print(f"  Template Language: {settings.WHATSAPP_TEMPLATE_LANGUAGE}")

# Test API connection
if settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_CLOUD_TOKEN:
    print(f"\nTesting API connection...")
    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_CLOUD_TOKEN}',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"  Response Status: {response.status_code}")
        print(f"  Response Body: {response.text[:500]}")
        
        if response.ok:
            print(f"  ✓ API connection successful")
        else:
            print(f"  ✗ API connection failed")
    except Exception as e:
        print(f"  ✗ API connection error: {e}")
else:
    print(f"\n✗ WhatsApp credentials not configured")

print("\n" + "="*60)
