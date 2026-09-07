"""
Standalone script to populate Agriculture and Borewell sector data with 4-level hierarchy.

Usage:
    python populate_agri_borewell.py

Structure:
    Sector → Service → Category (SubService, parent=None) → Items (SubService, parent=Category)
"""

import os
import django
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, SubService


def populate_data():
    """Populate Agriculture and Borewell sector data with 4-level hierarchy"""

    DATA = {
        "Agriculture": {
            "Agri Input Dealers (Vendors)": {
                "Seed Dealers": [
                    "Hybrid Seeds",
                    "Vegetable Seeds",
                    "Fruit Seeds",
                    "Grain Seeds",
                    "Fodder Seeds",
                    "Organic Seeds",
                ],
                "Fertilizer Dealers": [
                    "Urea",
                    "DAP",
                    "NPK Fertilizers",
                    "Potash",
                    "Micronutrients",
                    "Organic Fertilizers",
                    "Bio Fertilizers",
                ],
                "Crop Protection Dealers": [
                    "Insecticides",
                    "Fungicides",
                    "Herbicides",
                    "Weedicides",
                    "Plant Growth Regulators",
                    "Bio Pesticides",
                ],
                "Irrigation Dealers": [
                    "Drip Irrigation Kits",
                    "Sprinkler Systems",
                    "HDPE Pipes",
                    "PVC Pipes",
                    "Valves & Fittings",
                    "Filters",
                ],
                "Farm Tool Dealers": [
                    "Hand Tools",
                    "Power Tools",
                    "Sprayers",
                    "Pumps",
                    "Garden Equipment",
                ],
                "Animal & Dairy Inputs": [
                    "Cattle Feed",
                    "Poultry Feed",
                    "Mineral Mixtures",
                    "Veterinary Medicines",
                    "Dairy Equipment",
                ],
            },

            "Second-Hand Agriculture Equipment": {
                "Used Equipment": [
                    "Used Tractors",
                    "Used Rotavators",
                    "Used Harvesters",
                    "Used Seed Drills",
                    "Used Cultivators",
                    "Used Power Tillers",
                    "Used Sprayers",
                    "Used Pumps",
                    "Used Irrigation Systems",
                ]
            },
        },

        "Borewell": {
            "Borewell Equipment Dealers (New)": {
                "Pumps": [
                    "Submersible Pumps",
                    "Openwell Pumps",
                    "Monoblock Pumps",
                ],
                "Motors": [
                    "Submersible Motors",
                    "Surface Motors",
                ],
                "Pipes & Accessories": [
                    "HDPE Pipes",
                    "PVC Pipes",
                    "GI Pipes",
                    "Casing Pipes",
                    "Column Pipes",
                ],
                "Electrical": [
                    "Starter Panels",
                    "Control Panels",
                    "Pump Controllers",
                    "Cables",
                    "Capacitors",
                ],
                "Borewell Accessories": [
                    "Bore Caps",
                    "Clamps",
                    "Valves",
                    "Pipe Fittings",
                    "Cable Guards",
                ],
            },

            "Second-Hand Borewell Equipment": {
                "Used Equipment": [
                    "Used Drilling Rigs",
                    "Used Air Compressors",
                    "Used Mud Pumps",
                    "Used Submersible Pumps",
                    "Used Motors",
                    "Used Generators",
                    "Used Drill Rods",
                    "Used Borewell Cameras",
                    "Used Starter Panels",
                    "Used Control Panels",
                    "Used Pipe Handling Equipment",
                    "Used Water Tankers",
                ]
            },
        },
    }

    # Helper function to generate unique ID
    def generate_unique_id(base_name):
        """Generate a unique ID by appending a UUID suffix if needed"""
        clean_name = base_name.lower().replace(" ", "-")[:40]
        unique_id = clean_name

        # Check if ID exists, if so, append UUID
        counter = 1
        while SubService.objects.filter(id=unique_id[:50]).exists():
            unique_id = f"{clean_name}-{uuid.uuid4().hex[:8]}"
            counter += 1
            if counter > 100:
                # Fallback to full UUID
                unique_id = f"ss-{uuid.uuid4().hex[:45]}"
                break
        return unique_id[:50]

    # Counter for tracking created items
    stats = {
        'sectors': 0,
        'services': 0,
        'categories': 0,
        'items': 0,
        'updated_items': 0,
    }

    print("Starting population of Agriculture and Borewell data...\n")

    for sector_name, services_data in DATA.items():
        # Create or get Sector
        sector, created = Sector.objects.get_or_create(
            name=sector_name,
            defaults={
                'description': f'{sector_name} sector services',
                'icon': sector_name.lower()[0],
                'order': stats['sectors']
            }
        )
        if created:
            stats['sectors'] += 1
            print(f'+ Created Sector: {sector.name}')

        for service_name, categories_data in services_data.items():
            # Generate a unique ID for the service
            service_id_base = f"{sector.id[:20].lower()}-{service_name}".replace(" ", "-")
            service_id = service_id_base[:50]

            # Check if service exists by sector and name
            try:
                service = Service.objects.get(sector=sector, name=service_name)
            except Service.DoesNotExist:
                # Create with generated ID
                service = Service.objects.create(
                    id=service_id,
                    sector=sector,
                    name=service_name,
                    description=f'{service_name} - {sector_name}',
                    order=stats['services']
                )
                stats['services'] += 1
                print(f'  + Created Service: {service.name}')

            for category_name, items in categories_data.items():
                # Generate a unique ID for the category
                category_id_base = f"{service.id[:20].lower()}-{category_name}".replace(" ", "-")
                category_id = category_id_base[:50]

                # Check if category exists by service, name, and parent=None
                try:
                    category = SubService.objects.get(service=service, name=category_name, parent=None)
                except SubService.DoesNotExist:
                    # Create with generated ID
                    category = SubService.objects.create(
                        id=category_id,
                        service=service,
                        name=category_name,
                        parent=None,
                        description=f'{category_name} under {service.name}',
                        order=stats['categories']
                    )
                    stats['categories'] += 1
                    print(f'    + Created Category: {category.name}')

                for item_name in items:
                    # Check if item exists by service, name, and parent
                    try:
                        item = SubService.objects.get(service=service, name=item_name, parent=category)
                        # Update parent if it was None
                        if item.parent is None:
                            item.parent = category
                            item.save()
                            stats['updated_items'] += 1
                    except SubService.DoesNotExist:
                        # Generate a unique ID for the item
                        item_id_base = f"{service.id[:15].lower()}-{category.name[:15].lower()}-{item_name}".replace(" ", "-")
                        item_id = item_id_base[:50]

                        # Ensure ID is unique
                        while SubService.objects.filter(id=item_id).exists():
                            item_id = f"{item_id_base[:45]}-{uuid.uuid4().hex[:4]}"

                        # Create the item
                        item = SubService.objects.create(
                            id=item_id,
                            service=service,
                            name=item_name,
                            parent=category,
                            description=f'{item_name} - {category_name}',
                            order=stats['items']
                        )
                        stats['items'] += 1

    print("\n" + "=" * 60)
    print("Population Complete!")
    print(f"  Sectors: {stats['sectors']}")
    print(f"  Services: {stats['services']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Items: {stats['items']}")
    if stats['updated_items'] > 0:
        print(f"  Updated Items: {stats['updated_items']}")
    print("=" * 60)


if __name__ == "__main__":
    populate_data()
