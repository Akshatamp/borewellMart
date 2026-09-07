#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import SubService

print('Total subservices:', SubService.objects.count())
print('\nFirst 10 subservices:')
for s in SubService.objects.all()[:10]:
    print(f'  ID: {s.id}, Name: {s.name}')
