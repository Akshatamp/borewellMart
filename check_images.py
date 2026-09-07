#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City, Sector, Service, SubService

print("Checking image status...\n")

# Check cities
print("Cities with images:")
cities_with_images = City.objects.exclude(image='').exclude(image__isnull=True)
print(f"  Total cities: {City.objects.count()}")
print(f"  Cities with images: {cities_with_images.count()}")

for city in cities_with_images[:5]:
    print(f"    {city.name}: {city.image.name if city.image else 'No image'}")

# Check sectors
print("\nSectors with images:")
sectors_with_images = Sector.objects.exclude(image='').exclude(image__isnull=True)
print(f"  Total sectors: {Sector.objects.count()}")
print(f"  Sectors with images: {sectors_with_images.count()}")

for sector in sectors_with_images[:5]:
    print(f"    {sector.name}: {sector.image.name if sector.image else 'No image'}")

# Check services
print("\nServices with images:")
services_with_images = Service.objects.exclude(image='').exclude(image__isnull=True)
print(f"  Total services: {Service.objects.count()}")
print(f"  Services with images: {services_with_images.count()}")

for service in services_with_images[:5]:
    print(f"    {service.name}: {service.image.name if service.image else 'No image'}")

# Check subservices
print("\nSubServices with images:")
subservices_with_images = SubService.objects.exclude(image='').exclude(image__isnull=True)
print(f"  Total subservices: {SubService.objects.count()}")
print(f"  Subservices with images: {subservices_with_images.count()}")
