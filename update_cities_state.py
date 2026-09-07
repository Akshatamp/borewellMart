#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City

# Update all cities to have Karnataka as the state
updated_count = City.objects.filter(state='').update(state='Karnataka')
print(f"Updated {updated_count} cities with state 'Karnataka'")

# Verify the update
print("\nUpdated cities:")
for city in City.objects.all():
    print(f"  {city.name} - {city.state}")
