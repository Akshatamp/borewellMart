#!/usr/bin/env python
"""
Link existing media images to City and Service models
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City, Service, Sector
from django.core.files import File
import glob

# Map city names to their image files
city_image_mapping = {
    'Hubli': 'cities/hubli_resized_compressed.jpg',
    'Dharwad': 'cities/Dharwad_resized_compressed.jpg',
    'Bangalore': 'cities/bangalore_resized_compressed.jpg',
    'Belagavi': 'cities/belaguam_resized_compressed.jpg',
    'Mangalore': 'cities/mangalore_resized_compressed.jpg',
    'Mysuru': 'cities/mysore_resized_compressed.jpg',
    'Vijayapura': 'cities/Vijayapura_resized_compressed.jpg',
    'Raichur': 'cities/Raichur_resized_compressed.jpg',
    'Kalaburagi': 'cities/Kalaburagi_resized_compressed.jpg',
    'Bidar': 'cities/Bidar_resized_compressed.jpg',
    'Shivamogga': 'cities/Shivamogga_resized_compressed.jpg',
    'Ballari': 'cities/Ballari_resized_compressed.jpg',
}

# Map service names to their image files
service_image_mapping = {
    'Irrigation Solutions': 'service_subcategories/Irrigation_Solutions_resized_compressed.jpg',
    'Borewell Survey & Site Selection': 'service_subcategories/Borewell_Survey__Site_Selection_resized_compressed.jpg',
    'Agricultural Borewells': 'service_subcategories/Agricultural_Borewells_resized_compressed.jpg',
    'Borewell Drilling': 'service_subcategories/Borewell_Drillin_resized_compressed.jpg',
    'Solar Farming Solutions': 'service_subcategories/Solar_Farming_Solutions_resized_compressed.jpg',
    'Borewell Casing Services': 'service_subcategories/Borewell_Casing_Services_resized_compressed.jpg',
    'Farm Water Management': 'service_subcategories/Farm_Water_Management_resized_compressed.jpg',
    'Borewell Development': 'service_subcategories/Borewell_Development_resized_compressed.jpg',
    'Groundwater & Soil Services': 'service_subcategories/Groundwater__Soil_Services_resized_compressed.jpg',
    'Pump Installation & Maintenance': 'service_subcategories/Pump_Installation__Maintenance_resized_compressed.jpg',
    'Precision Agriculture': 'service_subcategories/Precision_Agriculture_resized_compressed.jpg',
    'Water Yield Testing': 'service_subcategories/Water_Yield_Testing_resized_compressed.jpg',
    'Water Quality Testing': 'service_subcategories/Water_Quality_Testing_resized_compressed.jpg',
    'Borewell Rehabilitation & Repair': 'service_subcategories/Borewell_Rehabilitation__Repair_resized_compressed.jpg',
    'Rainwater Harvesting Integration': 'service_subcategories/Rainwater_Harvesting_Integration_resized_compressed.jpg',
    'Solar Water Solutions': 'service_subcategories/Solar_Water_Solutions_resized_compressed.jpg',
    'Pipeline & Irrigation Services': 'service_subcategories/Pipeline__Irrigation_Services_resized_compressed.jpg',
    'Borewell Monitoring & Automation': 'service_subcategories/Borewell_Monitoring__Automation_resized_compressed.jpg',
    'Environmental & Compliance Services': 'service_subcategories/Environmental__Compliance_Services_resized_compressed.jpg',
}

# Map sector names to their image files (using relevant service images)
sector_image_mapping = {
    'Agriculture': 'service_subcategories/Irrigation_Solutions_resized_compressed.jpg',
    'Borewell': 'service_subcategories/Borewell_Drillin_resized_compressed.jpg',
}

print("Linking images to models...\n")

# Link city images
cities_updated = 0
for city in City.objects.all():
    if city.name in city_image_mapping:
        image_path = city_image_mapping[city.name]
        full_path = f'media/{image_path}'
        if os.path.exists(full_path):
            try:
                with open(full_path, 'rb') as f:
                    city.image.save(image_path, File(f), save=True)
                cities_updated += 1
                print(f'✓ Linked image for city: {city.name}')
            except Exception as e:
                print(f'✗ Error linking image for {city.name}: {e}')

# Link service images
services_updated = 0
for service in Service.objects.all():
    if service.name in service_image_mapping:
        image_path = service_image_mapping[service.name]
        full_path = f'media/{image_path}'
        if os.path.exists(full_path):
            try:
                with open(full_path, 'rb') as f:
                    service.image.save(image_path, File(f), save=True)
                services_updated += 1
                print(f'✓ Linked image for service: {service.name}')
            except Exception as e:
                print(f'✗ Error linking image for {service.name}: {e}')

# Link sector images
sectors_updated = 0
for sector in Sector.objects.all():
    if sector.name in sector_image_mapping:
        image_path = sector_image_mapping[sector.name]
        full_path = f'media/{image_path}'
        if os.path.exists(full_path):
            try:
                with open(full_path, 'rb') as f:
                    sector.image.save(image_path, File(f), save=True)
                sectors_updated += 1
                print(f'✓ Linked image for sector: {sector.name}')
            except Exception as e:
                print(f'✗ Error linking image for {sector.name}: {e}')

print(f'\nSummary:')
print(f'  Cities updated: {cities_updated}/{City.objects.count()}')
print(f'  Services updated: {services_updated}/{Service.objects.count()}')
print(f'  Sectors updated: {sectors_updated}/{Sector.objects.count()}')
