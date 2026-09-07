import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import SubService

# Sample features to choose from
FEATURES_POOL = [
    'Professional service',
    'Expert team',
    'Quality work',
    'Timely completion',
    'Affordable pricing',
    'Modern equipment',
    'Experienced staff',
    'Reliable service',
    'Customer satisfaction',
    'Quick response',
    'Safety measures',
    'Certified professionals',
    'Warranty included',
    '24/7 support',
    'Eco-friendly',
    'Cost effective',
    'High quality',
    'Best practices',
    'Custom solutions',
    'Trusted provider'
]

# Update all subservices
subservices = SubService.objects.all()
count = 0

for subservice in subservices:
    per_feet = random.randint(100, 300)
    num_features = random.randint(2, 4)
    features = random.sample(FEATURES_POOL, num_features)
    
    subservice.per_feet_amount = per_feet
    subservice.features = features
    subservice.save()
    count += 1
    print(f"Updated: {subservice.name} - ₹{per_feet}/ft - {features}")

print(f"\nTotal updated: {count} subservices")
