#!/usr/bin/env python
"""
Vendor Mapping Script for BorewellMart
Maps existing and new vendors to the updated service structure
"""

import json

# Load the updated services data
with open('core/management/commands/updated_services_data.json', 'r', encoding='utf-8') as f:
    services_data = json.load(f)

# Create a comprehensive vendor list
vendors = []

# ============================================
# EXISTING VENDORS - Mapped to new structure
# ============================================

# Map old service IDs to new subservice IDs
service_mapping = {
    # Agriculture Services
    'drip_irrigation_installation': 'drip_irrigation',
    'sprinkler_irrigation_systems': 'sprinkler_irrigation',
    'micro_irrigation_solutions': 'micro_irrigation',
    'farm_water_distribution': 'farm_pipeline_installation',
    'solar_water_pumps': 'solar_pumps',
    'solar_irrigation_systems': 'solar_irrigation_systems',
    'solar_pump_maintenance': 'solar_pump_maintenance',
    'energy_efficient_water_management': 'energy_efficient_water_management',
    'water_storage_tank_installation': 'water_storage_tanks',
    'farm_pipeline_networks': 'water_distribution_systems',
    'farm_borewell_drilling': 'farm_borewell_drilling',
    'deep_agricultural_borewells': 'deep_agricultural_borewells',
    'high_yield_borewell_development': 'high_yield_borewell_development',
    'borewell_recharge_systems': 'borewell_recharge_systems',

    # Borewell Services
    'domestic_borewell_drilling': 'residential_borewell_drilling',
    'agricultural_borewell_drilling': 'agricultural_borewell_drilling',
    'industrial_borewell_drilling': 'industrial_borewell_drilling',
    'deep_borewell_drilling': 'residential_borewell_drilling',
    'submersible_pump_installation': 'submersible_pump_installation',
    'pump_repair_servicing': 'submersible_pump_repair',
    'motor_rewinding_maintenance': 'motor_rewinding',
    'open_well_pump_installation': 'dealer_openwell_pumps',
    'hydrogeological_surveys': 'hydrogeological_survey',
    'geophysical_surveys': 'borewell_site_survey',
    'groundwater_assessment': 'drinking_water_testing',
    'pumping_tests': 'water_yield_improvement',
    'chemical_analysis': 'laboratory_testing',
    'bacteriological_testing': 'drinking_water_testing',
    'potability_testing': 'water_quality_analysis',
    'soil_water_analysis': 'agricultural_water_testing',
    'pvc_casing_installation': 'dealer_casing_pipes',
    'ms_casing_installation': 'dealer_casing_pipes',
    'casing_repair_replacement': 'borewell_casing_repair',
    'air_compressor_flushing': 'air_compressor_cleaning',
    'bore_cleaning': 'bore_flushing',
    'drilling_debris_removal': 'sand_removal',
    'yield_enhancement': 'yield_improvement',
    'iot_irrigation_automation': 'irrigation_automation',
    'remote_pump_monitoring': 'irrigation_automation',
    'water_level_sensors_monitoring': 'irrigation_automation',
    'mobile_farm_water_control': 'irrigation_automation',
    'water_flow_monitoring': 'water_distribution_systems',
    'smart_irrigation_controls': 'irrigation_automation',
    'groundwater_potential_assessment': 'hydrogeological_survey',
    'drilling_site_identification': 'borewell_site_survey',
    'rotary_drilling': 'residential_borewell_drilling',
    'dth_drilling': 'residential_borewell_drilling',
    'borewell_recharge_systems_rwh': 'recharge_pit_construction',
    'recharge_pit_construction': 'recharge_pit_construction',
    'borewell_cleaning_rehabilitation': 'borewell_restoration',
    'fallen_object_removal': 'borewell_blockage_removal',
    'hydro_fracturing': 'yield_improvement',
    'groundwater_yield_testing': 'water_yield_improvement'
}

# ============================================
# EXISTING VENDORS (from old data)
# ============================================

