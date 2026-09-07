#!/usr/bin/env python
"""
Create sample vendors from Karnataka cities and link them to subservices
"""

import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City, Vendor, User, UserProfile, SubService, VendorService
from django.contrib.auth.hashers import make_password

# Sample vendor data
vendor_data = [
    {
        'company_name': 'Borewell Solutions Hubli',
        'city': 'Hubli',
        'phone': '9876543210',
        'email': 'info@borewellsolutions.com',
        'address': 'Market Area, Hubli, Karnataka',
        'experience': 15,
        'rating': 4.8,
        'services': ['borewell_drilling', 'borewell_cleaning', 'pump_installation'],
    },
    {
        'company_name': 'Agri Tech Bangalore',
        'city': 'Bangalore',
        'phone': '9876543211',
        'email': 'contact@agritech.com',
        'address': 'Electronic City, Bangalore, Karnataka',
        'experience': 12,
        'rating': 4.7,
        'services': ['drip_irrigation', 'sprinkler_irrigation', 'farm_pipeline_installation'],
    },
    {
        'company_name': 'Mangalore Borewell Services',
        'city': 'Mangalore',
        'phone': '9876543212',
        'email': 'mangalore@borewell.com',
        'address': 'PVS Circle, Mangalore, Karnataka',
        'experience': 20,
        'rating': 4.9,
        'services': ['residential_borewell_drilling', 'agricultural_borewell_drilling', 'borewell_camera_inspection'],
    },
    {
        'company_name': 'Mysore Farm Equipment',
        'city': 'Mysuru',
        'phone': '9876543213',
        'email': 'mysore@farmequip.com',
        'address': 'Industrial Area, Mysuru, Karnataka',
        'experience': 10,
        'rating': 4.6,
        'services': ['tractor', 'rotavator', 'cultivator', 'seed_drill'],
    },
    {
        'company_name': 'Dharwad Water Systems',
        'city': 'Dharwad',
        'phone': '9876543214',
        'email': 'dharwad@watersystems.com',
        'address': 'Twin City, Dharwad, Karnataka',
        'experience': 18,
        'rating': 4.8,
        'services': ['submersible_pumps', 'pump_repair', 'motor_rewinding', 'starter_panel_installation'],
    },
    {
        'company_name': 'Belagavi Agriculture',
        'city': 'Belagavi',
        'phone': '9876543215',
        'email': 'belagavi@agri.com',
        'address': 'Khanapur Road, Belagavi, Karnataka',
        'experience': 14,
        'rating': 4.5,
        'services': ['soil_testing', 'crop_advisory', 'farm_consultation', 'fertilizer_recommendation'],
    },
    {
        'company_name': 'Kalaburagi Irrigation',
        'city': 'Kalaburagi',
        'phone': '9876543216',
        'email': 'kalaburagi@irrigation.com',
        'address': 'Main Road, Kalaburagi, Karnataka',
        'experience': 11,
        'rating': 4.4,
        'services': ['rainwater_harvesting', 'farm_pond_development', 'water_storage_tanks'],
    },
    {
        'company_name': 'Shivamogga Pumps',
        'city': 'Shivamogga',
        'phone': '9876543217',
        'email': 'shivamogga@pumps.com',
        'address': 'Bus Stand, Shivamogga, Karnataka',
        'experience': 16,
        'rating': 4.7,
        'services': ['openwell_pumps', 'monoblock_pumps', 'pump_replacement', 'pump_capacity_upgrade'],
    },
    {
        'company_name': 'Ballari Borewell Experts',
        'city': 'Ballari',
        'phone': '9876543218',
        'email': 'ballari@borewell.com',
        'address': 'Cantonment, Ballari, Karnataka',
        'experience': 13,
        'rating': 4.6,
        'services': ['borewell_deepening', 're-boring', 'casing_pipe_extension', 'yield_improvement'],
    },
    {
        'company_name': 'Hassan Farm Services',
        'city': 'Hassan',
        'phone': '9876543219',
        'email': 'hassan@farmservices.com',
        'address': 'Highway Road, Hassan, Karnataka',
        'experience': 9,
        'rating': 4.5,
        'services': ['greenhouse', 'polyhouse', 'shade_net', 'farm_fencing'],
    },
    {
        'company_name': 'Mandya Water Management',
        'city': 'Mandya',
        'phone': '9876543220',
        'email': 'mandya@watermgmt.com',
        'address': 'Sugar Town, Mandya, Karnataka',
        'experience': 17,
        'rating': 4.8,
        'services': ['water_distribution_systems', 'water_quality_testing', 'laboratory_testing'],
    },
    {
        'company_name': 'Bidar Agri Dealers',
        'city': 'Bidar',
        'phone': '9876543221',
        'email': 'bidar@agridealers.com',
        'address': 'Main Market, Bidar, Karnataka',
        'experience': 8,
        'rating': 4.3,
        'services': ['seed_dealers', 'fertilizer_dealers', 'crop_protection_dealers'],
    },
    {
        'company_name': 'Raichur Emergency Services',
        'city': 'Raichur',
        'phone': '9876543222',
        'email': 'raichur@emergency.com',
        'address': 'Station Road, Raichur, Karnataka',
        'experience': 22,
        'rating': 4.9,
        'services': ['emergency_pump_breakdown', 'no_water_in_borewell', 'pump_stuck_in_borewell', '24x7_support'],
        'is_emergency': True,
    },
    {
        'company_name': 'Vijayapura Pipeline',
        'city': 'Vijayapura',
        'phone': '9876543223',
        'email': 'vijayapura@pipeline.com',
        'address': 'New City, Vijayapura, Karnataka',
        'experience': 12,
        'rating': 4.6,
        'services': ['hdpe_pipe_installation', 'pvc_pipe_installation', 'underground_pipeline', 'pipe_leakage_repair'],
    },
]

