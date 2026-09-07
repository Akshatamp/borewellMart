#!/usr/bin/env python
"""
Add services to all vendors based on their specialization
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Vendor, VendorService, SubService

# Get all existing subservices grouped by category
all_subservices = list(SubService.objects.all())

# Define service groups for different vendor types
service_groups = {
    'drilling': [
        'domestic_borewell_drilling', 'agricultural_borewell_drilling',
        'industrial_borewell_drilling', 'deep_borewell_drilling',
        'rotary_drilling', 'dth_drilling', 'farm_borewell_drilling'
    ],
    'survey': [
        'hydrogeological_surveys', 'geophysical_surveys',
        'groundwater_potential_assessment', 'drilling_site_identification'
    ],
    'casing': [
        'pvc_casing_installation', 'ms_casing_installation',
        'casing_repair_replacement'
    ],
    'cleaning': [
        'air_compressor_flushing', 'bore_cleaning', 'drilling_debris_removal',
        'borewell_cleaning_rehabilitation', 'fallen_object_removal'
    ],
    'pumps': [
        'submersible_pump_installation', 'open_well_pump_installation',
        'solar_pump_installation', 'pump_repair_servicing',
        'motor_rewinding_maintenance'
    ],
    'testing': [
        'pumping_tests', 'chemical_analysis', 'bacteriological_testing',
        'potability_testing', 'water_yield_testing', 'discharge_measurement'
    ],
    'irrigation': [
        'drip_irrigation_installation', 'sprinkler_irrigation_systems',
        'micro_irrigation_solutions', 'farm_water_distribution',
        'farm_pipeline_networks', 'farm_water_distribution_systems'
    ],
    'solar': [
        'solar_water_pumps', 'solar_irrigation_systems',
        'solar_pump_maintenance', 'energy_efficient_water_management',
        'solar_powered_borewell_pumps'
    ],
    'recharge': [
        'borewell_recharge_systems', 'recharge_pit_construction',
        'rooftop_rainwater_harvesting_connection'
    ],
    'pipeline': [
        'hdpe_pipeline_installation', 'drip_irrigation_integration',
        'sprinkler_system_installation'
    ],
    'automation': [
        'iot_irrigation_automation', 'remote_pump_monitoring',
        'water_level_sensors', 'iot_irrigation_controls',
        'remote_pump_monitoring_automation'
    ]
}

# Map each vendor company name to relevant service groups
vendor_service_map = {
    'Hubli Aqua Borewell Services': ['drilling', 'pumps', 'survey'],
    'North Karnataka Drilling Works': ['drilling', 'survey'],
    'Bangalore Precision Borewells': ['survey', 'drilling', 'testing'],
    'Belagavi Borewell Masters': ['drilling', 'pumps', 'recharge'],
    'Coastal Water Solutions': ['testing', 'cleaning'],
    'Mysuru Agri Aqua Services': ['drilling', 'irrigation', 'solar'],
    'Vijayapura Solar & Irrigation Co': ['solar', 'irrigation', 'pipeline'],
    'Raichur Cotton Belt Irrigation': ['irrigation', 'automation'],
    'Kalaburagi Deep Drilling Experts': ['drilling', 'survey'],
    'Bidar Groundwater & Survey': ['survey', 'testing'],
    'Ballari Industrial Water Solutions': ['drilling', 'testing'],
    'Shivamogga Areca Plantation Services': ['irrigation', 'pipeline'],
    'Dharwad Pump & Motors': ['pumps', 'cleaning'],
    'Bangalore Smart Irrigation': ['automation', 'irrigation'],
    'Mangalore Quality Water Labs': ['testing'],
    'Vijayapura Farm Pond Specialists': ['recharge', 'testing'],
    'Raichur Solar Energy Systems': ['solar', 'irrigation'],
    'Kalaburagi Casing & Pipes': ['casing', 'pipeline'],
    'Bidar Open Well Experts': ['pumps', 'cleaning'],
    'Hubli Emergency Borewell Services': ['pumps', 'cleaning', 'testing'],
    'Belagavi Geophysical Survey': ['survey', 'drilling'],
    'Karnataka Seed Corporation': ['irrigation'],
    'Raichur Cotton Seed Dealers': ['irrigation'],
    'Green Earth Fertilizers': ['irrigation'],
    'Crop Care Solutions': ['irrigation'],
    'Drip Irrigation Systems India': ['irrigation', 'pipeline'],
    'Farm Tools & Equipment Hub': ['irrigation'],
    'Dairy & Livestock Supplies': ['irrigation'],
    'Agri Machinery Rental Services': ['drilling', 'irrigation'],
    'Soil Testing & Advisory Center': ['testing', 'irrigation'],
    'Farm Infrastructure Builders': ['recharge', 'pipeline'],
    'Agri Marketplace Hub': ['irrigation', 'solar'],
    'Second Hand Agri Equipment': ['pumps', 'irrigation'],
    'Water Management Systems': ['recharge', 'testing'],
    'Agricultural Pumps & Motors': ['pumps', 'irrigation'],
    'Borewell Pumps & Motors Hub': ['pumps', 'casing'],
    'Pipes & Fittings World': ['casing', 'pipeline'],
    'Electrical Control Systems': ['pumps', 'automation'],
    'Borewell Accessories Hub': ['casing', 'pumps'],
    'Complete Borewell Solutions': ['cleaning', 'testing'],
    'Borewell Repair & Maintenance Experts': ['cleaning', 'casing'],
    'Deep Drilling Specialists': ['drilling', 'cleaning'],
    'Groundwater Recharge Solutions': ['recharge', 'testing'],
    'Submersible Pump Services': ['pumps', 'cleaning'],
    'Borewell Electrical Works': ['pumps', 'automation'],
    'Pipeline & Plumbing Services': ['pipeline', 'casing'],
    'Water Testing Laboratories': ['testing'],
    'Equipment Rental Hub': ['drilling', 'pumps'],
    'Second Hand Borewell Equipment': ['pumps', 'casing'],
    'Emergency Borewell Services 24/7': ['pumps', 'cleaning'],
    'Annual Maintenance Contracts': ['pumps', 'testing'],
    'Solar Water Solutions': ['solar', 'irrigation'],
    'Irrigation Systems': ['irrigation', 'automation']
}

# Get available subservice IDs
available_subservice_ids = set(SubService.objects.values_list('id', flat=True))

# Add services to vendors
updated_count = 0
new_services_count = 0

for vendor in Vendor.objects.all():
    company_name = vendor.company_name
    service_groups_to_add = vendor_service_map.get(company_name, ['drilling', 'pumps'])

    services_added = []
    for group in service_groups_to_add:
        for service_id in service_groups[group]:
            if service_id in available_subservice_ids:
                # Check if vendor already has this service
                if not VendorService.objects.filter(vendor=vendor, subservice_id=service_id).exists():
                    try:
                        subservice = SubService.objects.get(id=service_id)
                        VendorService.objects.create(
                            vendor=vendor,
                            subservice=subservice,
                            price=5000,
                            description=f'Professional {subservice.name} by {vendor.company_name}'
                        )
                        services_added.append(service_id)
                        new_services_count += 1
                    except SubService.DoesNotExist:
                        pass

    if services_added:
        updated_count += 1
        print(f'Updated {company_name}: Added {len(services_added)} services')

print(f'\nSummary:')
print(f'  Vendors updated: {updated_count}')
print(f'  New vendor services added: {new_services_count}')