existing_vendors = [
    {
        "company_name": "Hubli Aqua Borewell Services",
        "location": "Hubli",
        "specialization": "Complete borewell solutions for domestic and agricultural needs",
        "services": ["residential_borewell_drilling", "agricultural_borewell_drilling", "submersible_pump_installation", "hydrogeological_survey"],
        "established_year": 2010,
        "phone": "9876543210",
        "email": "hubliaqua@borewell.com",
        "address": "Vidyanagar, Hubli - 580021",
        "experience": 14,
        "license_number": "BWL-KAR-2010-001"
    },
    {
        "company_name": "North Karnataka Drilling Works",
        "location": "Dharwad",
        "specialization": "Deep borewell drilling specialists for hard rock areas",
        "services": ["residential_borewell_drilling", "agricultural_borewell_drilling", "commercial_borewell_drilling", "industrial_borewell_drilling"],
        "established_year": 2008,
        "phone": "9876543211",
        "email": "northkar@drilling.com",
        "address": "KC Extension, Dharwad - 580008",
        "experience": 16,
        "license_number": "BWL-KAR-2008-015"
    },
    {
        "company_name": "Bangalore Precision Borewells",
        "location": "Bangalore",
        "specialization": "Urban borewell solutions with advanced technology",
        "services": ["hydrogeological_survey", "borewell_site_survey", "residential_borewell_drilling", "water_yield_improvement"],
        "established_year": 2012,
        "phone": "9876543212",
        "email": "blrprecision@borewell.com",
        "address": "BTM Layout, Bangalore - 560068",
        "experience": 12,
        "license_number": "BWL-KAR-2012-025"
    },
    {
        "company_name": "Belagavi Borewell Masters",
        "location": "Belagavi",
        "specialization": "Traditional and modern borewell techniques",
        "services": ["residential_borewell_drilling", "dealer_openwell_pumps", "recharge_pit_construction", "water_yield_improvement"],
        "established_year": 2005,
        "phone": "9876543213",
        "email": "belagavimaster@borewell.com",
        "address": "Camp Area, Belagavi - 590001",
        "experience": 19,
        "license_number": "BWL-KAR-2005-008"
    },
    {
        "company_name": "Coastal Water Solutions",
        "location": "Mangalore",
        "specialization": "Coastal region borewell and water solutions",
        "services": ["groundwater_assessment", "drinking_water_testing", "borewell_restoration", "water_yield_improvement"],
        "established_year": 2014,
        "phone": "9876543214",
        "email": "coastalwater@borewell.com",
        "address": "Hampankatta, Mangalore - 575001",
        "experience": 10,
        "license_number": "BWL-KAR-2014-032"
    },
    {
        "company_name": "Mysuru Agri Aqua Services",
        "location": "Mysuru",
        "specialization": "Agricultural water management and irrigation systems",
        "services": ["farm_borewell_drilling", "drip_irrigation", "sprinkler_irrigation", "solar_pumps"],
        "established_year": 2009,
        "phone": "9876543215",
        "email": "mysuruagri@borewell.com",
        "address": "Saraswathipuram, Mysuru - 570009",
        "experience": 15,
        "license_number": "BWL-KAR-2009-012"
    },
    {
        "company_name": "Vijayapura Solar & Irrigation Co",
        "location": "Vijayapura",
        "specialization": "Solar-powered farming and irrigation solutions",
        "services": ["solar_pumps", "solar_irrigation_systems", "drip_irrigation", "farm_pipeline_installation"],
        "established_year": 2016,
        "phone": "9876543225",
        "email": "vijayapurasolar@agri.com",
        "address": "TB Dam Road, Vijayapura - 586101",
        "experience": 8,
        "license_number": "AGR-KAR-2016-045"
    },
    {
        "company_name": "Raichur Cotton Belt Irrigation",
        "location": "Raichur",
        "specialization": "Irrigation solutions for cotton and agricultural farms",
        "services": ["sprinkler_irrigation", "micro_irrigation", "water_distribution_systems", "irrigation_automation"],
        "established_year": 2011,
        "phone": "9876543226",
        "email": "raichurcotton@irrigation.com",
        "address": "Station Road, Raichur - 584101",
        "experience": 13,
        "license_number": "AGR-KAR-2011-028"
    },
    {
        "company_name": "Kalaburagi Deep Drilling Experts",
        "location": "Kalaburagi",
        "specialization": "Deep drilling for arid region agricultural needs",
        "services": ["deep_agricultural_borewells", "farm_borewell_drilling", "high_yield_borewell_development", "residential_borewell_drilling"],
        "established_year": 2007,
        "phone": "9876543227",
        "email": "kalaburagideep@borewell.com",
        "address": "S.B. Temple Road, Kalaburagi - 585101",
        "experience": 17,
        "license_number": "BWL-KAR-2007-019"
    },
    {
        "company_name": "Bidar Groundwater & Survey",
        "location": "Bidar",
        "specialization": "Groundwater survey and assessment services",
        "services": ["groundwater_assessment", "water_yield_improvement", "borewell_site_survey", "hydrogeological_survey"],
        "established_year": 2013,
        "phone": "9876543228",
        "email": "bidarsurvey@groundwater.com",
        "address": "Choubara, Bidar - 584401",
        "experience": 11,
        "license_number": "SRV-KAR-2013-051"
    },
    {
        "company_name": "Ballari Industrial Water Solutions",
        "location": "Ballari",
        "specialization": "Industrial and agricultural water management",
        "services": ["industrial_borewell_drilling", "water_storage_tanks", "water_distribution_systems", "energy_efficient_water_management"],
        "established_year": 2010,
        "phone": "9876543229",
        "email": "ballariindustrial@water.com",
        "address": "Gandhi Nagar, Ballari - 583101",
        "experience": 14,
        "license_number": "IND-KAR-2010-037"
    },
    {
        "company_name": "Shivamogga Areca Plantation Services",
        "location": "Shivamogga",
        "specialization": "Water solutions for areca and plantation crops",
        "services": ["drip_irrigation", "sprinkler_irrigation", "farm_pipeline_installation", "irrigation_automation"],
        "established_year": 2012,
        "phone": "9876543230",
        "email": "shivamoggaareca@irrigation.com",
        "address": "Market Road, Shivamogga - 577201",
        "experience": 12,
        "license_number": "AGR-KAR-2012-041"
    },
    {
        "company_name": "Dharwad Pump & Motors",
        "location": "Dharwad",
        "specialization": "Pump installation, repair and motor rewinding",
        "services": ["submersible_pump_installation", "submersible_pump_repair", "motor_rewinding", "dealer_openwell_pumps"],
        "established_year": 2006,
        "phone": "9876543217",
        "email": "dharwadpump@motors.com",
        "address": "KCC Bank Road, Dharwad - 580001",
        "experience": 18,
        "license_number": "PMP-KAR-2006-022"
    },
    {
        "company_name": "Bangalore Smart Irrigation",
        "location": "Bangalore",
        "specialization": "IoT-based precision irrigation and automation",
        "services": ["irrigation_automation", "irrigation_automation", "water_yield_improvement", "irrigation_automation"],
        "established_year": 2018,
        "phone": "9876543218",
        "email": "blrsmart@irrigation.com",
        "address": "Whitefield, Bangalore - 560066",
        "experience": 6,
        "license_number": "IOT-KAR-2018-067"
    },
    {
        "company_name": "Mangalore Quality Water Labs",
        "location": "Mangalore",
        "specialization": "Water quality testing and analysis services",
        "services": ["drinking_water_testing", "drinking_water_testing", "drinking_water_testing", "agricultural_water_testing"],
        "established_year": 2015,
        "phone": "9876543220",
        "email": "mangalorelabs@water.com",
        "address": "PVS Circle, Mangalore - 575003",
        "experience": 9,
        "license_number": "LAB-KAR-2015-058"
    },
    {
        "company_name": "Vijayapura Farm Pond Specialists",
        "location": "Vijayapura",
        "specialization": "Farm pond construction and water storage",
        "services": ["water_storage_tanks", "water_distribution_systems", "borewell_recharge_systems", "recharge_pit_construction"],
        "established_year": 2014,
        "phone": "9876543233",
        "email": "vijayapurafarm@pond.com",
        "address": "Athani Road, Vijayapura - 586102",
        "experience": 10,
        "license_number": "FARM-KAR-2014-048"
    },
    {
        "company_name": "Raichur Solar Energy Systems",
        "location": "Raichur",
        "specialization": "Solar pump and irrigation solutions",
        "services": ["solar_pumps", "solar_irrigation_systems", "solar_pump_maintenance", "energy_efficient_water_management"],
        "established_year": 2017,
        "phone": "9876543232",
        "email": "raichursolar@energy.com",
        "address": "Railway Station Road, Raichur - 584102",
        "experience": 7,
        "license_number": "SLR-KAR-2017-062"
    },
    {
        "company_name": "Kalaburagi Casing & Pipes",
        "location": "Kalaburagi",
        "specialization": "Borewell casing and pipe installation services",
        "services": ["dealer_casing_pipes", "dealer_casing_pipes", "borewell_casing_repair", "hdpe_pipe_installation"],
        "established_year": 2009,
        "phone": "9876543234",
        "email": "kalaburagicasing@pipes.com",
        "address": "Sedam Road, Kalaburagi - 585102",
        "experience": 15,
        "license_number": "CAS-KAR-2009-031"
    },
    {
        "company_name": "Bidar Open Well Experts",
        "location": "Bidar",
        "specialization": "Traditional open well construction and restoration",
        "services": ["dealer_openwell_pumps", "borewell_restoration", "borewell_blockage_removal", "water_yield_improvement"],
        "established_year": 2004,
        "phone": "9876543235",
        "email": "bidaropenwell@traditional.com",
        "address": "Mantri Tank, Bidar - 584402",
        "experience": 20,
        "license_number": "OWL-KAR-2004-005"
    },
    {
        "company_name": "Hubli Emergency Borewell Services",
        "location": "Hubli",
        "specialization": "24/7 emergency borewell repair and maintenance",
        "services": ["submersible_pump_repair", "motor_rewinding", "borewell_casing_repair", "borewell_restoration"],
        "established_year": 2011,
        "phone": "9876543236",
        "email": "hubliemergency@borewell.com",
        "address": "Keshwapur, Hubli - 580022",
        "experience": 13,
        "license_number": "EMR-KAR-2011-029",
        "is_emergency_available": True
    },
    {
        "company_name": "Belagavi Geophysical Survey",
        "location": "Belagavi",
        "specialization": "Scientific groundwater survey and site selection",
        "services": ["hydrogeological_survey", "borewell_site_survey", "hydrogeological_survey", "borewell_site_survey"],
        "established_year": 2013,
        "phone": "9876543237",
        "email": "belagavisurvey@geo.com",
        "address": "Khanapur Road, Belagavi - 590002",
        "experience": 11,
        "license_number": "GEO-KAR-2013-054"
    }
]

