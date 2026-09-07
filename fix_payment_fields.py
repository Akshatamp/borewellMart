"""
Quick fix script for payment fields - Run this on production server
Usage: cd /home/agrikart/BoreWell && python fix_payment_fields.py
"""
import os
import sys
import django

sys.path.append('/home/agrikart/BoreWell')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewell.settings')
django.setup()

from core.models import VendorPayment

print("Fixing payment fields...")

# Fix payment_method - set to 'razorpay' for payments with razorpay_order_id
razorpay_payments = VendorPayment.objects.filter(
    payment_method__isnull=True
).exclude(razorpay_order_id__isnull=True).exclude(razorpay_order_id='')
count1 = razorpay_payments.update(payment_method='razorpay')
print(f"✓ Set payment_method='razorpay' for {count1} payments")

# Fix payment_method - set to 'other' for other payments
other_payments = VendorPayment.objects.filter(
    payment_method__isnull=True
)
count2 = other_payments.update(payment_method='other')
print(f"✓ Set payment_method='other' for {count2} payments")

# Fix payment_date for completed payments
completed = VendorPayment.objects.filter(status='completed').filter(payment_date__isnull=True)
count3 = 0
for p in completed:
    p.payment_date = p.created_at
    p.save(update_fields=['payment_date'])
    count3 += 1
print(f"✓ Set payment_date for {count3} completed payments")

# Fix transaction_id for completed payments
no_tid = VendorPayment.objects.filter(status='completed').filter(
    transaction_id__isnull=True).filter(transaction_id='')
count4 = 0
for p in no_tid:
    p.transaction_id = f'PAY_{p.id}'
    p.save(update_fields=['transaction_id'])
    count4 += 1
print(f"✓ Generated transaction_id for {count4} payments")

print("\n=== Summary ===")
print(f"Total payments: {VendorPayment.objects.count()}")
print(f"Completed: {VendorPayment.objects.filter(status='completed').count()}")
print(f"Pending: {VendorPayment.objects.filter(status='pending').count()}")

print("\nDone! Payment fields fixed.")
