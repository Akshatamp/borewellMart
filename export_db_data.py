import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, SubService, Vendor, City, User, UserProfile

# Export all sectors, services, and subservices
print("Exporting database data...")

DATA = {}

# Get all sectors
sectors = Sector.objects.all().order_by('order')
print(f"Found {sectors.count()} sectors")

for sector in sectors:
    sector_name = sector.name
    DATA[sector_name] = {}
    
    # Get all services for this sector
    services = sector.services.all().order_by('order')
    print(f"  {sector_name}: {services.count()} services")
    
    for service in services:
        service_name = service.name
        DATA[sector_name][service_name] = {}
        
        # Get all subservices for this service
        subservices = service.subservices.all().order_by('order')
        
        if subservices.exists():
            # Group subservices by parent (categories)
            parent_subservices = subservices.filter(parent__isnull=True)
            child_subservices = subservices.filter(parent__isnull=False)
            
            for parent in parent_subservices:
                parent_name = parent.name
                DATA[sector_name][service_name][parent_name] = []
                
                # Get children of this parent
                children = child_subservices.filter(parent=parent)
                for child in children:
                    child_data = {
                        'name': child.name,
                        'description': child.description,
                        'per_feet_amount': float(child.per_feet_amount) if child.per_feet_amount else None,
                        'features': child.features if child.features else []
                    }
                    DATA[sector_name][service_name][parent_name].append(child_data)
            
            # Also add subservices without parent as direct children
            direct_children = subservices.filter(parent__isnull=True)
            if direct_children.exists() and not parent_subservices.exists():
                DATA[sector_name][service_name]['items'] = []
                for child in direct_children:
                    child_data = {
                        'name': child.name,
                        'description': child.description,
                        'per_feet_amount': float(child.per_feet_amount) if child.per_feet_amount else None,
                        'features': child.features if child.features else []
                    }
                    DATA[sector_name][service_name]['items'].append(child_data)
        else:
            # No subservices, add empty list
            DATA[sector_name][service_name]['items'] = []

# Export verified vendors
print("\nExporting verified vendors...")
verified_vendors = Vendor.objects.filter(verification_status='verified')
print(f"Found {verified_vendors.count()} verified vendors")

VENDOR_DATA = []

for vendor in verified_vendors:
    vendor_data = {
        'company_name': vendor.company_name,
        'phone': vendor.phone,
        'email': vendor.email,
        'address': vendor.address,
        'city': vendor.city.name if vendor.city else None,
        'state': vendor.city.state if vendor.city else None,
        'experience': vendor.experience,
        'rating': float(vendor.rating) if vendor.rating else None,
        'verification_status': vendor.verification_status,
        'is_emergency_available': vendor.is_emergency_available,
        'services_count': vendor.services_count,
        'bookings_count': vendor.bookings_count,
        'services': []
    }
    
    # Get vendor services
    for vendor_service in vendor.vendor_services.all():
        service_data = {
            'subservice': vendor_service.subservice.name,
            'subservice_id': vendor_service.subservice.id,
            'service': vendor_service.subservice.service.name,
            'service_id': vendor_service.subservice.service.id,
            'sector': vendor_service.subservice.service.sector.name,
            'price': float(vendor_service.price) if vendor_service.price else None,
            'description': vendor_service.description
        }
        vendor_data['services'].append(service_data)
    
    VENDOR_DATA.append(vendor_data)

# Export cities with states
print("\nExporting cities...")
cities = City.objects.all().order_by('state', 'name')
print(f"Found {cities.count()} cities")

CITY_DATA = []

for city in cities:
    city_data = {
        'name': city.name,
        'slug': city.slug,
        'state': city.state,
        'description': city.description,
        'latitude': float(city.latitude) if city.latitude else None,
        'longitude': float(city.longitude) if city.longitude else None,
        'vendor_count': city.vendor_count,
        'service_count': city.service_count
    }
    CITY_DATA.append(city_data)

# Export customer users
print("\nExporting customer users...")
customer_profiles = UserProfile.objects.filter(user_type='customer')
print(f"Found {customer_profiles.count()} customer users")

CUSTOMER_DATA = []

for profile in customer_profiles:
    try:
        customer_data = {
            'username': profile.user.username,
            'email': profile.user.email,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'phone': profile.phone,
            'city': profile.city.name if profile.city else None,
            'state': profile.city.state if profile.city else None,
            'address': profile.address,
            'user_type': profile.user_type,
            'date_joined': profile.user.date_joined.isoformat() if profile.user.date_joined else None
        }
        CUSTOMER_DATA.append(customer_data)
    except Exception as e:
        print(f"  Error exporting customer {profile.user.username}: {e}")

# Write to Python file
output_file = 'db_exported_data.py'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Exported Database Data\n")
    f.write("# Generated on: " + str(django.utils.timezone.now()) + "\n\n")
    f.write("DATA = " + str(DATA) + "\n\n")
    f.write("VENDOR_DATA = " + str(VENDOR_DATA) + "\n\n")
    f.write("CITY_DATA = " + str(CITY_DATA) + "\n\n")
    f.write("CUSTOMER_DATA = " + str(CUSTOMER_DATA) + "\n")

print(f"\nData exported successfully to {output_file}")
print(f"  - {sectors.count()} sectors")
print(f"  - {Service.objects.count()} services")
print(f"  - {SubService.objects.count()} subservices")
print(f"  - {verified_vendors.count()} verified vendors")
print(f"  - {cities.count()} cities")
print(f"  - {customer_profiles.count()} customers")