# Add existing vendors
vendors.extend(existing_vendors)

# ============================================
# NEW VENDORS for remaining subservices
# ============================================

# Agriculture Services Vendors
agriculture_vendors = [
    {
        "company_name": "Karnataka Seed Corporation",
        "location": "Bangalore",
        "specialization": "Quality seed suppliers for all crops",
        "services": ["hybrid_seeds", "vegetable_seeds", "fruit_seeds", "grain_seeds", "fodder_seeds", "organic_seeds"],
        "established_year": 2010,
        "phone": "9876543401",
        "email": "karnatakaseeds@corp.com",
        "address": "VK Building, Bangalore - 560001",
        "experience": 14,
        "license_number": "SEED-KAR-2010-001"
    },
    {
        "company_name": "Raichur Cotton Seed Dealers",
        "location": "Raichur",
        "specialization": "Cotton and commercial crop seeds",
        "services": ["hybrid_seeds", "grain_seeds", "vegetable_seeds"],
        "established_year": 2012,
        "phone": "9876543402",
        "email": "raichurcotton@seeds.com",
        "address": "APMC Yard, Raichur - 584101",
        "experience": 12,
        "license_number": "COT-KAR-2012-002"
    },
    {
        "company_name": "Green Earth Fertilizers",
        "location": "Dharwad",
        "specialization": "Complete fertilizer solutions",
        "services": ["urea", "dap", "npk_fertilizers", "potash", "micronutrients", "organic_fertilizers", "bio_fertilizers"],
        "established_year": 2008,
        "phone": "9876543403",
        "email": "greenearth@fertilizers.com",
        "address": "Industrial Area, Dharwad - 580008",
        "experience": 16,
        "license_number": "FERT-KAR-2008-003"
    },
    {
        "company_name": "Crop Care Solutions",
        "location": "Belagavi",
        "specialization": "Crop protection and pest management",
        "services": ["insecticides", "fungicides", "herbicides", "weedicides", "plant_growth_regulators", "bio_pesticides"],
        "established_year": 2009,
        "phone": "9876543404",
        "email": "cropcare@protection.com",
        "address": "Market Road, Belagavi - 590001",
        "experience": 15,
        "license_number": "CROP-KAR-2009-004"
    },
    {
        "company_name": "Drip Irrigation Systems India",
        "location": "Hubli",
        "specialization": "Drip and sprinkler irrigation equipment",
        "services": ["drip_irrigation_kits", "sprinkler_systems_kits", "hdpe_pipes", "pvc_pipes_agri", "valves_fittings", "filters_irrigation"],
        "established_year": 2011,
        "phone": "9876543405",
        "email": "dripsystems@irrigation.com",
        "address": "Keshwapur, Hubli - 580022",
        "experience": 13,
        "license_number": "DRIP-KAR-2011-005"
    },
    {
        "company_name": "Farm Tools & Equipment Hub",
        "location": "Shivamogga",
        "specialization": "Farm tools and equipment",
        "services": ["hand_tools", "power_tools", "sprayers_equipment", "pumps_small", "garden_equipment"],
        "established_year": 2013,
        "phone": "9876543406",
        "email": "farmtools@equipment.com",
        "address": "Market Road, Shivamogga - 577201",
        "experience": 11,
        "license_number": "TOOLS-KAR-2013-006"
    },
    {
        "company_name": "Dairy & Livestock Supplies",
        "location": "Hassan",
        "specialization": "Dairy farming and livestock inputs",
        "services": ["cattle_feed", "poultry_feed", "mineral_mixtures", "veterinary_medicines", "dairy_equipment"],
        "established_year": 2010,
        "phone": "9876543407",
        "email": "dairysupplies@livestock.com",
        "address": "Main Road, Hassan - 573201",
        "experience": 14,
        "license_number": "DAIRY-KAR-2010-007"
    },
    {
        "company_name": "Agri Machinery Rental Services",
        "location": "Kalaburagi",
        "specialization": "Farm equipment on rent",
        "services": ["tractor_rental", "rotavator_rental", "cultivator_rental", "seed_drill_rental", "harvester_rental", "sprayer_rental", "power_tiller_rental"],
        "established_year": 2015,
        "phone": "9876543408",
        "email": "agrirental@machinery.com",
        "address": "Station Road, Kalaburagi - 585101",
        "experience": 9,
        "license_number": "RENT-KAR-2015-008"
    },
    {
        "company_name": "Soil Testing & Advisory Center",
        "location": "Mysuru",
        "specialization": "Soil testing and crop advisory",
        "services": ["soil_testing", "land_preparation", "crop_advisory", "farm_consultation", "pest_disease_management", "fertilizer_recommendation"],
        "established_year": 2014,
        "phone": "9876543409",
        "email": "soiltest@advisory.com",
        "address": "Saraswathipuram, Mysuru - 570009",
        "experience": 10,
        "license_number": "SOIL-KAR-2014-009"
    },
    {
        "company_name": "Farm Infrastructure Builders",
        "location": "Bangalore",
        "specialization": "Greenhouse and farm structures",
        "services": ["greenhouse", "polyhouse", "shade_net", "farm_fencing", "water_tanks_farm", "farm_roads"],
        "established_year": 2012,
        "phone": "9876543410",
        "email": "farminfra@builders.com",
        "address": "Yelahanka, Bangalore - 560064",
        "experience": 12,
        "license_number": "INFRA-KAR-2012-010"
    },
    {
        "company_name": "Agri Marketplace Hub",
        "location": "Bangalore",
        "specialization": "Agriculture marketplace - new equipment",
        "services": ["marketplace_seeds", "marketplace_fertilizers", "marketplace_pesticides", "marketplace_irrigation_equipment", "marketplace_farm_machinery", "marketplace_farm_tools", "marketplace_solar_equipment"],
        "established_year": 2018,
        "phone": "9876543411",
        "email": "agrimarketplace@hub.com",
        "address": "K_R_Market, Bangalore - 560053",
        "experience": 6,
        "license_number": "MKT-KAR-2018-011"
    },
    {
        "company_name": "Second Hand Agri Equipment",
        "location": "Mandya",
        "specialization": "Used agricultural equipment marketplace",
        "services": ["used_tractors", "used_rotavators", "used_harvesters", "used_seed_drills", "used_cultivators", "used_power_tillers", "used_sprayers", "used_pumps_agri", "used_irrigation_systems"],
        "established_year": 2016,
        "phone": "9876543412",
        "email": "usedagri@equipment.com",
        "address": "Industrial Area, Mandya - 571401",
        "experience": 8,
        "license_number": "USED-KAR-2016-012"
    },
    {
        "company_name": "Water Management Systems",
        "location": "Hubli",
        "specialization": "Rainwater harvesting and farm water management",
        "services": ["rainwater_harvesting", "farm_pond_development", "water_storage_tanks", "water_distribution_systems", "water_quality_testing_agri"],
        "established_year": 2013,
        "phone": "9876543413",
        "email": "watermgmt@systems.com",
        "address": "Vidyanagar, Hubli - 580021",
        "experience": 11,
        "license_number": "WATER-KAR-2013-013"
    },
    {
        "company_name": "Agricultural Pumps & Motors",
        "location": "Belagavi",
        "specialization": "Agricultural pumps and motors",
        "services": ["agricultural_pumps", "solar_pumps", "pump_installation_agri", "pump_repair_agri", "motor_rewinding", "control_panels"],
        "established_year": 2009,
        "phone": "9876543414",
        "email": "agripumps@motors.com",
        "address": "Camp Area, Belagavi - 590001",
        "experience": 15,
        "license_number": "AGPUMP-KAR-2009-014"
    }
]

