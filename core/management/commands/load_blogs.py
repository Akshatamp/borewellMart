from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Blog, UserProfile, City


class Command(BaseCommand):
    help = 'Load sample blog articles for BorewellMart'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample blog articles...')

        # Create or get admin user for blog author
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@borewellmart.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            # Create user profile with any city
            city = City.objects.first()
            if city:
                UserProfile.objects.create(
                    user=admin_user,
                    phone='9876543999',
                    user_type='admin',
                    city=city
                )
            self.stdout.write(self.style.SUCCESS('Created admin account for blog author'))
        elif not admin_user.is_staff:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Updated admin account for blog author'))

        # Sample blog data
        blogs_data = [
            {
                'title': 'Complete Guide to Borewell Drilling: Process, Cost, and Tips',
                'slug': 'complete-guide-borewell-drilling-process-cost-tips',
                'content': '''Borewell drilling is a critical investment for accessing groundwater. This comprehensive guide covers everything you need to know about the drilling process, expected costs, permitting requirements, and tips for ensuring a successful borewell. We discuss site selection, geologic survey importance, drilling methods used in India, and post-drilling care. Learn how to identify potential drilling locations and what to expect during the entire process from start to finish.''',
                'category': 'drilling'
            },
            {
                'title': '5 Essential Borewell Maintenance Tips for Year-Round Water Supply',
                'slug': 'essential-borewell-maintenance-tips-year-round-water',
                'content': '''Regular maintenance is key to ensuring your borewell provides clean water year after year. In this article, we cover the top 5 maintenance practices every borewell owner should follow: periodic water level monitoring, pump inspection schedules, water quality testing, cleaning frequency recommendations, and identifying early warning signs of problems. These simple maintenance routines can extend your borewell's life by years and prevent costly repairs.''',
                'category': 'maintenance'
            },
            {
                'title': 'Understanding Groundwater Levels: When to Drill and When to Wait',
                'slug': 'understanding-groundwater-levels-drill-wait',
                'content': '''Groundwater levels fluctuate seasonally and understanding these patterns is crucial before drilling. This article explains how to interpret groundwater survey reports, seasonal water table variations in different regions of India, and the optimal timing for new borewell drilling. We also cover how to read hydrogeological maps and why consulting local experts familiar with your area's water table behavior is essential for success.''',
                'category': 'general'
            },
            {
                'title': 'Common Borewell Water Problems and Their Solutions',
                'slug': 'common-borewell-water-problems-solutions',
                'content': '''Is your borewell water salty, smelly, or contaminated? This article identifies common water quality issues including high TDS, bacterial contamination, iron content, and chemical pollutants. We explain each problem's causes, health implications, and practical solutions ranging from simple filtration systems to advanced treatment options. Learn when to test your water and what treatment methods work best for specific contaminants found in borewell water.''',
                'category': 'water_quality'
            },
            {
                'title': 'Submersible Pumps 101: Selection, Installation, and Maintenance',
                'slug': 'submersible-pumps-selection-installation-maintenance',
                'content': '''Choosing the right submersible pump is crucial for efficient water extraction. This guide covers pump selection based on borewell depth and yield, horsepower calculations, energy efficiency considerations, and reputable pump brands available in India. We also explain proper installation techniques, vertical mounting best practices, control panel setup, and routine maintenance that extends pump life. Includes troubleshooting common pump problems and when to call for professional service.''',
                'category': 'pump'
            },
            {
                'title': 'Borewell Failure Recovery: Deepening, Flushing, and Alternative Options',
                'slug': 'borewell-failure-recovery-deepening-flushing-alternatives',
                'content': '''When your borewell stops yielding water, don't panic - there are several recovery options before considering a new borewell. This article explains borewell deepening methods, when deepening is viable, high-pressure jet flushing techniques, chemical treatment to open water-bearing fractures, and rehabilitation of old borewells. We also discuss when recovery attempts aren't cost-effective and alternatives like rainwater harvesting recharge systems to replenish your existing borewell.''',
                'category': 'drilling'
            },
        ]

        # Create blogs
        created_count = 0
        for blog_data in blogs_data:
            blog, created = Blog.objects.get_or_create(
                slug=blog_data['slug'],
                defaults={
                    'title': blog_data['title'],
                    'content': blog_data['content'],
                    'category': blog_data['category'],
                    'author': admin_user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {blog.title}')
            else:
                self.stdout.write(f'  Exists: {blog.title}')

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully loaded {created_count} blog articles!'))
        self.stdout.write(f'Total blogs in database: {Blog.objects.count()}')
