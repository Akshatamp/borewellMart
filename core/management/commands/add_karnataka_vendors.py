import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import City, SubService, Vendor, VendorService, UserProfile


class Command(BaseCommand):
    help = 'Add vendors (2-3 per city) for all Karnataka cities that have no vendors yet'

    # Company name prefixes for variety
    COMPANY_PREFIXES = [
        'Royal', 'Heritage', 'Premium', 'Elite', 'Super', 'Master', 'Expert', 'Professional',
        'Quality', 'Reliable', 'Speedy', 'Smart', 'Modern', 'Traditional', 'A1', 'Top',
        'Best', 'Golden', 'Silver', 'Happy', 'Lucky', 'Shree', 'Sri', 'Jai', 'New'
    ]

    COMPANY_SUFFIXES = [
        'Borewell', 'Water Works', 'Pump Services', 'Drilling', 'Aqua Solutions',
        'Irrigation Systems', 'Water Tech', 'Well Solutions', 'Hydro Systems',
        'Pump Masters', 'Bore Wells', 'Agri Wells', 'Farm Water', 'Deep Wells'
    ]

    def generate_vendor_data(self, city_name, index):
        """Generate vendor data dynamically based on city and index"""
        prefix = self.COMPANY_PREFIXES[index % len(self.COMPANY_PREFIXES)]
        suffix = self.COMPANY_SUFFIXES[(index // 2) % len(self.COMPANY_SUFFIXES)]
        company_name = f'{city_name} {prefix} {suffix}'

        # Generate unique phone and email
        phone_base = 9876500000 + (hash(city_name) % 10000000) + (index * 1000)
        phone = str(phone_base)[-10:]  # Last 10 digits
        email = f'{company_name.lower().replace(" ", "")}{index}@gmail.com'

        return {
            'company': company_name,
            'exp': random.randint(10, 25),
            'phone': phone,
            'email': email
        }

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding vendors for Karnataka cities...')

        # Get all subservices
        subservices = list(SubService.objects.all())

        if not subservices:
            self.stdout.write(self.style.ERROR('No subservices found in database. Please load services first.'))
            return

        self.stdout.write(f'Found {len(subservices)} subservices to assign.')

        # Get all Karnataka cities
        karnataka_cities = City.objects.filter(state='Karnataka')
        total_cities = karnataka_cities.count()

        if total_cities == 0:
            self.stdout.write(self.style.ERROR('No cities found with state=Karnataka'))
            return

        self.stdout.write(f'Found {total_cities} Karnataka cities.')

        # Stats
        cities_processed = 0
        cities_skipped = 0
        vendors_created = 0
        vendors_updated = 0

        # Counter for unique vendor usernames
        vendor_start_num = 100

        for city in karnataka_cities:
            city_name = city.name
            self.stdout.write(f'\nProcessing {city_name}...')

            # Check if vendors already exist in this city
            existing_vendors = Vendor.objects.filter(city=city)
            existing_count = existing_vendors.count()

            if existing_count > 0:
                self.stdout.write(self.style.WARNING(f'  Skipping: {existing_count} vendor(s) already exist in {city_name}'))
                cities_skipped += 1
                continue

            # Add 2-3 vendors for this city
            num_vendors = random.randint(2, 3)
            self.stdout.write(f'  Adding {num_vendors} vendor(s)...')

            for i in range(num_vendors):
                vendor_start_num += 1
                username = f'vendor{vendor_start_num}'

                # Generate vendor data
                v_data = self.generate_vendor_data(city_name, i)

                # Create user for vendor
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': v_data['email'],
                        'first_name': city_name.replace('-', ' ').split()[0]  # First word of city
                    }
                )

                if user_created:
                    user.set_password('Vendor@123')
                    user.save()

                    # Create user profile
                    UserProfile.objects.create(
                        user=user,
                        phone=v_data['phone'],
                        user_type='vendor',
                        city=city,
                        state='Karnataka'
                    )
                else:
                    self.stdout.write(f'  User {username} already exists, skipping...')
                    continue

                # Create vendor
                vendor = Vendor.objects.create(
                    user=user,
                    company_name=v_data['company'],
                    city=city,
                    state='Karnataka',
                    experience=v_data['exp'],
                    phone=v_data['phone'],
                    email=v_data['email'],
                    address=f'{v_data["company"]}, {city_name}, Karnataka',
                    verification_status='verified',
                    rating=round(random.uniform(4.0, 4.9), 1)
                )
                vendors_created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {vendor.company_name}'))

                # Assign 2-3 subservices to each vendor
                # Rotate through subservices to give variety
                start_idx = (vendors_created * 3) % len(subservices)
                vendor_subservices = subservices[start_idx:start_idx + 3]

                if not vendor_subservices:
                    vendor_subservices = subservices[:3]

                for j, subservice in enumerate(vendor_subservices):
                    VendorService.objects.create(
                        vendor=vendor,
                        subservice=subservice,
                        price=5000 + (j * 2000),
                        description=f'Professional {subservice.name} in {city_name}'
                    )

                assigned = [vs.subservice.name for vs in vendor.vendor_services.all()[:3]]
                self.stdout.write(f'    Services: {", ".join(assigned)}')

            cities_processed += 1

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('Vendor Addition Complete!'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total Karnataka cities: {total_cities}')
        self.stdout.write(f'Cities processed: {cities_processed}')
        self.stdout.write(f'Cities skipped (had vendors): {cities_skipped}')
        self.stdout.write(f'Vendors created: {vendors_created}')
        self.stdout.write('='*60)
        self.stdout.write('Default password: Vendor@123')
        self.stdout.write('='*60)
