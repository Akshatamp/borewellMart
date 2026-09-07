#!/usr/bin/env python
"""
Populate complete service hierarchy based on BorewellMart structure
Only adds missing services and subservices
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, SubService

# Complete hierarchy definition with nested structure
hierarchy = {
    'Agriculture': {
        'Irrigation Services': [
            'Drip Irrigation',
            'Sprinkler Irrigation',
            'Micro Irrigation',
            'Farm Pipeline Installation',
            'Irrigation Automation',
            'Irrigation Maintenance',
        ],
        'Water Management': [
            'Rainwater Harvesting',
            'Farm Pond Development',
            'Water Storage Tanks',
            'Water Distribution Systems',
            'Water Quality Testing',
        ],
        'Pumps & Motors': [
            'Agricultural Pumps',
            'Solar Pumps',
            'Pump Installation',
            'Pump Repair',
            'Motor Rewinding',
            'Control Panels',
        ],
        'Agricultural Services': [
            'Soil Testing',
            'Land Preparation',
            'Crop Advisory',
            'Farm Consultation',
            'Pest & Disease Management',
            'Fertilizer Recommendation',
        ],
        'Farm Infrastructure': [
            'Greenhouse',
            'Polyhouse',
            'Shade Net',
            'Farm Fencing',
            'Water Tanks',
            'Farm Roads',
        ],
        'Farm Equipment Rental': [
            'Tractor',
            'Rotavator',
            'Cultivator',
            'Seed Drill',
            'Harvester',
            'Sprayer',
            'Power Tiller',
        ],
        'Agri Input Dealers': {
            'Seed Dealers': [
                'Hybrid Seeds',
                'Vegetable Seeds',
                'Fruit Seeds',
                'Grain Seeds',
                'Fodder Seeds',
                'Organic Seeds',
            ],
            'Fertilizer Dealers': [
                'Urea',
                'DAP',
                'NPK Fertilizers',
                'Potash',
                'Micronutrients',
                'Organic Fertilizers',
                'Bio Fertilizers',
            ],
            'Crop Protection Dealers': [
                'Insecticides',
                'Fungicides',
                'Herbicides',
                'Weedicides',
                'Plant Growth Regulators',
                'Bio Pesticides',
            ],
            'Irrigation Dealers': [
                'Drip Irrigation Kits',
                'Sprinkler Systems',
                'HDPE Pipes',
                'PVC Pipes',
                'Valves & Fittings',
                'Filters',
            ],
            'Farm Tool Dealers': [
                'Hand Tools',
                'Power Tools',
                'Sprayers',
                'Pumps',
                'Garden Equipment',
            ],
            'Animal & Dairy Inputs': [
                'Cattle Feed',
                'Poultry Feed',
                'Mineral Mixtures',
                'Veterinary Medicines',
                'Dairy Equipment',
            ],
        },
        'Agriculture Marketplace': [
            'Seeds',
            'Fertilizers',
            'Pesticides',
            'Irrigation Equipment',
            'Farm Machinery',
            'Farm Tools',
            'Solar Equipment',
        ],
        'Second-Hand Agriculture Equipment': [
            'Used Tractors',
            'Used Rotavators',
            'Used Harvesters',
            'Used Seed Drills',
            'Used Cultivators',
            'Used Power Tillers',
            'Used Sprayers',
            'Used Pumps',
            'Used Irrigation Systems',
        ],
    },
    'Borewell': {
        'Borewell Drilling': [
            'Residential Borewell Drilling',
            'Agricultural Borewell Drilling',
            'Commercial Borewell Drilling',
            'Industrial Borewell Drilling',
            'Borewell Site Survey',
            'Hydrogeological Survey',
            'New Borewell Installation',
        ],
        'Borewell Cleaning': [
            'Air Compressor Cleaning',
            'Bore Flushing',
            'Sand Removal',
            'Silt Removal',
            'Mud Removal',
            'Borewell Camera Inspection',
            'Water Yield Improvement',
        ],
        'Borewell Repair & Maintenance': [
            'Borewell Restoration',
            'Borewell Casing Repair',
            'Borewell Leakage Repair',
            'Borewell Blockage Removal',
            'Water Flow Restoration',
            'Periodic Maintenance',
            'Borewell Health Inspection',
        ],
        'Borewell Deepening & Re-Boring': [
            'Borewell Deepening',
            'Re-Boring',
            'Casing Pipe Extension',
            'Yield Improvement',
            'Borewell Rehabilitation',
        ],
        'Borewell Recharge': [
            'Recharge Pit Construction',
            'Recharge Shaft Installation',
            'Rainwater Recharge System',
            'Recharge Bore Construction',
            'Groundwater Recharge Solutions',
            'Recharge Filter Installation',
        ],
        'Submersible Pumps & Motors': [
            'Pump Installation',
            'Pump Repair',
            'Pump Replacement',
            'Pump Pulling & Reinstallation',
            'Motor Installation',
            'Motor Repair',
            'Motor Rewinding',
            'Pump Capacity Upgrade',
        ],
        'Borewell Electrical Services': [
            'Starter Panel Installation',
            'Control Panel Installation',
            'Borewell Wiring',
            'Cable Replacement',
            'Earthing',
            'Electrical Fault Diagnosis',
            'Generator Connection',
            'Automatic Pump Controller Installation',
        ],
        'Pipeline & Plumbing Services': [
            'HDPE Pipe Installation',
            'PVC Pipe Installation',
            'GI Pipe Installation',
            'Underground Pipeline',
            'Water Distribution Pipeline',
            'Valve Installation',
            'Pipe Leakage Repair',
            'Pipeline Replacement',
        ],
        'Water Testing & Analysis': [
            'Drinking Water Testing',
            'Agricultural Water Testing',
            'TDS Testing',
            'pH Testing',
            'Water Quality Analysis',
            'Laboratory Testing',
            'Water Purity Consultation',
        ],
        'Borewell Equipment Rental': [
            'Drilling Rig Rental',
            'Air Compressor Rental',
            'Borewell Camera Rental',
            'Generator Rental',
            'Pipe Lifting Equipment Rental',
            'Crane Rental',
            'Dewatering Pump Rental',
        ],
        'Borewell Equipment Dealers': {
            'Pumps': [
                {
                    'name': 'Submersible Pumps',
                    'per_feet_amount': 150,
                    'features': ['High efficiency', 'Corrosion resistant', 'Long life']
                },
                {
                    'name': 'Openwell Pumps',
                    'per_feet_amount': 120,
                    'features': ['Easy installation', 'Low maintenance', 'Energy efficient']
                },
                {
                    'name': 'Monoblock Pumps',
                    'per_feet_amount': 100,
                    'features': ['Compact design', 'High performance', 'Durable']
                },
            ],
            'Motors': [
                {
                    'name': 'Submersible Motors',
                    'per_feet_amount': 200,
                    'features': ['Water cooled', 'High torque', 'Low noise']
                },
                {
                    'name': 'Surface Motors',
                    'per_feet_amount': 180,
                    'features': ['Air cooled', 'Easy repair', 'Cost effective']
                },
            ],
            'Pipes & Accessories': [
                {
                    'name': 'HDPE Pipes',
                    'per_feet_amount': 50,
                    'features': ['UV resistant', 'Leak proof', 'Flexible']
                },
                {
                    'name': 'PVC Pipes',
                    'per_feet_amount': 40,
                    'features': ['Light weight', 'Easy to install', 'Chemical resistant']
                },
                {
                    'name': 'GI Pipes',
                    'per_feet_amount': 80,
                    'features': ['Strong', 'Long lasting', 'Heat resistant']
                },
                {
                    'name': 'Casing Pipes',
                    'per_feet_amount': 60,
                    'features': ['High strength', 'Smooth bore', 'Corrosion resistant']
                },
                {
                    'name': 'Column Pipes',
                    'per_feet_amount': 55,
                    'features': ['Heavy duty', 'Precision engineered', 'Threaded joints']
                },
            ],
            'Electrical': [
                {
                    'name': 'Starter Panels',
                    'per_feet_amount': 500,
                    'features': ['Auto start', 'Overload protection', 'Phase monitoring']
                },
                {
                    'name': 'Control Panels',
                    'per_feet_amount': 600,
                    'features': ['Digital display', 'Remote control', 'Multi-stage protection']
                },
                {
                    'name': 'Pump Controllers',
                    'per_feet_amount': 450,
                    'features': ['Automatic operation', 'Dry run protection', 'Level sensing']
                },
                {
                    'name': 'Cables',
                    'per_feet_amount': 30,
                    'features': ['Waterproof', 'Heat resistant', 'High conductivity']
                },
                {
                    'name': 'Capacitors',
                    'per_feet_amount': 200,
                    'features': ['High capacity', 'Long life', 'Low loss']
                },
            ],
            'Borewell Accessories': [
                {
                    'name': 'Bore Caps',
                    'per_feet_amount': 150,
                    'features': ['Stainless steel', 'Lockable', 'Weather proof']
                },
                {
                    'name': 'Clamps',
                    'per_feet_amount': 50,
                    'features': ['Heavy duty', 'Rust proof', 'Easy to adjust']
                },
                {
                    'name': 'Valves',
                    'per_feet_amount': 100,
                    'features': ['Leak proof', 'High pressure', 'Easy operation']
                },
                {
                    'name': 'Pipe Fittings',
                    'per_feet_amount': 40,
                    'features': ['Universal fit', 'Durable', 'Easy installation']
                },
                {
                    'name': 'Cable Guards',
                    'per_feet_amount': 60,
                    'features': ['Protective', 'UV resistant', 'Long lasting']
                },
            ],
        },
        'Second-Hand Borewell Equipment': [
            'Used Drilling Rigs',
            'Used Air Compressors',
            'Used Mud Pumps',
            'Used Submersible Pumps',
            'Used Motors',
            'Used Generators',
            'Used Drill Rods',
            'Used Borewell Cameras',
            'Used Starter Panels',
            'Used Control Panels',
            'Used Pipe Handling Equipment',
            'Used Water Tankers',
        ],
        'Emergency Borewell Services': [
            'Emergency Pump Breakdown',
            'No Water in Borewell',
            'Pump Stuck in Borewell',
            'Cable Breakage',
            'Borewell Collapse Assistance',
            'Emergency Technician Visit',
            '24×7 Support',
        ],
        'Annual Maintenance Contract (AMC)': [
            'Annual Borewell Maintenance',
            'Pump Inspection',
            'Motor Inspection',
            'Electrical Inspection',
            'Pipeline Inspection',
            'Preventive Maintenance',
            'Scheduled Servicing',
        ],
    },
}

print("Starting hierarchy population...\n")

services_added = 0
services_skipped = 0
subservices_added = 0
subservices_skipped = 0

for sector_name, services_dict in hierarchy.items():
    # Get or create sector
    sector, sector_created = Sector.objects.get_or_create(
        name=sector_name,
        defaults={'id': sector_name.lower().replace(' ', '_'), 'order': 0}
    )
    if sector_created:
        print(f"✓ Created sector: {sector_name}")
    else:
        print(f"✓ Sector exists: {sector_name}")

    for service_name, subservices_data in services_dict.items():
        # Get or create service
        service_id = service_name.lower().replace(' ', '_').replace('&', 'and')
        service, service_created = Service.objects.get_or_create(
            id=service_id,
            sector=sector,
            defaults={'name': service_name, 'order': 0}
        )
        if service_created:
            services_added += 1
            print(f"  ✓ Created service: {service_name}")
        else:
            services_skipped += 1
            print(f"  - Service exists: {service_name}")

        # Handle nested structure (dict) or flat structure (list)
        if isinstance(subservices_data, dict):
            # Nested structure - create parent subservices with children
            for parent_name, children_list in subservices_data.items():
                # Generate unique ID and slug from parent name + service context
                parent_slug_base = parent_name.lower().replace(' ', '_').replace('&', 'and').replace('×', 'x')
                parent_id = f"{service.id}_{parent_slug_base}"
                
                # Try to get existing parent subservice first
                try:
                    parent_subservice = SubService.objects.get(id=parent_id, service=service)
                    parent_created = False
                    subservices_skipped += 1
                    print(f"    - Parent subservice exists: {parent_name}")
                except SubService.DoesNotExist:
                    # Create new parent subservice with unique slug
                    parent_subservice = SubService.objects.create(
                        id=parent_id,
                        service=service,
                        name=parent_name,
                        slug=parent_id,  # Use the unique ID as slug
                        order=0
                    )
                    parent_created = True
                    subservices_added += 1
                    print(f"    ✓ Created parent subservice: {parent_name}")

                # Add child subservices under parent
                for child_data in children_list:
                    # Handle both string and dict formats
                    if isinstance(child_data, str):
                        child_name = child_data
                        per_feet_amount = None
                        features = []
                    else:
                        child_name = child_data.get('name')
                        per_feet_amount = child_data.get('per_feet_amount')
                        features = child_data.get('features', [])

                    # Generate unique ID and slug from child name + parent context
                    child_slug_base = child_name.lower().replace(' ', '_').replace('&', 'and').replace('×', 'x').lstrip('_')
                    child_id = f"{parent_id}_{child_slug_base}"

                    # Check if child subservice exists
                    if SubService.objects.filter(id=child_id).exists():
                        subservices_skipped += 1
                        print(f"      - Child subservice exists: {child_name}")
                        # Update per_feet_amount and features if not set
                        child = SubService.objects.get(id=child_id)
                        if per_feet_amount and child.per_feet_amount is None:
                            child.per_feet_amount = per_feet_amount
                            child.save()
                        if features and not child.features:
                            child.features = features
                            child.save()
                    else:
                        SubService.objects.create(
                            id=child_id,
                            service=service,
                            parent=parent_subservice,
                            name=child_name,
                            slug=child_id,  # Use the unique ID as slug
                            per_feet_amount=per_feet_amount,
                            features=features,
                            order=0
                        )
                        subservices_added += 1
                        print(f"      ✓ Created child subservice: {child_name}")
        else:
            # Flat structure - create subservices directly
            for subservice_name in subservices_data:
                # Generate slug from name
                slug = subservice_name.lower().replace(' ', '_').replace('&', 'and').replace('×', 'x').lstrip('_')
                subservice_id = slug
                
                # Check if subservice exists
                if SubService.objects.filter(id=subservice_id).exists():
                    subservices_skipped += 1
                    print(f"    - Subservice exists: {subservice_name}")
                else:
                    SubService.objects.create(
                        id=subservice_id,
                        service=service,
                        name=subservice_name,
                        slug=slug,
                        order=0
                    )
                    subservices_added += 1
                    print(f"    ✓ Created subservice: {subservice_name}")

print(f"\n{'='*60}")
print(f"Summary:")
print(f"  Services added: {services_added}")
print(f"  Services skipped: {services_skipped}")
print(f"  Subservices added: {subservices_added}")
print(f"  Subservices skipped: {subservices_skipped}")
print(f"{'='*60}")
