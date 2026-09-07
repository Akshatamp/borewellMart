"""
Sectors, Services, and Subservices Population Script
Populates the database with sectors, services, and subservices from JSON data
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, ServiceCategory
from django.utils.text import slugify


def load_sectors_services_data():
    """Load sectors and services data from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'core/management/commands/sectors_services_data.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('sectors', [])


def populate_sectors_services():
    """Populate sectors, services, and subservices from JSON data"""
    print("="*60)
    print("Sectors, Services, and Subservices Population Script")
    print("="*60)

    sectors_data = load_sectors_services_data()

    total_sectors = 0
    total_services = 0
    total_subservices = 0

    for sector_data in sectors_data:
        # Create or update sector
        sector, created = Sector.objects.get_or_create(
            slug=sector_data['slug'],
            defaults={
                'name': sector_data['name'],
                'description': sector_data.get('description', ''),
            }
        )

        if created:
            print(f"\n✓ Created sector: {sector.name}")
            total_sectors += 1
        else:
            # Update description if sector exists
            sector.description = sector_data.get('description', '')
            sector.save()
            print(f"\n- Updated sector: {sector.name}")

        # Process services
        for service_data in sector_data.get('services', []):
            # Create or update service
            service, created = Service.objects.get_or_create(
                id=service_data['id'],
                defaults={
                    'sector': sector,
                    'name': service_data['name'],
                    'slug': service_data['slug'],
                    'description': service_data.get('description', ''),
                    'icon': service_data.get('icon', ''),
                }
            )

            if created:
                print(f"  ✓ Created service: {service.name}")
                total_services += 1
            else:
                # Update service details if it exists
                service.sector = sector
                service.name = service_data['name']
                service.slug = service_data['slug']
                service.description = service_data.get('description', '')
                service.icon = service_data.get('icon', '')
                service.save()
                print(f"  - Updated service: {service.name}")

            # Process subservices (ServiceCategory)
            for subservice_data in service_data.get('subservices', []):
                # Create or update subservice
                subservice, created = ServiceCategory.objects.get_or_create(
                    id=subservice_data['id'],
                    defaults={
                        'category': sector,
                        'name': subservice_data['name'],
                        'slug': subservice_data['slug'],
                        'description': subservice_data.get('description', ''),
                        'per_feet_amount': subservice_data.get('per_feet_amount', 0),
                    }
                )

                if created:
                    print(f"    ✓ Created subservice: {subservice.name}")
                    total_subservices += 1
                else:
                    # Update subservice details if it exists
                    subservice.category = sector
                    subservice.name = subservice_data['name']
                    subservice.slug = subservice_data['slug']
                    subservice.description = subservice_data.get('description', '')
                    subservice.per_feet_amount = subservice_data.get('per_feet_amount', 0)
                    subservice.save()
                    print(f"    - Updated subservice: {subservice.name}")

    print("\n" + "="*60)
    print("✓ Population completed successfully!")
    print("="*60)

    print("\nSummary:")
    print(f"  Sectors: {Sector.objects.count()}")
    print(f"  Services: {Service.objects.count()}")
    print(f"  Subservices: {ServiceCategory.objects.count()}")

    print("\nThis session:")
    print(f"  New sectors: {total_sectors}")
    print(f"  New services: {total_services}")
    print(f"  New subsservices: {total_subservices}")


def clear_existing_data():
    """Clear all existing sectors, services, and subservices"""
    print("\n" + "="*60)
    print("Clearing existing data...")
    print("="*60)

    subservice_count = ServiceCategory.objects.count()
    service_count = Service.objects.count()
    sector_count = Sector.objects.count()

    ServiceCategory.objects.all().delete()
    Service.objects.all().delete()
    Sector.objects.all().delete()

    print(f"✓ Deleted {subservice_count} subservices")
    print(f"✓ Deleted {service_count} services")
    print(f"✓ Deleted {sector_count} sectors")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_existing_data()
        print("\nRun script again without --clear to populate data.")
    else:
        populate_sectors_services()
