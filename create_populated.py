# Script to create populated.py with data and import logic
with open('db_exported_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

import_logic = '''

# ===== IMPORT LOGIC =====
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Sector, Service, SubService, Vendor, City, User, UserProfile, VendorService

print("Starting data import...")

# Import Cities
print("\\nImporting cities...")
for city_data in CITY_DATA:
    try:
        city, created = City.objects.get_or_create(
            name=city_data['name'],
            defaults={
                'slug': city_data['slug'],
                'state': city_data['state'],
                'description': city_data['description'],
                'latitude': city_data['latitude'],
                'longitude': city_data['longitude'],
                'vendor_count': city_data['vendor_count'],
                'service_count': city_data['service_count']
            }
        )
        if created:
            print(f"  Created city: {city.name}")
        else:
            city.slug = city_data['slug']
            city.state = city_data['state']
            city.description = city_data['description']
            city.latitude = city_data['latitude']
            city.longitude = city_data['longitude']
            city.vendor_count = city_data['vendor_count']
            city.service_count = city_data['service_count']
            city.save()
            print(f"  Updated city: {city.name}")
    except Exception as e:
        print(f"  Error importing city {city_data['name']}: {e}")

print(f"City import complete. Total: {City.objects.count()}")

# Import Sectors, Services, and SubServices
print("\\nImporting sectors, services, and subservices...")
for sector_name, services_data in DATA.items():
    sector, created = Sector.objects.get_or_create(
        name=sector_name,
        defaults={
            'id': sector_name.lower().replace(' ', '_'),
            'slug': sector_name.lower().replace(' ', '_'),
            'description': f'{sector_name} sector'
        }
    )
    if created:
        print(f"  Created sector: {sector.name}")
    
    for service_name, subservices_data in services_data.items():
        service, created = Service.objects.get_or_create(
            name=service_name,
            sector=sector,
            defaults={
                'id': service_name.lower().replace(' ', '_'),
                'slug': service_name.lower().replace(' ', '_'),
                'description': f'{service_name} - {sector_name}'
            }
        )
        if created:
            print(f"    Created service: {service.name}")
        
        for subservice_name, items in subservices_data.items():
            if isinstance(items, list) and items:
                parent, created = SubService.objects.get_or_create(
                    name=subservice_name,
                    service=service,
                    parent=None,
                    defaults={
                        'id': f"{service.id}_{subservice_name.lower().replace(' ', '_').replace('&', 'and').replace('×', 'x')}",
                        'slug': f"{service.id}_{subservice_name.lower().replace(' ', '_').replace('&', 'and').replace('×', 'x')}",
                        'description': f'{subservice_name} - {service_name}'
                    }
                )
                if created:
                    print(f"      Created category: {parent.name}")
                
                for item in items:
                    if isinstance(item, dict):
                        item_name = item.get('name')
                        per_feet_amount = item.get('per_feet_amount')
                        features = item.get('features', [])
                        description = item.get('description', '')
                    else:
                        item_name = item
                        per_feet_amount = None
                        features = []
                        description = ''
                    
                    if item_name:
                        child_id = f"{parent.id}_{item_name.lower().replace(' ', '_').replace('&', 'and').replace('×', 'x')}"
                        child, created = SubService.objects.get_or_create(
                            id=child_id,
                            defaults={
                                'name': item_name,
                                'service': service,
                                'parent': parent,
                                'slug': child_id,
                                'description': description or f'{item_name} - {subservice_name}',
                                'per_feet_amount': per_feet_amount,
                                'features': features
                            }
                        )
                        if created:
                            print(f"        Created subservice: {child.name}")
                        else:
                            if per_feet_amount and child.per_feet_amount is None:
                                child.per_feet_amount = per_feet_amount
                            if features and not child.features:
                                child.features = features
                            child.save()

print(f"SubServices import complete. Total: {SubService.objects.count()}")

# Import Vendors
print("\\nImporting vendors...")
for vendor_data in VENDOR_DATA:
    try:
        city = None
        if vendor_data.get('city'):
            city, _ = City.objects.get_or_create(name=vendor_data['city'])
        
        vendor, created = Vendor.objects.get_or_create(
            company_name=vendor_data['company_name'],
            defaults={
                'phone': vendor_data['phone'],
                'email': vendor_data['email'],
                'address': vendor_data['address'],
                'city': city,
                'experience': vendor_data['experience'],
                'rating': vendor_data['rating'],
                'verification_status': vendor_data['verification_status'],
                'is_emergency_available': vendor_data['is_emergency_available'],
                'services_count': vendor_data['services_count'],
                'bookings_count': vendor_data['bookings_count']
            }
        )
        if created:
            print(f"  Created vendor: {vendor.company_name}")
        else:
            vendor.phone = vendor_data['phone']
            vendor.email = vendor_data['email']
            vendor.address = vendor_data['address']
            vendor.city = city
            vendor.experience = vendor_data['experience']
            vendor.rating = vendor_data['rating']
            vendor.verification_status = vendor_data['verification_status']
            vendor.is_emergency_available = vendor_data['is_emergency_available']
            vendor.services_count = vendor_data['services_count']
            vendor.bookings_count = vendor_data['bookings_count']
            vendor.save()
            print(f"  Updated vendor: {vendor.company_name}")
        
        for service_data in vendor_data.get('services', []):
            try:
                subservice = SubService.objects.get(id=service_data['subservice_id'])
                vendor_service, created = VendorService.objects.get_or_create(
                    vendor=vendor,
                    subservice=subservice,
                    defaults={
                        'price': service_data.get('price'),
                        'description': service_data.get('description')
                    }
                )
                if created:
                    print(f"    Added service: {service_data['subservice']}")
            except SubService.DoesNotExist:
                print(f"    Subservice not found: {service_data['subservice_id']}")
    except Exception as e:
        print(f"  Error importing vendor {vendor_data['company_name']}: {e}")

print(f"Vendor import complete. Total: {Vendor.objects.count()}")

# Import Customers
print("\\nImporting customers...")
for customer_data in CUSTOMER_DATA:
    try:
        user, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults={
                'email': customer_data['email'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name']
            }
        )
        if created:
            print(f"  Created user: {user.username}")
        
        city = None
        if customer_data.get('city'):
            city, _ = City.objects.get_or_create(name=customer_data['city'])
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': customer_data['phone'],
                'city': city,
                'address': customer_data['address'],
                'user_type': customer_data['user_type']
            }
        )
        if created:
            print(f"    Created profile for: {user.username}")
        else:
            profile.phone = customer_data['phone']
            profile.city = city
            profile.address = customer_data['address']
            profile.user_type = customer_data['user_type']
            profile.save()
            print(f"    Updated profile for: {user.username}")
    except Exception as e:
        print(f"  Error importing customer {customer_data['username']}: {e}")

print(f"Customer import complete. Total: {UserProfile.objects.filter(user_type='customer').count()}")

print("\\n=== Import Complete ===")
print(f"Sectors: {Sector.objects.count()}")
print(f"Services: {Service.objects.count()}")
print(f"SubServices: {SubService.objects.count()}")
print(f"Vendors: {Vendor.objects.count()}")
print(f"Cities: {City.objects.count()}")
print(f"Customers: {UserProfile.objects.filter(user_type='customer').count()}")
'''

with open('populated.py', 'w', encoding='utf-8') as f:
    f.write(content + import_logic)

print('populated.py created successfully')
