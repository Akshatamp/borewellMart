"""
Test WhatsApp sending for a specific enquiry
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Enquiry
from core.utils import send_whatsapp_enquiry_notification

print("="*60)
print("Testing WhatsApp for Recent Enquiry")
print("="*60)

# Get the most recent enquiry
enquiry = Enquiry.objects.order_by('-created_at').first()

if enquiry:
    print(f"\nEnquiry Details:")
    print(f"  ID: {enquiry.id}")
    print(f"  Customer: {enquiry.customer.username}")
    print(f"  Vendor: {enquiry.vendor.company_name}")
    print(f"  Vendor Phone: {enquiry.vendor.phone}")
    print(f"  Subservice: {enquiry.subservice.name}")
    print(f"  Message: {enquiry.message}")
    print(f"  Created: {enquiry.created_at}")
    
    print(f"\nAttempting WhatsApp notification...")
    success, result = send_whatsapp_enquiry_notification(enquiry)
    
    print(f"\nResult:")
    print(f"  Success: {success}")
    print(f"  Result: {result}")
else:
    print("No enquiries found")

print("\n" + "="*60)
