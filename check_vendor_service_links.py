#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Vendor, VendorService, SubService
from django.db.models import Count

print("Checking Vendor-Service Links...\n")

# Check vendors with services
vendors_with_services = Vendor.objects.annotate(
    service_count=Count('vendor_services')
).filter(service_count__gt=0)

print(f"Vendors with services: {vendors_with_services.count()}")
print(f"Total vendor services: {VendorService.objects.count()}")

print("\nFirst 5 vendor-service links:")
for vs in VendorService.objects.all()[:5]:
    vendor = vs.vendor.company_name
    subservice = vs.subservice.name
    subservice_id = vs.subservice.id
    print(f"  {vendor} -> {subservice} (ID: {subservice_id})")

print("\nBreakdown by vendor:")
for vendor in vendors_with_services[:10]:
    services = VendorService.objects.filter(vendor=vendor)
    print(f"  {vendor.company_name}: {services.count()} services")
    for vs in services:
        print(f"    - {vs.subservice.name} (ID: {vs.subservice.id})")
