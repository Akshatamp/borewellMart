from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import City, SubService, Vendor, VendorService, UserProfile, Blog


class Command(BaseCommand):
    help = 'Load sample data for BorewellMart'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample data...')

        # Create Cities
        cities_data = [
            {'name': 'Hubli', 'description': 'Commercial hub of North Karnataka', 'latitude': 15.3647, 'longitude': 75.1239},
            {'name': 'Dharwad', 'description': 'Twin city of Hubli, educational center', 'latitude': 15.4609, 'longitude': 75.0567},
            {'name': 'Bangalore', 'description': 'Silicon Valley of India', 'latitude': 12.9716, 'longitude': 77.5946},
            {'name': 'Belagavi', 'description': 'Second capital of Karnataka', 'latitude': 15.8485, 'longitude': 74.5129},
            {'name': 'Mangalore', 'description': 'Coastal city of Karnataka', 'latitude': 12.9141, 'longitude': 74.8560},
            {'name': 'Mysuru', 'description': 'Cultural capital of Karnataka', 'latitude': 12.2958, 'longitude': 76.6394},
            {'name': 'Vijayapura', 'description': 'Agricultural hub of North Karnataka', 'latitude': 16.8304, 'longitude': 75.7140},
            {'name': 'Raichur', 'description': 'Cotton and rice growing region', 'latitude': 16.2076, 'longitude': 77.3463},
            {'name': 'Kalaburagi', 'description': 'Red cotton belt of Karnataka', 'latitude': 17.3280, 'longitude': 76.8336},
            {'name': 'Bidar', 'description': 'Agricultural district with rich groundwater', 'latitude': 17.9072, 'longitude': 77.5283},
            {'name': 'Ballari', 'description': 'Iron and agricultural district', 'latitude': 15.1393, 'longitude': 76.9123},
            {'name': 'Shivamogga', 'description': 'Areca nut and paddy growing region', 'latitude': 13.9299, 'longitude': 75.5681},
        ]

        cities = []
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                defaults={
                    'description': city_data['description'],
                    'latitude': city_data.get('latitude'),
                    'longitude': city_data.get('longitude')
                }
            )
            cities.append(city)
            if created:
                self.stdout.write(f'Created city: {city.name}')
            else:
                self.stdout.write(f'City already exists: {city.name}')

        # Create Services
        services_data = [
            {'name': 'Borewell Drilling', 'description': 'Professional borewell drilling services for residential and commercial needs', 'category': 'borewell'},
            {'name': 'Borewell Cleaning', 'description': 'Complete borewell cleaning and maintenance services', 'category': 'borewell'},
            {'name': 'Borewell Repair & Maintenance', 'description': 'Expert repair and maintenance for all types of borewells', 'category': 'borewell'},
            {'name': 'Submersible Pump Installation', 'description': 'Installation of submersible pumps for efficient water extraction', 'category': 'borewell'},
            {'name': 'Pump Repair & Replacement', 'description': 'Repair and replacement services for all pump types', 'category': 'borewell'},
            {'name': 'Borewell Deepening & Recharging', 'description': 'Borewell deepening and rainwater recharging services', 'category': 'borewell'},
            {'name': 'Drip Irrigation Installation', 'description': 'Complete drip irrigation system setup for farms and gardens', 'category': 'agriculture'},
            {'name': 'Sprinkler System Installation', 'description': 'Modern sprinkler irrigation systems for agricultural lands', 'category': 'agriculture'},
            {'name': 'Farm Pond Construction', 'description': 'Excavation and construction of farm ponds for water storage', 'category': 'agriculture'},
            {'name': 'Open Well Construction', 'description': 'Traditional open well digging and construction services', 'category': 'agriculture'},
            {'name': 'Solar Pump Installation', 'description': 'Solar-powered water pump systems for sustainable irrigation', 'category': 'agriculture'},
            {'name': 'Micro-Irrigation System Setup', 'description': 'Efficient micro-irrigation systems for water conservation', 'category': 'agriculture'},
            {'name': 'Agricultural Pipeline Installation', 'description': 'Main and sub-pipeline installation for farm irrigation', 'category': 'agriculture'},
            {'name': 'Groundwater Survey Services', 'description': 'Scientific groundwater detection and survey services', 'category': 'agriculture'},
        ]

        services = []
        for service_data in services_data:
            service, created = SubService.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'category': service_data.get('category', 'borewell')
                }
            )
            # Update existing service with category if it's missing
            if not created and not service.category:
                service.description = service_data['description']
                service.category = service_data.get('category', 'borewell')
                service.save()
                self.stdout.write(f'Updated service category: {service.name} -> {service.category}')
            services.append(service)
            if created:
                self.stdout.write(f'Created service: {service.name} ({service.category})')
            else:
                self.stdout.write(f'Service already exists: {service.name}')

        # Create Sample Customer
        customer_user, created = User.objects.get_or_create(
            username='customer',
            defaults={'email': 'customer@borewellmart.com'}
        )
        if created:
            customer_user.set_password('password123')
            customer_user.save()
            UserProfile.objects.create(
                user=customer_user,
                phone='9876543200',
                user_type='customer',
                city=cities[0]  # Hubli
            )
            self.stdout.write('Created sample customer account')
        else:
            self.stdout.write('Customer account already exists')

        # Create Vendors
        vendor_data = [
            {'company': 'Shree Borewell Services', 'city': 'Hubli', 'exp': 15, 'phone': '9876543210', 'email': 'shree@borewell.com'},
            {'company': 'Karnataka Borewell Works', 'city': 'Dharwad', 'exp': 12, 'phone': '9876543211', 'email': 'karnataka@borewell.com'},
            {'company': 'Bangalore Water Solutions', 'city': 'Bangalore', 'exp': 20, 'phone': '9876543212', 'email': 'bangalore@borewell.com'},
            {'company': 'Belagavi Borewell Experts', 'city': 'Belagavi', 'exp': 10, 'phone': '9876543213', 'email': 'belagavi@borewell.com'},
            {'company': 'Coastal Water Services', 'city': 'Mangalore', 'exp': 18, 'phone': '9876543214', 'email': 'coastal@borewell.com'},
            {'company': 'Mysuru Borewell Masters', 'city': 'Mysuru', 'exp': 14, 'phone': '9876543215', 'email': 'mysuru@borewell.com'},
            {'company': 'North Karnataka Drilling', 'city': 'Hubli', 'exp': 8, 'phone': '9876543216', 'email': 'north@borewell.com'},
            {'company': 'Dharwad Water Tech', 'city': 'Dharwad', 'exp': 11, 'phone': '9876543217', 'email': 'dharwad@borewell.com'},
            {'company': 'IT City Borewell', 'city': 'Bangalore', 'exp': 25, 'phone': '9876543218', 'email': 'itcity@borewell.com'},
            {'company': 'Belagavi Aqua Services', 'city': 'Belagavi', 'exp': 9, 'phone': '9876543219', 'email': 'aqua@borewell.com'},
            {'company': 'Mangalore Deep Wells', 'city': 'Mangalore', 'exp': 16, 'phone': '9876543220', 'email': 'deep@borewell.com'},
            {'company': 'Royal Borewell Services', 'city': 'Mysuru', 'exp': 13, 'phone': '9876543221', 'email': 'royal@borewell.com'},
            {'company': 'Hubli Aqua Tech', 'city': 'Hubli', 'exp': 7, 'phone': '9876543222', 'email': 'hubli@borewell.com'},
            {'company': 'Dharwad Prime Services', 'city': 'Dharwad', 'exp': 17, 'phone': '9876543223', 'email': 'prime@borewell.com'},
            {'company': 'Bangalore Elite Borewell', 'city': 'Bangalore', 'exp': 22, 'phone': '9876543224', 'email': 'elite@borewell.com'},
            # Agriculture-focused vendors in agricultural regions
            {'company': 'Vijayapura Agri Wells', 'city': 'Vijayapura', 'exp': 18, 'phone': '9876543225', 'email': 'vijayapura@agriwell.com'},
            {'company': 'Raichur Farm Irrigation', 'city': 'Raichur', 'exp': 20, 'phone': '9876543226', 'email': 'raichur@farmirrigation.com'},
            {'company': 'Kalaburagi Cotton Belt Drilling', 'city': 'Kalaburagi', 'exp': 15, 'phone': '9876543227', 'email': 'kalaburagi@cottondrilling.com'},
            {'company': 'Bidar Groundwater Experts', 'city': 'Bidar', 'exp': 12, 'phone': '9876543228', 'email': 'bidar@groundwater.com'},
            {'company': 'Ballari Farm Water Solutions', 'city': 'Ballari', 'exp': 16, 'phone': '9876543229', 'email': 'ballari@farmwater.com'},
            {'company': 'Shivamogga Areca Irrigation', 'city': 'Shivamogga', 'exp': 14, 'phone': '9876543230', 'email': 'shivamogga@arecairrigation.com'},
            {'company': 'Vijayapura Solar Pumps', 'city': 'Vijayapura', 'exp': 10, 'phone': '9876543231', 'email': 'vijayapura@solarpump.com'},
            {'company': 'Raichur Drip Systems', 'city': 'Raichur', 'exp': 11, 'phone': '9876543232', 'email': 'raichur@dripsystems.com'},
            {'company': 'Kalaburagi Farm Ponds', 'city': 'Kalaburagi', 'exp': 13, 'phone': '9876543233', 'email': 'kalaburagi@farmponds.com'},
            {'company': 'Bidar Open Well Specialists', 'city': 'Bidar', 'exp': 19, 'phone': '9876543234', 'email': 'bidar@openwell.com'},
        ]

        vendors = []
        for i, v_data in enumerate(vendor_data):
            # Create user for vendor
            username = f'vendor{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': v_data['email']}
            )
            if created:
                user.set_password('password123')
                user.save()
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    phone=v_data['phone'],
                    user_type='vendor',
                    city=City.objects.get(name=v_data['city'])
                )

            # Get or create vendor
            city = City.objects.get(name=v_data['city'])
            vendor, created = Vendor.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': v_data['company'],
                    'city': city,
                    'experience': v_data['exp'],
                    'phone': v_data['phone'],
                    'email': v_data['email'],
                    'address': f'{v_data["city"]}, Karnataka',
                    'verification_status': 'verified',
                    'rating': 4.0 + (i % 2) * 0.5  # Alternate between 4.0 and 4.5
                }
            )
            if created:
                self.stdout.write(f'Created vendor: {vendor.company_name}')
            else:
                self.stdout.write(f'Vendor already exists: {vendor.company_name}')
            vendors.append(vendor)

        # Assign services to vendors based on specialization
        # First 15 vendors get borewell services, next 10 get agriculture services
        borewell_services = list(Service.objects.filter(category='borewell'))
        agri_services = list(Service.objects.filter(category='agriculture'))

        # If no services have categories yet, fall back to index-based assignment
        if not borewell_services or not agri_services:
            self.stdout.write('Warning: Services not properly categorized. Using fallback assignment.')
            for i, vendor in enumerate(vendors):
                service1 = services[i % len(services)]
                service2 = services[(i + 1) % len(services)]

                VendorSubService.objects.get_or_create(
                    vendor=vendor,
                    subservice=service1,
                    defaults={'price': 5000 + (i * 1000), 'description': f'Professional {service1.name} service'}
                )

                VendorSubService.objects.get_or_create(
                    vendor=vendor,
                    subservice=service2,
                    defaults={'price': 6000 + (i * 1000), 'description': f'Professional {service2.name} service'}
                )
                self.stdout.write(f'Assigned services to {vendor.company_name}: {service1.name}, {service2.name}')
        else:
            for i, vendor in enumerate(vendors):
                if i < 15:  # First 15 - borewell specialists
                    service1 = borewell_services[i % len(borewell_services)]
                    service2 = borewell_services[(i + 1) % len(borewell_services)]
                else:  # Last 10 - agriculture specialists
                    agri_index = i - 15
                    service1 = agri_services[agri_index % len(agri_services)]
                    service2 = agri_services[(agri_index + 1) % len(agri_services)]

                VendorSubService.objects.get_or_create(
                    vendor=vendor,
                    subservice=service1,
                    defaults={'price': 5000 + (i * 1000), 'description': f'Professional {service1.name} service'}
                )

                VendorSubService.objects.get_or_create(
                    vendor=vendor,
                    subservice=service2,
                    defaults={'price': 6000 + (i * 1000), 'description': f'Professional {service2.name} service'}
                )

                self.stdout.write(f'Assigned services to {vendor.company_name}: {service1.name}, {service2.name}')

        # Create Sample Blog Articles
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

        # Create admin user for blog author
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@borewellmart.com', 'is_superuser': True, 'is_staff': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.create(
                user=admin_user,
                phone='9876543999',
                user_type='admin',
                city=cities[0]  # Hubli
            )
            self.stdout.write('Created admin account for blog author')
        elif admin_user.password == '' or not admin_user.is_staff:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write('Updated admin account')

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
                self.stdout.write(f'Created blog: {blog.title}')
            else:
                self.stdout.write(f'Blog already exists: {blog.title}')

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
        self.stdout.write('\n' + '='*50)
        self.stdout.write('SAMPLE ACCOUNTS:')
        self.stdout.write('='*50)
        self.stdout.write('Admin Account:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write('\nCustomer Account:')
        self.stdout.write('  Username: customer')
        self.stdout.write('  Password: password123')
        self.stdout.write('\nVendor Accounts (vendor1 to vendor25):')
        self.stdout.write('  Username: vendor1, vendor2, ..., vendor25')
        self.stdout.write('  Password: password123')
        self.stdout.write('='*50)
