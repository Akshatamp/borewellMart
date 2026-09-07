#!/usr/bin/env python
"""
Create vendors for existing subservices in the database
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import SubService, Vendor, User, UserProfile, City, VendorService
from django.db import transaction

# Get all existing subservices
existing_subservices = list(SubService.objects.values_list('id', flat=True))
print(f"Found {len(existing_subservices)} existing subservices")

# Create vendors for the existing subservices
vendors_data = [
    {
        "company_name": "Hubli Aqua Borewell Services",
        "location": "Hubli",
        "specialization": "Complete borewell solutions for domestic and agricultural needs",
        "services": ["domestic_borewell_drilling", "agricultural_borewell_drilling", "submersible_pump_installation", "hydrogeological_surveys"],
        "phone": "9876543210",
        "email": "hubliaqua@borewell.com",
        "address": "Vidyanagar, Hubli - 580021",
        "license_number": "BWL-KAR-2010-001"
    },
    {
        "company_name": "North Karnataka Drilling Works",
        "location": "Dharwad",
        "specialization": "Deep borewell drilling specialists",
        "services": ["domestic_borewell_drilling", "agricultural_borewell_drilling", "industrial_borewell_drilling", "deep_borewell_drilling"],
        "phone": "9876543211",
        "email": "northkar@drilling.com",
        "address": "KC Extension, Dharwad - 580008",
        "license_number": "BWL-KAR-2008-015"
    },
    {
        "company_name": "Bangalore Precision Borewells",
        "location": "Bangalore",
        "specialization": "Urban borewell solutions with advanced technology",
        "services": ["hydrogeological_surveys", "geophysical_surveys", "domestic_borewell_drilling", "yield_enhancement"],
        "phone": "9876543212",
        "email": "blrprecision@borewell.com",
        "address": "BTM Layout, Bangalore - 560068",
        "license_number": "BWL-KAR-2012-025"
    },
    {
        "company_name": "Belagavi Borewell Masters",
        "location": "Belagavi",
        "specialization": "Traditional and modern borewell techniques",
        "services": ["domestic_borewell_drilling", "open_well_pump_installation", "recharge_pit_construction", "yield_enhancement"],
        "phone": "9876543213",
        "email": "belagavimaster@borewell.com",
        "address": "Camp Area, Belagavi - 590001",
        "license_number": "BWL-KAR-2005-008"
    },
    {
        "company_name": "Mysuru Agri Aqua Services",
        "location": "Mysuru",
        "specialization": "Agricultural water management and irrigation",
        "services": ["farm_borewell_drilling", "drip_irrigation_installation", "sprinkler_irrigation_systems", "solar_water_pumps"],
        "phone": "9876543215",
        "email": "mysuruagri@borewell.com",
        "address": "Saraswathipuram, Mysuru - 570009",
        "license_number": "BWL-KAR-2009-012"
    },
    {
        "company_name": "Dharwad Pump & Motors",
        "location": "Dharwad",
        "specialization": "Pump installation, repair and motor rewinding",
        "services": ["submersible_pump_installation", "pump_repair_servicing", "motor_rewinding_maintenance", "open_well_pump_installation"],
        "phone": "9876543217",
        "email": "dharwadpump@motors.com",
        "address": "KCC Bank Road, Dharwad - 580001",
        "license_number": "PMP-KAR-2006-022"
    },
    {
        "company_name": "Complete Borewell Solutions",
        "location": "Hubli",
        "specialization": "Borewell cleaning and maintenance",
        "services": ["air_compressor_flushing", "bore_cleaning", "drilling_debris_removal", "yield_enhancement"],
        "phone": "9876543505",
        "email": "borewellclean@services.com",
        "address": "Keshwapur, Hubli - 580022",
        "license_number": "CLEAN-KAR-2009-105"
    },
    {
        "company_name": "Borewell Repair Experts",
        "location": "Dharwad",
        "specialization": "Borewell restoration and repair",
        "services": ["borewell_cleaning_rehabilitation", "casing_repair_replacement", "fallen_object_removal", "yield_enhancement"],
        "phone": "9876543506",
        "email": "borewellrepair@experts.com",
        "address": "KC Extension, Dharwad - 580008",
        "license_number": "REPAIR-KAR-2010-106"
    },
    {
        "company_name": "Solar Water Solutions",
        "location": "Mysuru",
        "specialization": "Solar-powered water systems",
        "services": ["solar_water_pumps", "solar_irrigation_systems", "solar_pump_maintenance", "energy_efficient_water_management"],
        "phone": "9876543508",
        "email": "solarwaters@systems.com",
        "address": "Saraswathipuram, Mysuru - 570009",
        "license_number": "SLR-KAR-2012-108"
    },
    {
        "company_name": "Pipeline Services",
        "location": "Hubli",
        "specialization": "Pipeline installation and plumbing",
        "services": ["hdpe_pipeline_installation", "pvc_casing_installation", "ms_casing_installation", "farm_pipeline_networks"],
        "phone": "9876543511",
        "email": "pipeline@plumbing.com",
        "address": "Keshwapur, Hubli - 580022",
        "license_number": "PIPELINE-KAR-2011-111"
    },
    {
        "company_name": "Water Testing Labs",
        "location": "Mangalore",
        "specialization": "Water quality testing and analysis",
        "services": ["chemical_analysis", "bacteriological_testing", "potability_testing", "industrial_water_quality_assessment"],
        "phone": "9876543512",
        "email": "watertest@laboratory.com",
        "address": "PVS Circle, Mangalore - 575003",
        "license_number": "LABTEST-KAR-2015-112"
    },
    {
        "company_name": "Irrigation Systems",
        "location": "Shivamogga",
        "specialization": "Drip and sprinkler irrigation systems",
        "services": ["drip_irrigation_installation", "sprinkler_irrigation_systems", "micro_irrigation_solutions", "farm_water_distribution"],
        "phone": "9876543405",
        "email": "irrigations@systems.com",
        "address": "Market Road, Shivamogga - 577201",
        "license_number": "IRRI-KAR-2011-005"
    }
]

# Create vendors
created_count = 0
vendor_service_count = 0

for vendor_data in vendors_data:
    try:
        with transaction.atomic():
            # Get or create city
            city, _ = City.objects.get_or_create(
                name=vendor_data['location'],
                defaults={
                    'description': f'{vendor_data["location"]} - Service area',
                    'latitude': 15.0,
                    'longitude': 75.0
                }
            )

            # Create user for vendor
            username = vendor_data['email'].split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user, created = User.objects.get_or_create(
                email=vendor_data['email'],
                defaults={
                    'username': username,
                    'is_active': True
                }
            )

            if created:
                user.set_password(vendor_data['phone'])
                user.save()

                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    phone=vendor_data['phone'],
                    user_type='vendor',
                    city=city
                )

                # Create Vendor
                vendor = Vendor.objects.create(
                    user=user,
                    company_name=vendor_data['company_name'],
                    city=city,
                    experience=5,
                    phone=vendor_data['phone'],
                    email=vendor_data['email'],
                    address=vendor_data.get('address', f'{city.name}, Karnataka'),
                    license_number=vendor_data.get('license_number', ''),
                    verification_status='verified',
                    rating=4.5,
                    is_emergency_available=False
                )
                created_count += 1
                print(f'Created vendor: {vendor.company_name}')

                # Assign subservices to vendor (only existing ones)
                for service_id in vendor_data.get('services', []):
                    if service_id in existing_subservices:
                        try:
                            subservice = SubService.objects.get(id=service_id)
                            # Default vendor price
                            price = 5000
                            VendorService.objects.create(
                                vendor=vendor,
                                subservice=subservice,
                                price=price,
                                description=f'Professional {subservice.name} by {vendor.company_name}'
                            )
                            vendor_service_count += 1
                        except SubService.DoesNotExist:
                            pass
            else:
                print(f'Vendor already exists: {vendor_data["company_name"]}')

    except Exception as e:
        print(f'Error creating vendor {vendor_data.get("company_name")}: {e}')

print(f'\nSummary:')
print(f'  Vendors created: {created_count}')
print(f'  Vendor services created: {vendor_service_count}')
