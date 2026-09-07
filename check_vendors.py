#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Vendor, VendorService, SubService

print('Total vendors:', Vendor.objects.count())
print('Total vendor services:', VendorService.objects.count())

print('\nVendor services breakdown:')
for vendor in Vendor.objects.all():
    services = VendorService.objects.filter(vendor=vendor).count()
    print(f'  {vendor.company_name}: {services} services')
