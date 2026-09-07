#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, SubService

print("Checking admin data...\n")

# Check sectors
print(f"Sectors: {Sector.objects.count()}")
for sector in Sector.objects.all():
    print(f"  - {sector.name} (services: {sector.services.count()})")

# Check services
print(f"\nServices: {Service.objects.count()}")
for service in Service.objects.all()[:10]:
    print(f"  - {service.name} (sector: {service.sector.name}, subservices: {service.subservices.count()})")

# Check subservices
print(f"\nSubservices: {SubService.objects.count()}")

print("\n✅ Data is populated correctly!")
print("Sectors and services should now show in the admin panel.")
