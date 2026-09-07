#!/usr/bin/env python
"""
Remove vendors linked to subservices, then delete all sectors, services, and subservices
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Vendor, VendorService, SubService, Service, Sector

print("Starting cleanup...\n")

# Step 1: Delete vendors that have vendor_service links
print("Step 1: Deleting vendors with service links...")
vendors_with_services = Vendor.objects.filter(vendor_services__isnull=False).distinct()
vendors_count = vendors_with_services.count()
print(f"Found {vendors_count} vendors with service links")

for vendor in vendors_with_services:
    print(f"  Deleting: {vendor.company_name}")
    vendor.delete()

print(f"✓ Deleted {vendors_count} vendors\n")

# Step 2: Delete all subservices
print("Step 2: Deleting all subservices...")
subservices_count = SubService.objects.count()
print(f"Found {subservices_count} subservices")
SubService.objects.all().delete()
print(f"✓ Deleted {subservices_count} subservices\n")

# Step 3: Delete all services
print("Step 3: Deleting all services...")
services_count = Service.objects.count()
print(f"Found {services_count} services")
Service.objects.all().delete()
print(f"✓ Deleted {services_count} services\n")

# Step 4: Delete all sectors
print("Step 4: Deleting all sectors...")
sectors_count = Sector.objects.count()
print(f"Found {sectors_count} sectors")
Sector.objects.all().delete()
print(f"✓ Deleted {sectors_count} sectors\n")

print("="*60)
print("Cleanup Complete!")
print("="*60)
print(f"Summary:")
print(f"  Vendors deleted: {vendors_count}")
print(f"  Subservices deleted: {subservices_count}")
print(f"  Services deleted: {services_count}")
print(f"  Sectors deleted: {sectors_count}")
print("="*60)
