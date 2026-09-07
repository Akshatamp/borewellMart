from django.core.management.base import BaseCommand
from core.models import Vendor, VendorEquipment


class Command(BaseCommand):
    help = 'Add sample old equipment for testing'

    def handle(self, *args, **options):
        # Get the first vendor
        vendor = Vendor.objects.first()
        if not vendor:
            self.stdout.write(self.style.ERROR('No vendors found in database. Please create a vendor first.'))
            return

        self.stdout.write(f'Adding equipment for vendor: {vendor.company_name}')

        # Sample equipment data
        equipment_data = [
            {
                'title': 'Used Rotatory Drilling Rig - 150mm Capacity',
                'description': 'Well-maintained rotatory drilling rig with 150mm drilling capacity. Perfect for borewell drilling up to 500 feet depth. Engine in good condition, recently serviced. Includes all necessary accessories like drill pipes, bits, and pumping equipment.',
                'category': 'drilling_machine',
                'condition': 'good',
                'price': 285000,
                'is_negotiable': True,
                'year_manufactured': 2018,
                'brand': 'L&T Construction',
                'location': 'Hubli, Karnataka',
                'is_available': True,
            },
            {
                'title': '7.5 HP Submersible Pump Set - Stainless Steel',
                'description': 'Heavy-duty 7.5 HP submersible pump with stainless steel body. Suitable for deep borewells up to 600 feet. Single-phase motor with thermal overload protection. Includes control panel and 100m of heavy-duty cable. Used for 2 seasons only.',
                'category': 'pump',
                'condition': 'excellent',
                'price': 45000,
                'is_negotiable': True,
                'year_manufactured': 2021,
                'brand': 'CRI Pumps',
                'location': 'Dharwad, Karnataka',
                'is_available': True,
            },
        ]

        # Create equipment items
        for data in equipment_data:
            # Check if equipment with same title already exists for this vendor
            existing = VendorEquipment.objects.filter(vendor=vendor, title=data['title']).first()
            if existing:
                self.stdout.write(self.style.WARNING(f'Equipment "{data["title"]}" already exists. Skipping.'))
                continue

            equipment = VendorEquipment.objects.create(vendor=vendor, **data)
            self.stdout.write(self.style.SUCCESS(f'Created: {equipment.title} (ID: {equipment.id})'))

        self.stdout.write(self.style.SUCCESS('Sample equipment added successfully!'))
