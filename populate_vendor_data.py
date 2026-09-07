"""
Vendor Data Population Script
Populates the database with cities, sectors, services, subservices, and sample vendors
"""

import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City, Sector, ServiceCategory, Service, Vendor, User, VendorPlan
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify
from datetime import datetime, timedelta

# Cities Data
CITIES_DATA = [
    {"name": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Delhi", "state": "Delhi", "latitude": 28.7041, "longitude": 77.1025},
    {"name": "Bangalore", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867},
    {"name": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707},
    {"name": "Kolkata", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639},
    {"name": "Pune", "state": "Maharashtra", "latitude": 18.5204, "longitude": 73.8567},
    {"name": "Jaipur", "state": "Rajasthan", "latitude": 26.9124, "longitude": 75.7873},
    {"name": "Ahmedabad", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714},
    {"name": "Surat", "state": "Gujarat", "latitude": 21.1702, "longitude": 72.8311},
]

# Sectors and Services Data
SECTORS_SERVICES_DATA = [
    {
        "sector": "Agriculture",
        "services": [
            {
                "name": "Borewell Drilling",
                "id": "borewell_drilling",
                "subservices": [
                    {"name": "Deep Borewell", "id": "deep_borewell", "per_feet": 150},
                    {"name": "Shallow Borewell", "id": "shallow_borewell", "per_feet": 120},
                    {"name": "Tube Well Drilling", "id": "tube_well", "per_feet": 140},
                    {"name": "Rock Drilling", "id": "rock_drilling", "per_feet": 180},
                ]
            },
            {
                "name": "Irrigation Systems",
                "id": "irrigation_systems",
                "subservices": [
                    {"name": "Drip Irrigation", "id": "drip_irrigation", "per_feet": 80},
                    {"name": "Sprinkler System", "id": "sprinkler_system", "per_feet": 75},
                    {"name": "Flood Irrigation", "id": "flood_irrigation", "per_feet": 60},
                ]
            },
            {
                "name": "Water Pump Installation",
                "id": "water_pump_installation",
                "subservices": [
                    {"name": "Submersible Pump", "id": "submersible_pump", "per_feet": 100},
                    {"name": "Centrifugal Pump", "id": "centrifugal_pump", "per_feet": 90},
                    {"name": "Jet Pump", "id": "jet_pump", "per_feet": 85},
                ]
            },
        ]
    },
    {
        "sector": "Construction",
        "services": [
            {
                "name": "Earth Excavation",
                "id": "earth_excavation",
                "subservices": [
                    {"name": "Foundation Digging", "id": "foundation_digging", "per_feet": 120},
                    {"name": "Trench Excavation", "id": "trench_excavation", "per_feet": 110},
                ]
            },
            {
                "name": "Land Leveling",
                "id": "land_leveling",
                "subservices": [
                    {"name": "Bulldozing", "id": "bulldozing", "per_feet": 100},
                    {"name": "Grading", "id": "grading", "per_feet": 95},
                ]
            },
        ]
    },
    {
        "sector": "Maintenance",
        "services": [
            {
                "name": "Borewell Maintenance",
                "id": "borewell_maintenance",
                "subservices": [
                    {"name": "Borewell Flushing", "id": "borewell_flushing", "per_feet": 80},
                    {"name": "Pump Repair", "id": "pump_repair", "per_feet": 150},
                    {"name": "Pipe Replacement", "id": "pipe_replacement", "per_feet": 120},
                ]
            },
            {
                "name": "Water Testing",
                "id": "water_testing",
                "subservices": [
                    {"name": "Water Quality Test", "id": "water_quality", "per_feet": 500},
                    {"name": "Borewell Camera Inspection", "id": "camera_inspection", "per_feet": 300},
                ]
            },
        ]
    },
]

# Sample Vendors Data
VENDORS_DATA = [
    {
        "company_name": "Agro Water Solutions",
        "username": "agrowater",
        "email": "info@agrowater.com",
        "phone": "9876543210",
        "city": "Mumbai",
        "address": "Plot 123, Industrial Area, Andheri East, Mumbai - 400069",
        "experience": 15,
        "license_number": "AGRI/MH/2020/12345",
        "about": "Leading borewell drilling company with 15+ years of experience in Maharashtra region.",
        "services": ["borewell_drilling", "irrigation_systems"],
    },
    {
        "company_name": "Deep Well Experts",
        "username": "deepwell",
        "email": "contact@deepwell.com",
        "phone": "9876543211",
        "city": "Bangalore",
        "address": "45, Electronics City Phase 1, Bangalore - 560100",
        "experience": 12,
        "license_number": "KAR/BLR/2019/54321",
        "about": "Specialized in deep borewell drilling and rock drilling for residential and commercial purposes.",
        "services": ["borewell_drilling"],
    },
    {
        "company_name": "Green Field Irrigation",
        "username": "greenfield",
        "email": "sales@greenfield.com",
        "phone": "9876543212",
        "city": "Hyderabad",
        "address": "78, Madhapur, Hyderabad - 500081",
        "experience": 10,
        "license_number": "TS/HYD/2021/67890",
        "about": "Complete irrigation solutions for farms and gardens. Modern drip and sprinkler systems.",
        "services": ["irrigation_systems", "water_pump_installation"],
    },
    {
        "company_name": "Pump Masters",
        "username": "pumpmasters",
        "email": "info@pumpmasters.com",
        "phone": "9876543213",
        "city": "Chennai",
        "address": "23, Anna Nagar, Chennai - 600040",
        "experience": 8,
        "license_number": "TN/CHN/2022/11111",
        "about": "Expert water pump installation and maintenance services across Tamil Nadu.",
        "services": ["water_pump_installation", "borewell_maintenance"],
    },
    {
        "company_name": "Rock Drilling Co",
        "username": "rockdrilling",
        "email": "contact@rockdrilling.com",
        "phone": "9876543214",
        "city": "Pune",
        "address": "156, Hinjewadi, Pune - 411057",
        "experience": 20,
        "license_number": "MH/PUN/2018/22222",
        "about": "Specialized in rock drilling and challenging terrains. Advanced equipment for hard soil conditions.",
        "services": ["borewell_drilling"],
    },
    {
        "company_name": "Aqua Tech Services",
        "username": "aquatech",
        "email": "support@aquatech.com",
        "phone": "9876543215",
        "city": "Delhi",
        "address": "45, Nehru Place, New Delhi - 110019",
        "experience": 11,
        "license_number": "DL/ND/2020/33333",
        "about": "Complete water solutions including drilling, pumps, and maintenance services.",
        "services": ["borewell_drilling", "water_pump_installation", "borewell_maintenance"],
    },
    {
        "company_name": "Farm Irrigation Systems",
        "username": "farmirrigation",
        "email": "info@farmirrigation.com",
        "phone": "9876543216",
        "city": "Jaipur",
        "address": "89, Industrial Area, Jaipur - 302006",
        "experience": 9,
        "license_number": "RJ/JAI/2021/44444",
        "about": "Modern irrigation systems for agricultural lands. Drip and sprinkler specialists.",
        "services": ["irrigation_systems"],
    },
    {
        "company_name": "Well Care Solutions",
        "username": "wellcare",
        "email": "contact@wellcare.com",
        "phone": "9876543217",
        "city": "Ahmedabad",
        "address": "67, Shivranjani, Ahmedabad - 380015",
        "experience": 14,
        "license_number": "GJ/AMD/2019/55555",
        "about": "Borewell maintenance and restoration experts. 24/7 emergency service available.",
        "services": ["borewell_maintenance", "water_testing"],
    },
]


def populate_cities():
    """Populate cities in the database"""
    print("Populating cities...")
    for city_data in CITIES_DATA:
        city, created = City.objects.get_or_create(
            name=city_data["name"],
            defaults={
                "state": city_data["state"],
                "latitude": city_data["latitude"],
                "longitude": city_data["longitude"],
            }
        )
        if created:
            print(f"  ✓ Created city: {city.name}")
        else:
            print(f"  - City already exists: {city.name}")


def populate_sectors_and_services():
    """Populate sectors, services, and subservices"""
    print("\nPopulating sectors, services, and subservices...")

    for sector_data in SECTORS_SERVICES_DATA:
        sector, created = Sector.objects.get_or_create(
            name=sector_data["sector"],
            defaults={"slug": slugify(sector_data["sector"])}
        )
        if created:
            print(f"  ✓ Created sector: {sector.name}")
        else:
            print(f"  - Sector already exists: {sector.name}")

        for service_data in sector_data["services"]:
            service, created = Service.objects.get_or_create(
                id=service_data["id"],
                defaults={
                    "sector": sector,
                    "name": service_data["name"],
                    "slug": slugify(service_data["name"]),
                }
            )
            if created:
                print(f"    ✓ Created service: {service.name}")
            else:
                # Update sector if service exists but belongs to wrong sector
                if service.sector != sector:
                    service.sector = sector
                    service.save()
                print(f"    - Service already exists: {service.name}")

            # Populate subservices (ServiceCategory or SubService)
            for subservice_data in service_data["subservices"]:
                subservice, created = ServiceCategory.objects.get_or_create(
                    id=subservice_data["id"],
                    defaults={
                        "category": sector,
                        "name": subservice_data["name"],
                        "slug": slugify(subservice_data["name"]),
                        "per_feet_amount": subservice_data.get("per_feet", 0),
                    }
                )
                if created:
                    print(f"      ✓ Created subservice: {subservice.name}")
                else:
                    # Update per_feet_amount if subservice exists
                    if subservice.per_feet_amount != subservice_data.get("per_feet", 0):
                        subservice.per_feet_amount = subservice_data.get("per_feet", 0)
                        subservice.save()
                    print(f"      - Subservice already exists: {subservice.name}")


def populate_vendors():
    """Populate sample vendors"""
    print("\nPopulating vendors...")

    for vendor_data in VENDORS_DATA:
        # Get city
        city = City.objects.get(name=vendor_data["city"])

        # Create user account
        user, created = User.objects.get_or_create(
            username=vendor_data["username"],
            defaults={
                "email": vendor_data["email"],
                "password": make_password("vendor123"),  # Default password
                "first_name": vendor_data["company_name"],
                "is_active": True,
            }
        )

        if created:
            print(f"  ✓ Created user: {user.username}")

        # Create vendor profile
        vendor, created = Vendor.objects.get_or_create(
            user=user,
            defaults={
                "company_name": vendor_data["company_name"],
                "phone": vendor_data["phone"],
                "city": city,
                "address": vendor_data["address"],
                "experience": vendor_data["experience"],
                "license_number": vendor_data.get("license_number", ""),
                "about": vendor_data.get("about", ""),
                "verification_status": "verified",
            }
        )

        if created:
            print(f"    ✓ Created vendor: {vendor.company_name}")

            # Create vendor plan
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=365)

            VendorPlan.objects.create(
                vendor=vendor,
                plan_type="basic",
                plan_name="Basic Plan",
                price=5000,
                start_date=start_date,
                end_date=end_date,
                status="active",
                validity_period=365,
            )
            print(f"      ✓ Created basic plan for vendor")
        else:
            print(f"    - Vendor already exists: {vendor.company_name}")

        # Link services to vendor
        for service_id in vendor_data["services"]:
            try:
                service = Service.objects.get(id=service_id)
                from core.models import VendorService
                VendorService.objects.get_or_create(
                    vendor=vendor,
                    service=service,
                    defaults={"price": random.randint(100, 200)}
                )
            except Service.DoesNotExist:
                print(f"      ! Service not found: {service_id}")


def run_population():
    """Run all population functions"""
    print("="*50)
    print("Vendor Data Population Script")
    print("="*50)

    try:
        populate_cities()
        populate_sectors_and_services()
        populate_vendors()

        print("\n" + "="*50)
        print("✓ Data population completed successfully!")
        print("="*50)

        print("\nSummary:")
        print(f"  Cities: {City.objects.count()}")
        print(f"  Sectors: {Sector.objects.count()}")
        print(f"  Services: {Service.objects.count()}")
        print(f"  Subservices: {ServiceCategory.objects.count()}")
        print(f"  Vendors: {Vendor.objects.count()}")

    except Exception as e:
        print(f"\n✗ Error during population: {e}")
        raise


if __name__ == "__main__":
    run_population()
