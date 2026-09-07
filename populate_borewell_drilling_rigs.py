"""
Borewell Drilling Rigs Population Script
Populates the database with Borewell Drilling Rigs service and subservices
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, SubService
from django.utils.text import slugify

DATA = {
    'Borewell': {
        'Borewell Drilling Rigs': {
            'Borewell Drilling Rigs': [{'name': 'Borewell Drilling Rigs', 'description': 'Borewell Drilling Rigs', 'features': ['Heavy duty', 'Deep drilling', 'High efficiency']}],
            'Truck Mounted Rigs': [{'name': 'Truck Mounted Rigs', 'description': 'Truck Mounted Rigs', 'features': ['Mobile', 'Easy transport', 'Powerful']}],
            'Tractor Mounted Rigs': [{'name': 'Tractor Mounted Rigs', 'description': 'Tractor Mounted Rigs', 'features': ['Compact', 'Versatile', 'Cost effective']}],
            'Crawler Mounted Rigs': [{'name': 'Crawler Mounted Rigs', 'description': 'Crawler Mounted Rigs', 'features': ['All terrain', 'Stable', 'Heavy duty']}],
            'Trailer Mounted Rigs': [{'name': 'Trailer Mounted Rigs', 'description': 'Trailer Mounted Rigs', 'features': ['Portable', 'Easy setup', 'Flexible']}],
            'Mini Drilling Rigs': [{'name': 'Mini Drilling Rigs', 'description': 'Mini Drilling Rigs', 'features': ['Compact', 'Lightweight', 'Easy handling']}],
            'Air Compressors': [{'name': 'Air Compressors', 'description': 'Air Compressors', 'features': ['High pressure', 'Reliable', 'Fuel efficient']}],
            'DTH Hammers': [{'name': 'DTH Hammers', 'description': 'DTH Hammers', 'features': ['Down the hole', 'Fast drilling', 'Durable']}],
            'Drill Rods': [{'name': 'Drill Rods', 'description': 'Drill Rods', 'features': ['High strength', 'Various lengths', 'Quality steel']}],
            'Drill Bits': [{'name': 'Drill Bits', 'description': 'Drill Bits', 'features': ['Various sizes', 'Tungsten carbide', 'Long life']}],
            'Mud Pumps': [{'name': 'Mud Pumps', 'description': 'Mud Pumps', 'features': ['High flow', 'Heavy duty', 'Reliable']}],
            'Hydraulic Power Packs': [{'name': 'Hydraulic Power Packs', 'description': 'Hydraulic Power Packs', 'features': ['High power', 'Efficient', 'Compact']}],
            'Generators': [{'name': 'Generators', 'description': 'Generators', 'features': ['Various capacities', 'Fuel efficient', 'Reliable']}],
            'Borewell Cameras': [{'name': 'Borewell Cameras', 'description': 'Borewell Cameras', 'features': ['HD video', 'LED lighting', 'Depth measurement']}],
            'Borewell Cleaning Machines': [{'name': 'Borewell Cleaning Machines', 'description': 'Borewell Cleaning Machines', 'features': ['High pressure', 'Effective cleaning', 'Portable']}],
            'Water Pumps': [{'name': 'Water Pumps', 'description': 'Water Pumps', 'features': ['High flow', 'Energy efficient', 'Various types']}],
            'Casing Pipes': [{'name': 'Casing Pipes', 'description': 'Casing Pipes', 'features': ['Heavy duty', 'Various diameters', 'PVC/Steel']}],
            'Winches': [{'name': 'Winches', 'description': 'Winches', 'features': ['High capacity', 'Smooth operation', 'Safe']}],
            'Welding Machines': [{'name': 'Welding Machines', 'description': 'Welding Machines', 'features': ['Portable', 'Various types', 'Reliable']}],
            'Spare Parts': [{'name': 'Spare Parts', 'description': 'Spare Parts', 'features': ['Genuine parts', 'Wide range', 'Quality assured']}]
        }
    }
}


def populate_borewell_drilling_rigs():
    """Populate Borewell Drilling Rigs service and subservices"""
    print("="*60)
    print("Borewell Drilling Rigs Population Script")
    print("="*60)

    total_sectors = 0
    total_services = 0
    total_subservices = 0

    for sector_name, services_data in DATA.items():
        # Create or update sector
        sector, created = Sector.objects.get_or_create(
            slug=slugify(sector_name),
            defaults={
                'name': sector_name,
                'description': f'{sector_name} services',
                'order': 1,
            }
        )

        if created:
            print(f"\n✓ Created sector: {sector.name}")
            total_sectors += 1
        else:
            print(f"\n- Found existing sector: {sector.name}")

        # Process services
        for service_name, subservices_data in services_data.items():
            # Generate unique ID
            base_id = slugify(service_name)
            id = base_id
            counter = 1
            while Service.objects.filter(id=id).exists():
                id = f"{base_id}-{counter}"
                counter += 1

            # Create or update service
            service, created = Service.objects.get_or_create(
                id=id,
                defaults={
                    'sector': sector,
                    'name': service_name,
                    'slug': slugify(service_name),
                    'description': f'{service_name} services',
                    'icon': '',
                    'order': 1,
                }
            )

            if created:
                print(f"  ✓ Created service: {service.name}")
                total_services += 1
            else:
                print(f"  - Found existing service: {service.name}")

            # Process subservices
            for subservice_list in subservices_data.values():
                for subservice_data in subservice_list:
                    # Generate unique ID
                    base_id = slugify(subservice_data['name'])
                    id = base_id
                    counter = 1
                    while SubService.objects.filter(id=id).exists():
                        id = f"{base_id}-{counter}"
                        counter += 1

                    # Create or update subservice
                    subservice, created = SubService.objects.get_or_create(
                        id=id,
                        defaults={
                            'service': service,
                            'name': subservice_data['name'],
                            'description': subservice_data.get('description', ''),
                            'features': subservice_data.get('features', []),
                            'popular': False,
                            'order': 1,
                        }
                    )

                    if created:
                        print(f"    ✓ Created subservice: {subservice.name} (ID: {id})")
                        total_subservices += 1
                    else:
                        # Update subservice details if it exists
                        subservice.service = service
                        subservice.name = subservice_data['name']
                        subservice.description = subservice_data.get('description', '')
                        subservice.features = subservice_data.get('features', [])
                        subservice.save()
                        print(f"    - Updated subservice: {subservice.name} (ID: {id})")

    print("\n" + "="*60)
    print("✓ Population completed successfully!")
    print("="*60)

    print("\nSummary:")
    print(f"  Sectors: {Sector.objects.count()}")
    print(f"  Services: {Service.objects.count()}")
    print(f"  Subservices: {SubService.objects.count()}")

    print("\nThis session:")
    print(f"  New sectors: {total_sectors}")
    print(f"  New services: {total_services}")
    print(f"  New subservices: {total_subservices}")


if __name__ == "__main__":
    populate_borewell_drilling_rigs()
