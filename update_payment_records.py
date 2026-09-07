"""
Management command to update existing payment records with missing data.
Run this on production server: python manage.py update_payment_records
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/home/agrikart/BoreWell')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewell.settings')
django.setup()

from core.models import VendorPayment
from django.utils import timezone

def update_payment_records():
    """Update existing payment records with missing data"""

    print("Starting payment record update...")

    # Update payments with missing payment_method
    # For payments with razorpay_order_id, set payment_method to 'razorpay'
    updated_method = VendorPayment.objects.filter(
        payment_method__isnull=True
    ).exclude(razorpay_order_id__isnull=True).exclude(razorpay_order_id='').update(payment_method='razorpay')

    print(f"✓ Updated {updated_method} payments with payment_method='razorpay'")

    # For payments without razorpay_order_id but pending/completed, set to 'other'
    updated_other = VendorPayment.objects.filter(
        payment_method__isnull=True
    ).filter(
        status__in=['pending', 'completed']
    ).update(payment_method='other')

    print(f"✓ Updated {updated_other} payments with payment_method='other'")

    # Update completed payments with missing payment_date
    # Use created_at as fallback for payment_date
    completed_payments = VendorPayment.objects.filter(
        status='completed'
    ).filter(payment_date__isnull=True)

    count = 0
    for payment in completed_payments:
        payment.payment_date = payment.created_at
        payment.save(update_fields=['payment_date'])
        count += 1

    print(f"✓ Updated {count} completed payments with payment_date")

    # Generate transaction IDs for completed payments missing them
    completed_no_tid = VendorPayment.objects.filter(
        status='completed'
    ).filter(transaction_id__isnull=True).filter(transaction_id='')

    tid_count = 0
    for payment in completed_no_tid:
        payment.transaction_id = f'MANUAL_{payment.id}_{payment.created_at.strftime("%Y%m%d%H%M%S")}'
        payment.save(update_fields=['transaction_id'])
        tid_count += 1

    print(f"✓ Generated {tid_count} transaction IDs for completed payments")

    # Show summary
    total = VendorPayment.objects.count()
    pending = VendorPayment.objects.filter(status='pending').count()
    completed = VendorPayment.objects.filter(status='completed').count()

    print(f"\n=== Payment Summary ===")
    print(f"Total payments: {total}")
    print(f"Pending: {pending}")
    print(f"Completed: {completed}")

    # Show sample of updated records
    print(f"\n=== Sample Updated Records ===")
    for payment in VendorPayment.objects.all()[:5]:
        print(f"Payment #{payment.id}: {payment.vendor.company_name}")
        print(f"  Status: {payment.status}")
        print(f"  Method: {payment.payment_method}")
        print(f"  Transaction ID: {payment.transaction_id}")
        print(f"  Payment Date: {payment.payment_date}")
        print()

if __name__ == '__main__':
    update_payment_records()
    print("Payment record update completed!")