# Borewell Equipment Dealers Vendors
borewell_dealers = [
    {
        "company_name": "Borewell Pumps & Motors Hub",
        "location": "Hubli",
        "specialization": "Complete borewell pump and motor solutions",
        "services": ["dealer_submersible_pumps", "dealer_openwell_pumps", "dealer_monoblock_pumps", "dealer_submersible_motors", "dealer_surface_motors"],
        "established_year": 2010,
        "phone": "9876543501",
        "email": "borewellpumps@hub.com",
        "address": "Industrial Area, Hubli - 580022",
        "experience": 14,
        "license_number": "PUMP-KAR-2010-101"
    },
    {
        "company_name": "Pipes & Fittings World",
        "location": "Dharwad",
        "specialization": "Pipes and fittings for borewells",
        "services": ["dealer_hdpe_pipes", "dealer_pvc_pipes", "dealer_gi_pipes", "dealer_casing_pipes", "dealer_column_pipes"],
        "established_year": 2011,
        "phone": "9876543502",
        "email": "pipesworld@fittings.com",
        "address": "KC Extension, Dharwad - 580008",
        "experience": 13,
        "license_number": "PIPE-KAR-2011-102"
    },
    {
        "company_name": "Electrical Control Systems",
        "location": "Bangalore",
        "specialization": "Electrical panels and controls",
        "services": ["dealer_starter_panels", "dealer_control_panels", "dealer_pump_controllers", "dealer_cables", "dealer_capacitors"],
        "established_year": 2012,
        "phone": "9876543503",
        "email": "electrical@controls.com",
        "address": "Peenya Industrial Area, Bangalore - 560058",
        "experience": 12,
        "license_number": "ELEC-KAR-2012-103"
    },
    {
        "company_name": "Borewell Accessories Hub",
        "location": "Belagavi",
        "specialization": "Borewell accessories and fittings",
        "services": ["dealer_bore_caps", "dealer_clamps", "dealer_valves", "dealer_pipe_fittings", "dealer_cable_guards"],
        "established_year": 2013,
        "phone": "9876543504",
        "email": "borewellaccess@hub.com",
        "address": "Market Road, Belagavi - 590001",
        "experience": 11,
        "license_number": "ACCESS-KAR-2013-104"
    }
]

