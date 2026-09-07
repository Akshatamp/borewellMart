import json
import os
import re
from datetime import date, time, timedelta
from decimal import Decimal
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "borewellmart.settings")
os.environ["DEBUG"] = "True"

import django

django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from core.models import (
    Blog,
    Booking,
    City,
    Enquiry,
    FavoriteVendor,
    Review,
    Service,
    ServiceCategory,
    ServiceSubcategory,
    UserProfile,
    Vendor,
    VendorGallery,
    VendorPayment,
    VendorService,
)


BASE_DIR = Path(__file__).resolve().parent
COMMAND_DATA_DIR = BASE_DIR / "core" / "management" / "commands"

CITY_DATA = [
    {"name": "Hubli", "description": "Commercial hub of North Karnataka", "latitude": 15.3647, "longitude": 75.1239},
    {"name": "Dharwad", "description": "Twin city of Hubli, educational center", "latitude": 15.4609, "longitude": 75.0567},
    {"name": "Bangalore", "description": "Silicon Valley of India", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Belagavi", "description": "Second capital of Karnataka", "latitude": 15.8485, "longitude": 74.5129},
    {"name": "Mangalore", "description": "Coastal city of Karnataka", "latitude": 12.9141, "longitude": 74.8560},
    {"name": "Mysuru", "description": "Cultural capital of Karnataka", "latitude": 12.2958, "longitude": 76.6394},
    {"name": "Vijayapura", "description": "Agricultural hub of North Karnataka", "latitude": 16.8304, "longitude": 75.7140},
    {"name": "Raichur", "description": "Cotton and rice growing region", "latitude": 16.2076, "longitude": 77.3463},
    {"name": "Kalaburagi", "description": "Red cotton belt of Karnataka", "latitude": 17.3280, "longitude": 76.8336},
    {"name": "Bidar", "description": "Agricultural district with rich groundwater", "latitude": 17.9072, "longitude": 77.5283},
    {"name": "Ballari", "description": "Iron and agricultural district", "latitude": 15.1393, "longitude": 76.9123},
    {"name": "Shivamogga", "description": "Areca nut and paddy growing region", "latitude": 13.9299, "longitude": 75.5681},
]

PER_FEET_AMOUNT_BY_SERVICE_ID = {
    "domestic_borewell_drilling": 95,
    "agricultural_borewell_drilling": 110,
    "industrial_borewell_drilling": 140,
    "deep_borewell_drilling": 160,
    "rotary_drilling": 105,
    "dth_drilling": 120,
    "farm_borewell_drilling": 110,
    "deep_agricultural_borewells": 155,
}

BLOG_DATA = [
    {
        "title": "How to Maintain Your Borewell for Long-Lasting Performance",
        "slug": "maintain-borewell-long-lasting",
        "category": "borewell_maintenance",
        "content": "Regular cleaning, yield checks, pump inspection, and casing checks help a borewell stay reliable through changing seasons.",
    },
    {
        "title": "Signs Your Borewell Needs Professional Cleaning",
        "slug": "signs-borewell-needs-cleaning",
        "category": "borewell_maintenance",
        "content": "Reduced water flow, muddy discharge, unusual smell, and frequent pump strain are common signs that a borewell needs service.",
    },
    {
        "title": "Benefits of Rainwater Harvesting and Borewell Recharging",
        "slug": "benefits-rainwater-harvesting-borewell-recharging",
        "category": "water_conservation",
        "content": "Recharge pits and rainwater harvesting systems help restore groundwater and improve long-term borewell performance.",
    },
    {
        "title": "Choosing the Right Submersible Pump for Your Borewell",
        "slug": "choosing-right-submersible-pump",
        "category": "pump_maintenance",
        "content": "Pump selection depends on borewell depth, water yield, usage, power availability, and required discharge.",
    },
    {
        "title": "Government Schemes for Farm Irrigation",
        "slug": "government-schemes-farm-irrigation",
        "category": "government_schemes",
        "content": "Farmers can explore subsidies for drip irrigation, sprinkler systems, solar pumps, farm ponds, and groundwater recharge structures.",
    },
]


def load_json(filename):
    with open(COMMAND_DATA_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_username(value):
    username = re.sub(r"[^a-zA-Z0-9_]", "", value.split("@")[0].lower())
    return username or "user"


def get_or_create_user(username, email, password, first_name="", last_name=""):
    user = User.objects.filter(username=username).first() or User.objects.filter(email=email).first()
    if user is None:
        user = User(username=username, email=email, first_name=first_name, last_name=last_name, is_active=True)
        user.set_password(password)
        user.save()
        return user, True

    changed = False
    if email and user.email != email:
        user.email = email
        changed = True
    if first_name and user.first_name != first_name:
        user.first_name = first_name
        changed = True
    if last_name and user.last_name != last_name:
        user.last_name = last_name
        changed = True
    if changed:
        user.save()
    return user, False


def ensure_profile(user, phone, user_type, city=None, address=""):
    profile, _ = UserProfile.objects.update_or_create(
        user=user,
        defaults={
            "phone": phone,
            "user_type": user_type,
            "city": city,
            "address": address,
        },
    )
    return profile


def populate_cities(services_data, agri_data):
    cities = {}
    for city_data in CITY_DATA + agri_data.get("agricultural_cities", []):
        city, _ = City.objects.update_or_create(
            name=city_data["name"],
            defaults={
                "description": city_data.get("description", ""),
                "latitude": city_data.get("latitude"),
                "longitude": city_data.get("longitude"),
            },
        )
        cities[city.name] = city

    for vendor_data in services_data.get("vendors", []) + agri_data.get("specialized_agri_vendors", []):
        if vendor_data.get("location") not in cities:
            city, _ = City.objects.get_or_create(
                name=vendor_data["location"],
                defaults={"description": f'{vendor_data["location"]} service area'},
            )
            cities[city.name] = city
    return cities


def populate_services(services_data, agri_data):
    service_map = {}

    for category_data in services_data.get("service_categories", []):
        category, _ = ServiceCategory.objects.update_or_create(
            id=category_data["id"],
            defaults={
                "name": category_data["name"],
                "description": category_data.get("description", ""),
                "icon": category_data.get("icon", ""),
                "order": category_data.get("order", 0),
            },
        )

        for subcategory_index, sub_data in enumerate(category_data.get("subcategories", [])):
            subcategory, _ = ServiceSubcategory.objects.update_or_create(
                id=sub_data["id"],
                defaults={
                    "category": category,
                    "name": sub_data["name"],
                    "description": sub_data.get("description", ""),
                    "icon": sub_data.get("icon", ""),
                    "order": sub_data.get("order", subcategory_index),
                },
            )

            for service_index, service_data in enumerate(sub_data.get("services", [])):
                per_feet_amount = PER_FEET_AMOUNT_BY_SERVICE_ID.get(service_data["id"])
                service, _ = Service.objects.update_or_create(
                    id=service_data["id"],
                    defaults={
                        "subcategory": subcategory,
                        "name": service_data["name"],
                        "description": service_data.get("description", ""),
                        "features": service_data.get("features", []),
                        "per_feet_amount": per_feet_amount,
                        "popular": service_data.get("popular", False),
                        "order": service_data.get("order", service_index),
                    },
                )
                service_map[service.id] = service
                service_map[slugify(service.name)] = service

    agriculture_category, _ = ServiceCategory.objects.update_or_create(
        id="agriculture",
        defaults={
            "name": "Agriculture",
            "description": "Complete agricultural water management and irrigation solutions",
            "icon": "agriculture",
            "order": 1,
        },
    )
    field_subcategory, _ = ServiceSubcategory.objects.update_or_create(
        id="agriculture_field_services",
        defaults={
            "category": agriculture_category,
            "name": "Agriculture Field Services",
            "description": "Additional farm water, pond, pump, pipeline, and survey services",
            "icon": "agriculture",
            "order": 99,
        },
    )

    for index, service_data in enumerate(agri_data.get("agricultural_services", [])):
        service_id = slugify(service_data["name"]).replace("-", "_")
        features = []
        for key in ("target_crops", "benefits", "types", "pipe_types", "methods"):
            features.extend(service_data.get(key, []))
        for key in ("water_saving", "capacity_range", "depth_range", "power_range", "efficiency", "diameter_range", "accuracy"):
            if service_data.get(key):
                features.append(f"{key.replace('_', ' ').title()}: {service_data[key]}")

        service, _ = Service.objects.update_or_create(
            id=service_id,
            defaults={
                "subcategory": field_subcategory,
                "name": service_data["name"],
                "description": service_data.get("description", ""),
                "features": features,
                "popular": index < 2,
                "order": index,
            },
        )
        service_map[service.id] = service
        service_map[slugify(service.name)] = service

    return service_map


def resolve_service(service_map, raw_name):
    key = str(raw_name).strip()
    candidates = [
        key,
        key.replace(" ", "_").lower(),
        slugify(key),
        slugify(key).replace("-", "_"),
    ]
    aliases = {
        "borewell-drilling": "domestic_borewell_drilling",
        "deep-borewell-drilling": "deep_borewell_drilling",
        "submersible-pumps": "submersible_pump_installation",
        "groundwater-survey": "groundwater_assessment",
        "pump-installation": "submersible_pump_installation",
        "pump-repair": "pump_repair_servicing",
        "irrigation-pipeline": "farm_pipeline_networks",
        "water-storage-solutions": "water_storage_tank_installation",
        "drip-irrigation": "drip_irrigation_installation",
        "sprinkler-systems": "sprinkler_irrigation_systems",
        "farm-pond-construction": "farm_pond_construction",
        "solar-pump-installation": "solar_pump_installation",
        "open-well-construction": "open_well_construction",
        "micro-irrigation": "micro_irrigation_system_setup",
        "check-dams": "borewell_recharge_systems",
        "rainwater-harvesting": "borewell_recharge_systems",
        "recharge-wells": "borewell_recharge_systems",
        "farm-ponds": "farm_pond_construction",
        "step-wells-restoration": "open_well_construction",
        "solar-fencing": "solar_water_pumps",
        "solar-water-heaters": "solar_water_pumps",
        "automated-irrigation": "iot_irrigation_automation",
        "fertigation-systems": "drip_irrigation_installation",
        "drip-irrigation-design": "drip_irrigation_installation",
        "water-quality-testing": "industrial_water_quality_assessment",
        "water_quality_testing": "industrial_water_quality_assessment",
    }
    candidates.append(aliases.get(slugify(key), ""))

    for candidate in candidates:
        if candidate and candidate in service_map:
            return service_map[candidate]
    return None


def populate_users_and_vendors(services_data, agri_data, cities, service_map):
    admin, _ = get_or_create_user("admin", "admin@borewellmart.com", "admin123", "BorewellMart", "Admin")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    ensure_profile(admin, "9876543210", "admin", cities.get("Hubli"), "BorewellMart Admin Office")

    customers = []
    for index, city_name in enumerate(["Hubli", "Dharwad", "Bangalore", "Mysuru", "Vijayapura"], start=1):
        user, _ = get_or_create_user(
            f"customer{index}",
            f"customer{index}@borewellmart.com",
            "password123",
            "Customer",
            str(index),
        )
        ensure_profile(user, f"98765000{index:02d}", "customer", cities.get(city_name), f"{city_name}, Karnataka")
        customers.append(user)

    all_vendor_data = []
    all_vendor_data.extend(services_data.get("vendors", []))
    for agri_vendor in agri_data.get("specialized_agri_vendors", []):
        all_vendor_data.append(
            {
                "company_name": agri_vendor["company_name"],
                "location": agri_vendor["location"],
                "specialization": agri_vendor.get("specialization", ""),
                "services": agri_vendor.get("services", []),
                "phone": agri_vendor["phone"],
                "email": agri_vendor["email"],
                "address": f'{agri_vendor.get("service_area", agri_vendor["location"])}, Karnataka',
                "experience": max(timezone.now().year - agri_vendor.get("established_year", 2015), 1),
                "license_number": f"AGR-{slugify(agri_vendor['company_name']).upper()[:20]}",
            }
        )

    vendors = []
    for index, vendor_data in enumerate(all_vendor_data, start=1):
        city = cities.get(vendor_data["location"])
        email = vendor_data["email"].replace(" ", "")
        username = clean_username(email)
        if User.objects.filter(username=username).exclude(email=email).exists():
            username = f"{username}{index}"

        user, _ = get_or_create_user(username, email, "password123", vendor_data["company_name"][:30])
        ensure_profile(user, vendor_data["phone"], "vendor", city, vendor_data.get("address", ""))

        vendor, _ = Vendor.objects.update_or_create(
            user=user,
            defaults={
                "company_name": vendor_data["company_name"],
                "city": city,
                "experience": vendor_data.get("experience", 5),
                "phone": vendor_data["phone"],
                "email": email,
                "address": vendor_data.get("address", f"{city.name if city else vendor_data['location']}, Karnataka"),
                "license_number": vendor_data.get("license_number", ""),
                "certifications": vendor_data.get("specialization", ""),
                "rating": Decimal("4.50") if index % 2 else Decimal("4.30"),
                "verification_status": "verified",
                "is_emergency_available": vendor_data.get("is_emergency_available", index % 7 == 0),
            },
        )
        vendors.append(vendor)

        VendorPayment.objects.update_or_create(
            vendor=vendor,
            defaults={
                "amount": Decimal("999.00"),
                "status": "completed",
                "payment_method": "razorpay",
                "transaction_id": f"seed_txn_{vendor.id}",
                "razorpay_order_id": f"seed_order_{vendor.id}",
                "payment_date": timezone.now(),
                "paid_amount": Decimal("999.00"),
                "gateway_response": {"source": "populate_all_data.py", "status": "seeded"},
                "notes": "Seeded registration payment",
            },
        )

        assigned = 0
        for raw_service in vendor_data.get("services", []):
            service = resolve_service(service_map, raw_service)
            if not service:
                print(f"Warning: service not found for {vendor.company_name}: {raw_service}")
                continue
            VendorService.objects.update_or_create(
                vendor=vendor,
                service=service,
                defaults={
                    "price": Decimal("5000.00"),
                    "description": f"Professional {service.name} by {vendor.company_name}",
                },
            )
            assigned += 1

        if assigned == 0:
            for service in list(Service.objects.all().order_by("order")[:3]):
                VendorService.objects.get_or_create(
                    vendor=vendor,
                    service=service,
                    defaults={"price": 5000, "description": f"Professional {service.name} service"},
                )

        VendorGallery.objects.get_or_create(
            vendor=vendor,
            caption=f"{vendor.company_name} drilling and water service work",
            image_type="previous_work",
            defaults={"image": "vendor_gallery/sample-work.jpg"},
        )

    return admin, customers, vendors


def populate_missing_vendor_records():
    for vendor in Vendor.objects.all():
        VendorPayment.objects.get_or_create(
            vendor=vendor,
            defaults={
                "amount": Decimal("999.00"),
                "status": "completed",
                "payment_method": "razorpay",
                "transaction_id": f"seed_txn_{vendor.id}",
                "razorpay_order_id": f"seed_order_{vendor.id}",
                "payment_date": timezone.now(),
                "paid_amount": Decimal("999.00"),
                "gateway_response": {"source": "populate_all_data.py", "status": "seeded"},
                "notes": "Seeded registration payment",
            },
        )
        VendorGallery.objects.get_or_create(
            vendor=vendor,
            caption=f"{vendor.company_name} drilling and water service work",
            image_type="previous_work",
            defaults={"image": "vendor_gallery/sample-work.jpg"},
        )


def populate_customer_activity(customers, vendors):
    for index, customer in enumerate(customers):
        vendor = vendors[index % len(vendors)]
        vendor_service = vendor.vendor_services.select_related("service").first()
        if not vendor_service:
            continue

        enquiry, _ = Enquiry.objects.update_or_create(
            customer=customer,
            vendor=vendor,
            subservice=vendor_service.subservice,
            defaults={
                "message": f"I need details for {vendor_service.subservice.name} near my location.",
                "status": "responded" if index % 2 == 0 else "pending",
                "vendor_response": "Site visit and quotation can be arranged within 24 hours.",
                "quoted_amount": vendor_service.price,
            },
        )

        booking, _ = Booking.objects.update_or_create(
            customer=customer,
            vendor=vendor,
            subservice=vendor_service.subservice,
            date=date.today() + timedelta(days=index + 1),
            time=time(hour=10 + index, minute=0),
            defaults={
                "enquiry": enquiry,
                "address": customer.userprofile.address or f"{vendor.city.name if vendor.city else 'Karnataka'}",
                "description": f"Sample booking for {vendor_service.subservice.name}",
                "status": "completed" if index < 3 else "accepted",
                "is_emergency": index == 0,
            },
        )

        Review.objects.update_or_create(
            customer=customer,
            vendor=vendor,
            defaults={
                "booking": booking,
                "rating": 5 if index % 2 == 0 else 4,
                "comment": "Good response, clear quotation, and professional service.",
            },
        )
        FavoriteVendor.objects.get_or_create(customer=customer, vendor=vendor)
        vendor.update_rating()


def populate_blogs(author, services_data, agri_data):
    for blog_data in BLOG_DATA:
        Blog.objects.update_or_create(
            slug=blog_data["slug"],
            defaults={
                "title": blog_data["title"],
                "content": blog_data["content"],
                "category": blog_data["category"],
                "author": author,
            },
        )

    for scheme in services_data.get("government_schemes", []) + agri_data.get("government_schemes", []):
        slug = slugify(scheme["scheme_name"])
        Blog.objects.update_or_create(
            slug=slug,
            defaults={
                "title": scheme["scheme_name"],
                "content": f'{scheme.get("description", "")}\n\nSubsidy: {scheme.get("subsidy", "")}\nEligible services: {", ".join(scheme.get("eligible_services", []))}',
                "category": "government_schemes",
                "author": author,
            },
        )


def print_summary():
    print("\nDatabase population complete.")
    print(f"Cities: {City.objects.count()}")
    print(f"Categories: {ServiceCategory.objects.count()}")
    print(f"Subcategories: {ServiceSubcategory.objects.count()}")
    print(f"Services: {Service.objects.count()}")
    print(f"Services with per-feet amount: {Service.objects.filter(per_feet_amount__isnull=False).count()}")
    print(f"Users: {User.objects.count()}")
    print(f"Profiles: {UserProfile.objects.count()}")
    print(f"Vendors: {Vendor.objects.count()}")
    print(f"Vendor payments: {VendorPayment.objects.count()}")
    print(f"Vendor services: {VendorService.objects.count()}")
    print(f"Enquiries: {Enquiry.objects.count()}")
    print(f"Bookings: {Booking.objects.count()}")
    print(f"Reviews: {Review.objects.count()}")
    print(f"Favorites: {FavoriteVendor.objects.count()}")
    print(f"Gallery records: {VendorGallery.objects.count()}")
    print(f"Blogs: {Blog.objects.count()}")
    print("\nLogin accounts:")
    print("Admin: admin / admin123")
    print("Customers: customer1 to customer5 / password123")
    print("Vendors: use seeded vendor usernames / password123")


def main():
    services_data = load_json("services_data.json")
    agri_data = load_json("agri_vendors_data.json")

    with transaction.atomic():
        cities = populate_cities(services_data, agri_data)
        service_map = populate_services(services_data, agri_data)
        admin, customers, vendors = populate_users_and_vendors(services_data, agri_data, cities, service_map)
        populate_missing_vendor_records()
        populate_customer_activity(customers, vendors)
        populate_blogs(admin, services_data, agri_data)

    print_summary()


if __name__ == "__main__":
    main()
