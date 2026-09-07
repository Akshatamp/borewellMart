#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City

print('Total cities:', City.objects.count())
print('\nCities:')
for city in City.objects.all()[:20]:
    state = city.state if city.state else 'No state'
    print(f'  {city.name} - {state}')
