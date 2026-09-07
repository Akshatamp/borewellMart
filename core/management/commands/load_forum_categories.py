from django.core.management.base import BaseCommand
from core.models import ForumCategory, Sector


class Command(BaseCommand):
    help = 'Load forum categories into the database'

    def handle(self, *args, **kwargs):
        forum_categories_data = [
            {
                'name': 'General Discussion',
                'description': 'Talk about anything related to borewell services and equipment',
                'icon': 'chat-left-text',
                'order': 1,
                'is_service_related': False,
                'slug': 'general-discussion'
            },
            {
                'name': 'Borewell Drilling',
                'description': 'Discuss borewell drilling techniques, equipment, and best practices',
                'icon': 'water',
                'order': 2,
                'is_service_related': True,
                'slug': 'borewell-drilling'
            },
            {
                'name': 'Water Pumps & Motors',
                'description': 'Questions and discussions about water pumps, submersible motors, and installations',
                'icon': 'gear',
                'order': 3,
                'is_service_related': True,
                'slug': 'water-pumps-motors'
            },
            {
                'name': 'Pipes & Fittings',
                'description': 'Discuss PVC, HDPE pipes, fittings, and plumbing solutions',
                'icon': 'diagram-3',
                'order': 4,
                'is_service_related': True,
                'slug': 'pipes-fittings'
            },
            {
                'name': 'Maintenance & Repairs',
                'description': 'Tips for maintaining borewell systems and troubleshooting common issues',
                'icon': 'tools',
                'order': 5,
                'is_service_related': False,
                'slug': 'maintenance-repairs'
            },
            {
                'name': 'Water Quality & Testing',
                'description': 'Discuss water quality testing, purification, and treatment methods',
                'icon': 'droplet',
                'order': 6,
                'is_service_related': False,
                'slug': 'water-quality-testing'
            },
            {
                'name': 'Equipment Marketplace',
                'description': 'Buy, sell, or trade borewell equipment and machinery',
                'icon': 'cart',
                'order': 7,
                'is_service_related': False,
                'slug': 'equipment-marketplace'
            },
            {
                'name': 'Agricultural Services',
                'description': 'Discussions about irrigation, agricultural borewells, and farming solutions',
                'icon': 'tree',
                'order': 8,
                'is_service_related': True,
                'slug': 'agricultural-services'
            },
            {
                'name': 'Construction Services',
                'description': 'Talk about construction borewells and foundation drilling',
                'icon': 'building',
                'order': 9,
                'is_service_related': True,
                'slug': 'construction-services'
            },
            {
                'name': 'Tips & Tricks',
                'description': 'Share your tips, tricks, and DIY solutions for borewell projects',
                'icon': 'lightbulb',
                'order': 10,
                'is_service_related': False,
                'slug': 'tips-tricks'
            },
            {
                'name': 'Vendor Recommendations',
                'description': 'Recommend reliable vendors and share your experiences',
                'icon': 'star',
                'order': 11,
                'is_service_related': False,
                'slug': 'vendor-recommendations'
            },
            {
                'name': 'Pricing & Cost Discussion',
                'description': 'Discuss pricing, get quotes, and share cost information',
                'icon': 'currency-rupee',
                'order': 12,
                'is_service_related': False,
                'slug': 'pricing-cost-discussion'
            },
        ]

        created_count = 0
        updated_count = 0

        for category_data in forum_categories_data:
            slug = category_data.pop('slug')
            category, created = ForumCategory.objects.update_or_create(
                slug=slug,
                defaults=category_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created forum category: {category.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated forum category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully processed {created_count + updated_count} forum categories '
                f'({created_count} created, {updated_count} updated)'
            )
        )
