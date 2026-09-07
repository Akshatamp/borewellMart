import uuid
from django.core.management.base import BaseCommand
from core.models import Sector, Service, SubService


class Command(BaseCommand):
    help = 'Populate Agriculture and Borewell sector data with 4-level hierarchy'

    def handle(self, *args, **options):
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
                        {
                            "name": "Submersible Pumps",
                            "per_feet_amount": 150,
                            "features": ["High efficiency", "Corrosion resistant", "Long life"]
                        },
                        {
                            "name": "Openwell Pumps",
                            "per_feet_amount": 120,
                            "features": ["Easy installation", "Low maintenance", "Energy efficient"]
                        },
                        {
                            "name": "Monoblock Pumps",
                            "per_feet_amount": 100,
                            "features": ["Compact design", "High performance", "Durable"]
                        },
                    ],
                    "Motors": [
                        {
                            "name": "Submersible Motors",
                            "per_feet_amount": 200,
                            "features": ["Water cooled", "High torque", "Low noise"]
                        },
                        {
                            "name": "Surface Motors",
                            "per_feet_amount": 180,
                            "features": ["Air cooled", "Easy repair", "Cost effective"]
                        },
                    ],
                    "Pipes & Accessories": [
                        {
                            "name": "HDPE Pipes",
                            "per_feet_amount": 50,
                            "features": ["UV resistant", "Leak proof", "Flexible"]
                        },
                        {
                            "name": "PVC Pipes",
                            "per_feet_amount": 40,
                            "features": ["Light weight", "Easy to install", "Chemical resistant"]
                        },
                        {
                            "name": "GI Pipes",
                            "per_feet_amount": 80,
                            "features": ["Strong", "Long lasting", "Heat resistant"]
                        },
                        {
                            "name": "Casing Pipes",
                            "per_feet_amount": 60,
                            "features": ["High strength", "Smooth bore", "Corrosion resistant"]
                        },
                        {
                            "name": "Column Pipes",
                            "per_feet_amount": 55,
                            "features": ["Heavy duty", "Precision engineered", "Threaded joints"]
                        },
                    ],
                    "Electrical": [
                        {
                            "name": "Starter Panels",
                            "per_feet_amount": 500,
                            "features": ["Auto start", "Overload protection", "Phase monitoring"]
                        },
                        {
                            "name": "Control Panels",
                            "per_feet_amount": 600,
                            "features": ["Digital display", "Remote control", "Multi-stage protection"]
                        },
                        {
                            "name": "Pump Controllers",
                            "per_feet_amount": 450,
                            "features": ["Automatic operation", "Dry run protection", "Level sensing"]
                        },
                        {
                            "name": "Cables",
                            "per_feet_amount": 30,
                            "features": ["Waterproof", "Heat resistant", "High conductivity"]
                        },
                        {
                            "name": "Capacitors",
                            "per_feet_amount": 200,
                            "features": ["High capacity", "Long life", "Low loss"]
                        },
                    ],
                    "Borewell Accessories": [
                        {
                            "name": "Bore Caps",
                            "per_feet_amount": 150,
                            "features": ["Stainless steel", "Lockable", "Weather proof"]
                        },
                        {
                            "name": "Clamps",
                            "per_feet_amount": 50,
                            "features": ["Heavy duty", "Rust proof", "Easy to adjust"]
                        },
                        {
                            "name": "Valves",
                            "per_feet_amount": 100,
                            "features": ["Leak proof", "High pressure", "Easy operation"]
                        },
                        {
                            "name": "Pipe Fittings",
                            "per_feet_amount": 40,
                            "features": ["Universal fit", "Durable", "Easy installation"]
                        },
                        {
                            "name": "Cable Guards",
                            "per_feet_amount": 60,
                            "features": ["Protective", "UV resistant", "Long lasting"]
                        },
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
        }

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
                self.stdout.write(self.style.SUCCESS(f'+ Created Sector: {sector.name}'))

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
                    self.stdout.write(self.style.SUCCESS(f'  + Created Service: {service.name}'))

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
                        self.stdout.write(self.style.SUCCESS(f'    + Created Category: {category.name}'))

                    # Add per_feet_amount and features for Borewell Equipment Dealers categories
                    if service.name == "Borewell Equipment Dealers (New)":
                        category_data = {
                            "Pumps": {"per_feet_amount": 150, "features": ["Wide range", "Energy efficient", "Durable"]},
                            "Motors": {"per_feet_amount": 200, "features": ["High performance", "Long life", "Low maintenance"]},
                            "Pipes & Accessories": {"per_feet_amount": 60, "features": ["Quality material", "Leak proof", "Easy installation"]},
                            "Electrical": {"per_feet_amount": 400, "features": ["Safe operation", "Reliable", "Easy to use"]},
                            "Borewell Accessories": {"per_feet_amount": 100, "features": ["Essential parts", "High quality", "Long lasting"]},
                        }
                        if category_name in category_data:
                            # Update if per_feet_amount or features are not set
                            if category.per_feet_amount is None or not category.features:
                                category.per_feet_amount = category_data[category_name]["per_feet_amount"]
                                category.features = category_data[category_name]["features"]
                                category.save()
                                self.stdout.write(self.style.SUCCESS(f'    + Updated Category: {category.name}'))

                    for item_data in items:
                        # Handle both string and dict formats
                        if isinstance(item_data, str):
                            item_name = item_data
                            per_feet_amount = None
                            features = []
                        else:
                            item_name = item_data.get('name')
                            per_feet_amount = item_data.get('per_feet_amount')
                            features = item_data.get('features', [])

                        # Check if item exists by service, name, and parent
                        try:
                            item = SubService.objects.get(service=service, name=item_name, parent=category)
                            # Update parent if it was None
                            if item.parent is None:
                                item.parent = category
                                item.save()
                            # Update per_feet_amount and features if not set
                            if per_feet_amount and item.per_feet_amount is None:
                                item.per_feet_amount = per_feet_amount
                                item.save()
                            if features and not item.features:
                                item.features = features
                                item.save()
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
                                per_feet_amount=per_feet_amount,
                                features=features,
                                order=stats['items']
                            )
                            stats['items'] += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*60}\n'
            f'Population Complete!\n'
            f'  Sectors: {stats["sectors"]}\n'
            f'  Services: {stats["services"]}\n'
            f'  Categories: {stats["categories"]}\n'
            f'  Items: {stats["items"]}\n'
            f'{"="*60}'
        ))