print("Starting sample vendor creation...\n")

vendors_created = 0
vendors_skipped = 0
services_linked = 0

for vendor_info in vendor_data:
    company_name = vendor_info['company_name']
    city_name = vendor_info['city']
    
    # Check if vendor already exists
    if Vendor.objects.filter(company_name=company_name).exists():
        print(f"- Vendor already exists: {company_name}")
        vendors_skipped += 1
        continue
    
    # Get city
    try:
        city = City.objects.get(name=city_name, state='Karnataka')
    except City.DoesNotExist:
        print(f"✗ City not found: {city_name}")
        continue
    
    # Create user
    username = company_name.lower().replace(' ', '_').replace('-', '_')
    email = vendor_info['email']
    
    if User.objects.filter(username=username).exists():
        username = f"{username}_{random.randint(1000, 9999)}"
    
    user = User.objects.create(
        username=username,
        email=email,
        password=make_password('password123'),
        first_name=company_name.split()[0],
        last_name=' '.join(company_name.split()[1:]) if len(company_name.split()) > 1 else ''
    )
    
    # Create user profile
    UserProfile.objects.create(
        user=user,
        user_type='vendor',
        city=city,
        phone=vendor_info['phone']
    )
    
    # Create vendor
    vendor = Vendor.objects.create(
        user=user,
        company_name=company_name,
        phone=vendor_info['phone'],
        email=email,
        address=vendor_info['address'],
        city=city,
        experience=vendor_info['experience'],
        rating=vendor_info['rating'],
        verification_status='verified',
        is_emergency_available=vendor_info.get('is_emergency', False)
    )
    
    vendors_created += 1
    print(f"✓ Created vendor: {company_name} in {city_name}")
    
    # Link services
    for service_id in vendor_info['services']:
        try:
            subservice = SubService.objects.get(id=service_id)
            VendorService.objects.create(
                vendor=vendor,
                subservice=subservice,
                price=random.randint(500, 5000)
            )
            services_linked += 1
            print(f"  ✓ Linked service: {subservice.name}")
        except SubService.DoesNotExist:
            print(f"  ✗ Service not found: {service_id}")

print(f"\n{'='*60}")
print(f"Summary:")
print(f"  Vendors created: {vendors_created}")
print(f"  Vendors skipped: {vendors_skipped}")
print(f"  Services linked: {services_linked}")
print(f"{'='*60}")