# Borewell Services Vendors
borewell_services = [
    {
        "company_name": "Complete Borewell Solutions",
        "location": "Hubli",
        "specialization": "Complete borewell cleaning and maintenance",
        "services": ["air_compressor_cleaning", "bore_flushing", "sand_removal", "silt_removal", "mud_removal", "borewell_camera_inspection", "water_yield_improvement"],
        "established_year": 2009,
        "phone": "9876543505",
        "email": "borewellclean@services.com",
        "address": "Keshwapur, Hubli - 580022",
        "experience": 15,
        "license_number": "CLEAN-KAR-2009-105"
    },
    {
        "company_name": "Borewell Repair & Maintenance Experts",
        "location": "Dharwad",
        "specialization": "Borewell restoration and repair",
        "services": ["borewell_restoration", "borewell_casing_repair", "borewell_leakage_repair", "borewell_blockage_removal", "water_flow_restoration", "periodic_maintenance", "borewell_health_inspection"],
        "established_year": 2010,
        "phone": "9876543506",
        "email": "borewellrepair@experts.com",
        "address": "KC Extension, Dharwad - 580008",
        "experience": 14,
        "license_number": "REPAIR-KAR-2010-106"
    },
    {
        "company_name": "Deep Drilling Specialists",
        "location": "Kalaburagi",
        "specialization": "Borewell deepening and re-boring",
        "services": ["borewell_deepening", "re_boring", "casing_pipe_extension", "yield_improvement_deepening", "borewell_rehabilitation"],
        "established_year": 2011,
        "phone": "9876543507",
        "email": "deepdrill@specialists.com",
        "address": "S.B. Temple Road, Kalaburagi - 585101",
        "experience": 13,
        "license_number": "DEEP-KAR-2011-107"
    },
    {
        "company_name": "Groundwater Recharge Solutions",
        "location": "Mysuru",
        "specialization": "Borewell recharge and groundwater management",
        "services": ["recharge_pit_construction", "recharge_shaft_installation", "rainwater_recharge_system", "recharge_bore_construction", "groundwater_recharge_solutions", "recharge_filter_installation"],
        "established_year": 2012,
        "phone": "9876543508",
        "email": "recharge@groundwater.com",
        "address": "Saraswathipuram, Mysuru - 570009",
        "experience": 12,
        "license_number": "RECHARGE-KAR-2012-108"
    },
    {
        "company_name": "Submersible Pump Services",
        "location": "Bangalore",
        "specialization": "Pump installation, repair and replacement",
        "services": ["submersible_pump_installation", "submersible_pump_repair", "submersible_pump_replacement", "pump_pulling_reinstallation", "motor_installation", "motor_repair", "motor_rewinding_borewell", "pump_capacity_upgrade"],
        "established_year": 2013,
        "phone": "9876543509",
        "email": "pumpservices@submersible.com",
        "address": "BTM Layout, Bangalore - 560068",
        "experience": 11,
        "license_number": "SUBPUMP-KAR-2013-109"
    },
    {
        "company_name": "Borewell Electrical Works",
        "location": "Hubli",
        "specialization": "Borewell electrical systems",
        "services": ["starter_panel_installation", "control_panel_installation_borewell", "borewell_wiring", "cable_replacement", "earthing", "electrical_fault_diagnosis", "generator_connection", "automatic_pump_controller_installation"],
        "established_year": 2014,
        "phone": "9876543510",
        "email": "borewell@electrical.com",
        "address": "Vidyanagar, Hubli - 580021",
        "experience": 10,
        "license_number": "BLELEC-KAR-2014-110"
    },
    {
        "company_name": "Pipeline & Plumbing Services",
        "location": "Dharwad",
        "specialization": "Pipeline installation and plumbing",
        "services": ["hdpe_pipe_installation", "pvc_pipe_installation", "gi_pipe_installation", "underground_pipeline", "water_distribution_pipeline", "valve_installation", "pipe_leakage_repair", "pipeline_replacement"],
        "established_year": 2011,
        "phone": "9876543511",
        "email": "pipeline@plumbing.com",
        "address": "KC Extension, Dharwad - 580008",
        "experience": 13,
        "license_number": "PIPELINE-KAR-2011-111"
    },
    {
        "company_name": "Water Testing Laboratories",
        "location": "Mangalore",
        "specialization": "Complete water testing and analysis",
        "services": ["drinking_water_testing", "agricultural_water_testing", "tds_testing", "ph_testing", "water_quality_analysis", "laboratory_testing", "water_purity_consultation"],
        "established_year": 2015,
        "phone": "9876543512",
        "email": "watertest@laboratory.com",
        "address": "PVS Circle, Mangalore - 575003",
        "experience": 9,
        "license_number": "LABTEST-KAR-2015-112"
    },
    {
        "company_name": "Equipment Rental Hub",
        "location": "Hubli",
        "specialization": "Borewell equipment rental services",
        "services": ["drilling_rig_rental", "air_compressor_rental", "borewell_camera_rental", "generator_rental", "pipe_lifting_equipment_rental", "crane_rental", "dewatering_pump_rental"],
        "established_year": 2016,
        "phone": "9876543513",
        "email": "equipmentrental@hub.com",
        "address": "Keshwapur, Hubli - 580022",
        "experience": 8,
        "license_number": "RENTAL-KAR-2016-113"
    },
    {
        "company_name": "Second Hand Borewell Equipment",
        "location": "Belagavi",
        "specialization": "Used borewell equipment marketplace",
        "services": ["used_drilling_rigs", "used_air_compressors", "used_mud_pumps", "used_submersible_pumps_equipment", "used_motors_equipment", "used_generators_equipment", "used_drill_rods", "used_borewell_cameras", "used_starter_panels_equipment", "used_control_panels_equipment", "used_pipe_handling_equipment", "used_water_tankers"],
        "established_year": 2017,
        "phone": "9876543514",
        "email": "usedborewell@equipment.com",
        "address": "Camp Area, Belagavi - 590001",
        "experience": 7,
        "license_number": "USEDBW-KAR-2017-114"
    },
    {
        "company_name": "Emergency Borewell Services 24/7",
        "location": "Hubli",
        "specialization": "Round the clock emergency borewell services",
        "services": ["emergency_pump_breakdown", "no_water_in_borewell", "pump_stuck_in_borewell", "cable_breakage", "borewell_collapse_assistance", "emergency_technician_visit", "24_7_support"],
        "established_year": 2015,
        "phone": "9876543515",
        "email": "emergency@24x7.com",
        "address": "Keshwapur, Hubli - 580022",
        "experience": 9,
        "license_number": "EMER-KAR-2015-115",
        "is_emergency_available": True
    },
    {
        "company_name": "Annual Maintenance Contracts",
        "location": "Bangalore",
        "specialization": "Complete AMC services for borewells",
        "services": ["annual_borewell_maintenance", "pump_inspection_amc", "motor_inspection_amc", "electrical_inspection", "pipeline_inspection", "preventive_maintenance", "scheduled_servicing"],
        "established_year": 2014,
        "phone": "9876543516",
        "email": "amc@borewell.com",
        "address": "BTM Layout, Bangalore - 560068",
        "experience": 10,
        "license_number": "AMC-KAR-2014-116"
    }
]

# Add all new vendors
vendors.extend(agriculture_vendors)
vendors.extend(borewell_dealers)
vendors.extend(borewell_services)

# ============================================
# Create the final JSON structure
# ============================================

final_data = {
    "vendors": vendors
}

# Save to updated vendors file
with open('core/management/commands/updated_vendors_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"Created vendor mapping with {len(vendors)} vendors")
print(f"Vendor breakdown:")
print(f"   - Existing vendors: {len(existing_vendors)}")
print(f"   - New agriculture vendors: {len(agriculture_vendors)}")
print(f"   - Borewell dealers: {len(borewell_dealers)}")
print(f"   - Borewell services: {len(borewell_services)}")
print(f"\nSaved to: core/management/commands/updated_vendors_data.json")