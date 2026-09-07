#!/usr/bin/env python
"""
Fix vendor service IDs to match the actual subservice IDs in the database
"""

import json

# Load the services data to get the correct subservice IDs
with open('core/management/commands/services_data.json', 'r', encoding='utf-8') as f:
    services_data = json.load(f)

# Create a mapping from simplified IDs to actual database IDs
subservice_mapping = {}

for category in services_data.get('service_categories', []):
    for subcategory in category.get('subcategories', []):
        for service in subcategory.get('services', []):
            actual_id = service.get('id')
            name = service.get('name', '').lower()

            # Create the simplified ID (what we used in vendor data)
            simplified_id = name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('/', '_').replace('&', 'and').replace(',', '').replace(':', '').replace('__', '_').strip('_')

            subservice_mapping[simplified_id] = actual_id

# Additional manual mappings for special cases
manual_mappings = {
    'residential_borewell_drilling': 'domestic_borewell_drilling',
    'commercial_borewell_drilling': 'agricultural_borewell_drilling',
    'groundwater_assessment': 'groundwater_assessment',
    'drinking_water_testing': 'bacteriological_testing',
    'water_yield_improvement': 'yield_enhancement',
    'borewell_site_survey': 'drilling_site_identification',
    'water_quality_analysis': 'potability_testing',
    'agricultural_water_testing': 'soil_water_analysis',
    'dealer_casing_pipes': 'pvc_casing_installation',
    'borewell_casing_repair': 'casing_repair_replacement',
    'air_compressor_cleaning': 'air_compressor_flushing',
    'bore_flushing': 'bore_cleaning',
    'sand_removal': 'drilling_debris_removal',
    'borewell_restoration': 'borewell_cleaning_rehabilitation',
    'borewell_blockage_removal': 'fallen_object_removal',
    'submersible_pump_repair': 'pump_repair_servicing',
    'motor_rewinding': 'motor_rewinding_maintenance',
    'dealer_openwell_pumps': 'open_well_pump_installation',
    'hydrogeological_survey': 'hydrogeological_surveys',
    'laboratory_testing': 'chemical_analysis',
    'borewell_leakage_repair': 'casing_repair_replacement',
    'water_flow_restoration': 'yield_enhancement',
    'periodic_maintenance': 'pump_repair_servicing',
    'borewell_health_inspection': 'water_yield_testing',
    'borewell_deepening': 'deep_borewell_drilling',
    're_boring': 're_boring_services',
    'casing_pipe_extension': 'casing_repair_replacement',
    'yield_improvement_deepening': 'yield_enhancement',
    'borewell_rehabilitation': 'borewell_cleaning_rehabilitation',
    'recharge_shaft_installation': 'recharge_pit_construction',
    'rainwater_recharge_system': 'borewell_recharge_systems',
    'recharge_bore_construction': 'recharge_pit_construction',
    'groundwater_recharge_solutions': 'groundwater_recharge_consultancy',
    'recharge_filter_installation': 'recharge_pit_construction',
    'submersible_pump_replacement': 'pump_repair_servicing',
    'pump_pulling_reinstallation': 'pump_repair_servicing',
    'motor_installation': 'submersible_pump_installation',
    'motor_repair': 'motor_rewinding_maintenance',
    'motor_rewinding_borewell': 'motor_rewinding_maintenance',
    'pump_capacity_upgrade': 'submersible_pump_installation',
    'starter_panel_installation': 'pump_repair_servicing',
    'control_panel_installation_borewell': 'pump_repair_servicing',
    'borewell_wiring': 'pump_repair_servicing',
    'cable_replacement': 'pump_repair_servicing',
    'earthing': 'pump_repair_servicing',
    'electrical_fault_diagnosis': 'pump_repair_servicing',
    'generator_connection': 'pump_repair_servicing',
    'automatic_pump_controller_installation': 'remote_pump_monitoring_automation',
    'hdpe_pipe_installation': 'hdpe_pipeline_installation',
    'pvc_pipe_installation': 'pvc_casing_installation',
    'gi_pipe_installation': 'ms_casing_installation',
    'underground_pipeline': 'farm_pipeline_networks',
    'water_distribution_pipeline': 'farm_water_distribution_systems',
    'valve_installation': 'pump_repair_servicing',
    'pipe_leakage_repair': 'casing_repair_replacement',
    'pipeline_replacement': 'hdpe_pipeline_installation',
    'tds_testing': 'potability_testing',
    'ph_testing': 'potability_testing',
    'water_purity_consultation': 'potability_testing',
    'drilling_rig_rental': 'submersible_pump_installation',
    'air_compressor_rental': 'air_compressor_flushing',
    'borewell_camera_rental': 'water_level_sensors',
    'generator_rental': 'solar_pump_installation',
    'pipe_lifting_equipment_rental': 'submersible_pump_installation',
    'crane_rental': 'submersible_pump_installation',
    'dewatering_pump_rental': 'submersible_pump_installation',
    'emergency_pump_breakdown': 'pump_repair_servicing',
    'no_water_in_borewell': 'borewell_cleaning_rehabilitation',
    'pump_stuck_in_borewell': 'borewell_cleaning_rehabilitation',
    'cable_breakage': 'pump_repair_servicing',
    'borewell_collapse_assistance': 'collapsed_borewell_rehabilitation',
    'emergency_technician_visit': 'pump_repair_servicing',
    '24_7_support': 'pump_repair_servicing',
    'annual_borewell_maintenance': 'water_yield_testing',
    'pump_inspection_amc': 'pump_repair_servicing',
    'motor_inspection_amc': 'motor_rewinding_maintenance',
    'electrical_inspection': 'pump_repair_servicing',
    'pipeline_inspection': 'hdpe_pipeline_installation',
    'preventive_maintenance': 'pump_repair_servicing',
    'scheduled_servicing': 'pump_repair_servicing',
}

# Merge the mappings
subservice_mapping.update(manual_mappings)

# Load the vendor data
with open('core/management/commands/updated_vendors_data.json', 'r', encoding='utf-8') as f:
    vendors_data = json.load(f)

# Update vendor service IDs
for vendor in vendors_data['vendors']:
    updated_services = []
    for service_id in vendor.get('services', []):
        # Map the simplified ID to the actual database ID
        actual_id = subservice_mapping.get(service_id)
        if actual_id:
            updated_services.append(actual_id)
        else:
            # Try to find a close match
            for key, value in subservice_mapping.items():
                if service_id in key or key in service_id:
                    updated_services.append(value)
                    break
            else:
                print(f"Warning: Could not map service ID: {service_id}")

    vendor['services'] = updated_services

# Save the updated vendor data
with open('core/management/commands/services_data.json', 'w', encoding='utf-8') as f:
    # Load the original services data
    with open('core/management/commands/services_data.json', 'r', encoding='utf-8') as original:
        services_original = json.load(original)

    # Update the vendors section
    services_original['vendors'] = vendors_data['vendors']

    # Write back
    json.dump(services_original, f, indent=2, ensure_ascii=False)

print("Vendor service IDs have been updated to match database IDs!")
print(f"Updated {len(vendors_data['vendors'])} vendors")
