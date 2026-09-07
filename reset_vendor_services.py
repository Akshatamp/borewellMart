#!/usr/bin/env python
"""
Reset vendor services to match original vendor data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import Vendor, VendorService, SubService

# Clear all existing vendor services
print("Clearing all existing vendor services...")
VendorService.objects.all().delete()
print("Cleared!")

# Original vendor service mappings from the old data
# Map old service names to current database IDs
service_mappings = {
    'drip_irrigation_installation': 'drip_irrigation_installation',
    'sprinkler_irrigation_systems': 'sprinkler_irrigation_systems',
    'micro_irrigation_solutions': 'micro_irrigation_solutions',
    'farm_water_distribution': 'farm_water_distribution',
    'solar_water_pumps': 'solar_water_pumps',
    'solar_irrigation_systems': 'solar_irrigation_systems',
    'solar_pump_maintenance': 'solar_pump_maintenance',
    'energy_efficient_water_management': 'energy_efficient_water_management',
    'water_storage_tank_installation': 'water_storage_tank_installation',
    'farm_pipeline_networks': 'farm_pipeline_networks',
    'farm_borewell_drilling': 'farm_borewell_drilling',
    'deep_agricultural_borewells': 'deep_agricultural_borewells',
    'high_yield_borewell_development': 'high_yield_borewell_development',
    'borewell_recharge_systems': 'borewell_recharge_systems',
    'domestic_borewell_drilling': 'domestic_borewell_drilling',
    'agricultural_borewell_drilling': 'agricultural_borewell_drilling',
    'industrial_borewell_drilling': 'industrial_borewell_drilling',
    'deep_borewell_drilling': 'deep_borewell_drilling',
    'submersible_pump_installation': 'submersible_pump_installation',
    'pump_repair_servicing': 'pump_repair_servicing',
    'motor_rewinding_maintenance': 'motor_rewinding_maintenance',
    'open_well_pump_installation': 'open_well_pump_installation',
    'hydrogeological_surveys': 'hydrogeological_surveys',
    'geophysical_surveys': 'geophysical_surveys',
    'groundwater_assessment': 'groundwater_assessment',
    'pumping_tests': 'pumping_tests',
    'chemical_analysis': 'chemical_analysis',
    'bacteriological_testing': 'bacteriological_testing',
    'potability_testing': 'potability_testing',
    'soil_water_analysis': 'soil_water_analysis',
    'pvc_casing_installation': 'pvc_casing_installation',
    'ms_casing_installation': 'ms_casing_installation',
    'casing_repair_replacement': 'casing_repair_replacement',
    'air_compressor_flushing': 'air_compressor_flushing',
    'bore_cleaning': 'bore_cleaning',
    'drilling_debris_removal': 'drilling_debris_removal',
    'yield_enhancement': 'yield_enhancement',
    'iot_irrigation_automation': 'iot_irrigation_automation',
    'remote_pump_monitoring': 'remote_pump_monitoring',
    'water_level_sensors_monitoring': 'water_level_sensors_monitoring',
    'mobile_farm_water_control': 'mobile_farm_water_control',
    'water_flow_monitoring': 'water_flow_monitoring',
    'smart_irrigation_controls': 'smart_irrigation_controls',
    'groundwater_potential_assessment': 'groundwater_potential_assessment',
    'drilling_site_identification': 'drilling_site_identification',
    'rotary_drilling': 'rotary_drilling',
    'dth_drilling': 'dth_drilling',
    'borewell_recharge_systems_rwh': 'borewell_recharge_systems_rwh',
    'recharge_pit_construction': 'recharge_pit_construction',
    'borewell_cleaning_rehabilitation': 'borewell_cleaning_rehabilitation',
    'fallen_object_removal': 'fallen_object_removal',
    'hydro_fracturing': 'hydro_fracturing',
    'groundwater_yield_testing': 'water_yield_testing'
}

# Original vendor data with their services
original_vendors = [
    {
        "company_name": "Hubli Aqua Borewell Services",
        "services": ["domestic_borewell_drilling", "agricultural_borewell_drilling", "submersible_pump_installation", "hydrogeological_surveys"]
    },
    {
        "company_name": "North Karnataka Drilling Works",
        "services": ["domestic_borewell_drilling", "agricultural_borewell_drilling", "industrial_borewell_drilling", "deep_borewell_drilling"]
    },
    {
        "company_name": "Bangalore Precision Borewells",
        "services": ["hydrogeological_surveys", "geophysical_surveys", "domestic_borewell_drilling", "yield_enhancement"]
    },
    {
        "company_name": "Belagavi Borewell Masters",
        "services": ["domestic_borewell_drilling", "open_well_pump_installation", "recharge_pit_construction", "yield_enhancement"]
    },
    {
        "company_name": "Coastal Water Solutions",
        "services": ["groundwater_assessment", "bacteriological_testing", "borewell_cleaning_rehabilitation", "yield_enhancement"]
    },
    {
        "company_name": "Mysuru Agri Aqua Services",
        "services": ["farm_borewell_drilling", "drip_irrigation_installation", "sprinkler_irrigation_systems", "solar_water_pumps"]
    },
    {
        "company_name": "Vijayapura Solar & Irrigation Co",
        "services": ["solar_water_pumps", "solar_irrigation_systems", "drip_irrigation_installation", "farm_pipeline_networks"]
    },
    {
        "company_name": "Raichur Cotton Belt Irrigation",
        "services": ["sprinkler_irrigation_systems", "micro_irrigation_solutions", "farm_water_distribution_systems", "iot_irrigation_automation"]
    },
    {
        "company_name": "Kalaburagi Deep Drilling Experts",
        "services": ["deep_agricultural_borewells", "farm_borewell_drilling", "high_yield_borewell_development", "domestic_borewell_drilling"]
    },
    {
        "company_name": "Bidar Groundwater & Survey",
        "services": ["groundwater_assessment", "yield_enhancement", "drilling_site_identification", "hydrogeological_surveys"]
    },
    {
        "company_name": "Ballari Industrial Water Solutions",
        "services": ["industrial_borewell_drilling", "water_storage_tank_installation", "farm_water_distribution_systems", "energy_efficient_water_management"]
    },
    {
        "company_name": "Shivamogga Areca Plantation Services",
        "services": ["drip_irrigation_installation", "sprinkler_irrigation_systems", "farm_pipeline_networks", "iot_irrigation_automation"]
    },
    {
        "company_name": "Dharwad Pump & Motors",
        "services": ["submersible_pump_installation", "pump_repair_servicing", "motor_rewinding_maintenance", "open_well_pump_installation"]
    },
    {
        "company_name": "Bangalore Smart Irrigation",
        "services": ["iot_irrigation_automation", "water_yield_testing", "yield_enhancement"]
    },
    {
        "company_name": "Mangalore Quality Water Labs",
        "services": ["bacteriological_testing", "potability_testing", "soil_water_analysis"]
    },
    {
        "company_name": "Vijayapura Farm Pond Specialists",
        "services": ["water_storage_tank_installation", "farm_water_distribution_systems", "borewell_recharge_systems", "recharge_pit_construction"]
    },
    {
        "company_name": "Raichur Solar Energy Systems",
        "services": ["solar_water_pumps", "solar_irrigation_systems", "solar_pump_maintenance", "energy_efficient_water_management"]
    },
    {
        "company_name": "Kalaburagi Casing & Pipes",
        "services": ["pvc_casing_installation", "ms_casing_installation", "casing_repair_replacement", "hdpe_pipeline_installation"]
    },
    {
        "company_name": "Bidar Open Well Experts",
        "services": ["open_well_pump_installation", "borewell_cleaning_rehabilitation", "fallen_object_removal", "yield_enhancement"]
    },
    {
        "company_name": "Hubli Emergency Borewell Services",
        "services": ["pump_repair_servicing", "motor_rewinding_maintenance", "casing_repair_replacement", "borewell_cleaning_rehabilitation"]
    },
    {
        "company_name": "Belagavi Geophysical Survey",
        "services": ["hydrogeological_surveys", "drilling_site_identification"]
    }
]

# Get available subservice IDs
available_subservice_ids = set(SubService.objects.values_list('id', flat=True))

# Assign services to vendors based on original data
services_added = 0
vendors_updated = 0

for vendor_data in original_vendors:
    try:
        vendor = Vendor.objects.get(company_name=vendor_data['company_name'])

        for service_name in vendor_data['services']:
            # Map to database ID
            db_service_id = service_mappings.get(service_name)

            if db_service_id and db_service_id in available_subservice_ids:
                try:
                    subservice = SubService.objects.get(id=db_service_id)
                    VendorService.objects.create(
                        vendor=vendor,
                        subservice=subservice,
                        price=5000,
                        description=f'Professional {subservice.name} by {vendor.company_name}'
                    )
                    services_added += 1
                except SubService.DoesNotExist:
                    print(f"SubService not found: {db_service_id}")
            else:
                print(f"Service ID not available: {service_name} -> {db_service_id}")

        vendors_updated += 1
        print(f"Updated: {vendor.company_name}")

    except Vendor.DoesNotExist:
        print(f"Vendor not found: {vendor_data['company_name']}")

print(f"\nSummary:")
print(f"  Vendors updated: {vendors_updated}")
print(f"  Services added: {services_added}")
