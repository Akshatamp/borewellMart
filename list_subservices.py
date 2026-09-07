#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import SubService

subservices = SubService.objects.values_list('id', 'name')
print('All subservices:')
for sid, name in subservices:
    print(f'  {sid}: {name}')
