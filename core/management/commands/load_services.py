from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import (
    Sector, Service, SubService, City, Vendor, VendorService,
    User, UserProfile
)
from django.db import transaction
import json
import os


class Command(BaseCommand):
    help = 'Load hierarchical services and vendors data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='core/management/commands/services_data.json',
            help='Path to services JSON file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing services and vendors before loading'
        )

    def handle(self, *args, **options):
        file_path = options.get('file')
        clear_existing = options.get('clear')

        if clear_existing:
            self.stdout.write('Clearing existing data...')
            # Delete in correct order to respect foreign key constraints
            from core.models import Booking, Enquiry, ForumThread
            VendorService.objects.all().delete()
            Booking.objects.all().delete()
            Enquiry.objects.all().delete()
            ForumThread.objects.all().delete()
            User.objects.filter(userprofile__user_type='vendor').delete()
            Vendor.objects.all().delete()
            SubService.objects.all().delete()
            Service.objects.all().delete()
            Sector.objects.all().delete()
            self.stdout.write(self.style.WARNING('All existing services and vendors cleared'))

        # Load JSON data
        full_path = os.path.join(settings.BASE_DIR, file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {full_path}'))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON: {e}'))
            return

        # Track created items
        stats = {
            'sectors': 0,
            'services': 0,
            'subservices': 0,
            'vendors': 0,
            'vendor_services': 0
        }

        # Load Services
        self.stdout.write('\nLoading Services:')
        for category_data in data.get('service_categories', []):
            # Create or update sector (formerly category)
            sector, created = Sector.objects.update_or_create(
                id=category_data['id'],
                defaults={
                    'name': category_data['name'],
                    'description': category_data.get('description', ''),
                    'icon': category_data.get('icon', ''),
                    'order': category_data.get('order', stats['sectors'])
                }
            )
            if created:
                stats['sectors'] += 1
                self.stdout.write(f'  Created sector: {sector.name}')

            # Process services (formerly subcategories)
            service_order = 0
            for sub_data in category_data.get('subcategories', []):
                service, created = Service.objects.update_or_create(
                    id=sub_data['id'],
                    defaults={
                        'sector': sector,
                        'name': sub_data['name'],
                        'description': sub_data.get('description', ''),
                        'icon': sub_data.get('icon', ''),
                        'order': sub_data.get('order', service_order)
                    }
                )
                if created:
                    stats['services'] += 1
                    self.stdout.write(f'    Created service: {service.name}')

                # Process subservices (formerly services)
                subservice_order = 0
                for service_data in sub_data.get('services', []):
                    subservice, created = SubService.objects.update_or_create(
                        id=service_data['id'],
                        defaults={
                            'service': service,
                            'name': service_data['name'],
                            'description': service_data.get('description', ''),
                            'features': service_data.get('features', []),
                            'popular': service_data.get('popular', False),
                            'order': service_data.get('order', subservice_order)
                        }
                    )
                    if created:
                        stats['subservices'] += 1
                        self.stdout.write(f'      Created subservice: {subservice.name}')
                    subservice_order += 1
                service_order += 1

        # Load Vendors
        self.stdout.write('\nLoading Vendors:')
        for vendor_data in data.get('vendors', []):
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
                            experience=vendor_data.get('experience', 5),
                            phone=vendor_data['phone'],
                            email=vendor_data['email'],
                            address=vendor_data.get('address', f'{city.name}, Karnataka'),
                            license_number=vendor_data.get('license_number', ''),
                            verification_status='verified',
                            rating=4.5,
                            is_emergency_available=vendor_data.get('is_emergency_available', False)
                        )
                        stats['vendors'] += 1
                        self.stdout.write(f'  Created vendor: {vendor.company_name}')

                        # Assign subservices to vendor
                        for service_id in vendor_data.get('services', []):
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
                                stats['vendor_services'] += 1
                            except SubService.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(f'    SubService not found: {service_id}')
                                )
                    else:
                        self.stdout.write(f'  Vendor already exists: {vendor_data["company_name"]}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating vendor {vendor_data.get("company_name")}: {e}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n' + '='*60 +
            f'\nSummary:'
            f'\n  Sectors: {stats["sectors"]}'
            f'\n  Services: {stats["services"]}'
            f'\n  SubServices: {stats["subservices"]}'
            f'\n  Vendors: {stats["vendors"]}'
            f'\n  Vendor Services: {stats["vendor_services"]}'
            f'\n' + '='*60
        ))
