"""
Vendors Data Population Script
Populates the database with sample vendors
"""

import os
import django
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City, Vendor, User, VendorPlan, Service, VendorService
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

# Default password for all vendors
DEFAULT_PASSWORD = "vendor123"

# Sample Vendors Data
VENDORS_DATA = [
    # Maharashtra Vendors
    {
        "company_name": "Agro Water Solutions",
        "username": "agrowater",
        "email": "info@agrowater.com",
        "phone": "9876543210",
        "city": "Mumbai",
        "address": "Plot 123, Industrial Area, Andheri East, Mumbai - 400069",
        "experience": 15,
        "license_number": "AGRI/MH/2020/12345",
        "about": "Leading borewell drilling company with 15+ years of experience in Maharashtra region. Specialized in deep borewell drilling and rock drilling.",
        "services": ["borewell_drilling", "irrigation_systems"],
        "plan_type": "premium",
    },
    {
        "company_name": "Rock Drilling Co",
        "username": "rockdrilling",
        "email": "contact@rockdrilling.com",
        "phone": "9876543214",
        "city": "Pune",
        "address": "156, Hinjewadi, Pune - 411057",
        "experience": 20,
        "license_number": "MH/PUN/2018/22222",
        "about": "Specialized in rock drilling and challenging terrains. Advanced equipment for hard soil conditions. Serving Pune and surrounding areas.",
        "services": ["borewell_drilling"],
        "plan_type": "premium",
    },
    {
        "company_name": "Nashik Borewell Experts",
        "username": "nashikborewell",
        "email": "nashik@borewell.com",
        "phone": "9876543220",
        "city": "Nashik",
        "address": "45, Gangapur Road, Nashik - 422013",
        "experience": 12,
        "license_number": "MH/NASH/2021/33111",
        "about": "Complete borewell solutions for Nashik region. Agricultural and domestic borewell specialists.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "basic",
    },
    {
        "company_name": "Aqua Care Nagpur",
        "username": "aquacarengp",
        "email": "aquacare@nagpur.com",
        "phone": "9876543221",
        "city": "Nagpur",
        "address": "78, Civil Lines, Nagpur - 440001",
        "experience": 10,
        "license_number": "MH/NAG/2022/44444",
        "about": "Water solutions provider for Vidarbha region. Borewell drilling, pump installation, and maintenance services.",
        "services": ["borewell_drilling", "borewell_maintenance", "water_testing"],
        "plan_type": "standard",
    },

    # Karnataka Vendors
    {
        "company_name": "Deep Well Experts",
        "username": "deepwell",
        "email": "contact@deepwell.com",
        "phone": "9876543211",
        "city": "Bangalore",
        "address": "45, Electronics City Phase 1, Bangalore - 560100",
        "experience": 12,
        "license_number": "KAR/BLR/2019/54321",
        "about": "Specialized in deep borewell drilling and rock drilling for residential and commercial purposes. Serving Bangalore since 2012.",
        "services": ["borewell_drilling"],
        "plan_type": "premium",
    },
    {
        "company_name": "Mysore Agro Services",
        "username": "mysoreagro",
        "email": "info@mysoreagro.com",
        "phone": "9876543222",
        "city": "Mysore",
        "address": "23, Industrial Area, Mysore - 570011",
        "experience": 8,
        "license_number": "KAR/MYS/2023/55555",
        "about": "Agricultural borewell and irrigation specialists for Mysore region. Modern drip irrigation experts.",
        "services": ["irrigation_systems", "water_pump_installation"],
        "plan_type": "basic",
    },
    {
        "company_name": "Hubli Water Works",
        "username": "hubliwater",
        "email": "contact@hubliwater.com",
        "phone": "9876543223",
        "city": "Hubli",
        "address": "67, Keshwapur, Hubli - 580021",
        "experience": 14,
        "license_number": "KAR/HUB/2020/66666",
        "about": "Complete water solutions for North Karnataka. Borewell drilling, pump services, and maintenance.",
        "services": ["borewell_drilling", "water_pump_installation", "borewell_maintenance"],
        "plan_type": "standard",
    },

    # Telangana Vendors
    {
        "company_name": "Green Field Irrigation",
        "username": "greenfield",
        "email": "sales@greenfield.com",
        "phone": "9876543212",
        "city": "Hyderabad",
        "address": "78, Madhapur, Hyderabad - 500081",
        "experience": 10,
        "license_number": "TS/HYD/2021/67890",
        "about": "Complete irrigation solutions for farms and gardens. Modern drip and sprinkler systems. Serving Telangana.",
        "services": ["irrigation_systems", "water_pump_installation"],
        "plan_type": "premium",
    },
    {
        "company_name": "Warangal Borewell Services",
        "username": "warangalborewell",
        "email": "info@warangalborewell.com",
        "phone": "9876543224",
        "city": "Warangal",
        "address": "34, Hanumakonda, Warangal - 506001",
        "experience": 11,
        "license_number": "TS/WAR/2022/77777",
        "about": "Expert borewell drilling services for Warangal and surrounding districts. Agricultural specialists.",
        "services": ["borewell_drilling"],
        "plan_type": "basic",
    },

    # Tamil Nadu Vendors
    {
        "company_name": "Pump Masters",
        "username": "pumpmasters",
        "email": "info@pumpmasters.com",
        "phone": "9876543213",
        "city": "Chennai",
        "address": "23, Anna Nagar, Chennai - 600040",
        "experience": 8,
        "license_number": "TN/CHN/2022/11111",
        "about": "Expert water pump installation and maintenance services across Tamil Nadu. Authorized dealer for major pump brands.",
        "services": ["water_pump_installation", "borewell_maintenance"],
        "plan_type": "standard",
    },
    {
        "company_name": "Coimbatore Agri Tech",
        "username": "coimbatoreagri",
        "email": "agri@coimbatore.com",
        "phone": "9876543225",
        "city": "Coimbatore",
        "address": "56, Peelamedu, Coimbatore - 641004",
        "experience": 16,
        "license_number": "TN/CBE/2019/88888",
        "about": "Leading agricultural borewell company in Coimbatore. Specialized in farm irrigation systems and deep borewells.",
        "services": ["borewell_drilling", "irrigation_systems"],
        "plan_type": "premium",
    },
    {
        "company_name": "Madurai Water Solutions",
        "username": "maduraiwater",
        "email": "contact@maduraiwater.com",
        "phone": "9876543226",
        "city": "Madurai",
        "address": "89, KK Nagar, Madurai - 625020",
        "experience": 9,
        "license_number": "TN/MDU/2023/99999",
        "about": "Complete water solutions for Madurai region. Borewell drilling, pump installation, and maintenance.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "basic",
    },

    # Gujarat Vendors
    {
        "company_name": "Well Care Solutions",
        "username": "wellcare",
        "email": "contact@wellcare.com",
        "phone": "9876543217",
        "city": "Ahmedabad",
        "address": "67, Shivranjani, Ahmedabad - 380015",
        "experience": 14,
        "license_number": "GJ/AMD/2019/55555",
        "about": "Borewell maintenance and restoration experts. 24/7 emergency service available. Serving Gujarat.",
        "services": ["borewell_maintenance", "water_testing"],
        "plan_type": "premium",
    },
    {
        "company_name": "Surat Borewell Drilling",
        "username": "suratdrilling",
        "email": "info@suratdrilling.com",
        "phone": "9876543227",
        "city": "Surat",
        "address": "123, Katargam, Surat - 395004",
        "experience": 13,
        "license_number": "GJ/SUR/2021/10101",
        "about": "Expert borewell drilling services in Surat. Specialized in residential and commercial drilling.",
        "services": ["borewell_drilling"],
        "plan_type": "standard",
    },
    {
        "company_name": "Vadodara Water Systems",
        "username": "vadodarawater",
        "email": "vadodara@watersys.com",
        "phone": "9876543228",
        "city": "Vadodara",
        "address": "45, Alkapuri, Vadodara - 390007",
        "experience": 10,
        "license_number": "GJ/VAD/2022/12121",
        "about": "Complete water solutions for Vadodara. Borewell, pumps, and irrigation systems.",
        "services": ["borewell_drilling", "irrigation_systems", "water_pump_installation"],
        "plan_type": "premium",
    },

    # Rajasthan Vendors
    {
        "company_name": "Farm Irrigation Systems",
        "username": "farmirrigation",
        "email": "info@farmirrigation.com",
        "phone": "9876543216",
        "city": "Jaipur",
        "address": "89, Industrial Area, Jaipur - 302006",
        "experience": 9,
        "license_number": "RJ/JAI/2021/44444",
        "about": "Modern irrigation systems for agricultural lands. Drip and sprinkler specialists. Serving Rajasthan.",
        "services": ["irrigation_systems"],
        "plan_type": "standard",
    },
    {
        "company_name": "Jodhpur Borewell Works",
        "username": "jodhpurborewell",
        "email": "jodhpur@borewell.com",
        "phone": "9876543229",
        "city": "Jodhpur",
        "address": "34, Basni, Jodhpur - 342005",
        "experience": 11,
        "license_number": "RJ/JOD/2020/13131",
        "about": "Expert borewell drilling in arid regions of Rajasthan. Deep drilling specialists.",
        "services": ["borewell_drilling"],
        "plan_type": "basic",
    },
    {
        "company_name": "Udaipur Water Solutions",
        "username": "udaiwater",
        "email": "udaipur@watersol.com",
        "phone": "9876543230",
        "city": "Udaipur",
        "address": "67, Fatehpura, Udaipur - 313001",
        "experience": 7,
        "license_number": "RJ/UDAI/2023/14141",
        "about": "Water solutions for Udaipur region. Borewell drilling and pump installation.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "basic",
    },

    # Delhi NCR Vendors
    {
        "company_name": "Aqua Tech Services",
        "username": "aquatech",
        "email": "support@aquatech.com",
        "phone": "9876543215",
        "city": "Delhi",
        "address": "45, Nehru Place, New Delhi - 110019",
        "experience": 11,
        "license_number": "DL/ND/2020/33333",
        "about": "Complete water solutions including drilling, pumps, and maintenance services. Serving Delhi NCR.",
        "services": ["borewell_drilling", "water_pump_installation", "borewell_maintenance"],
        "plan_type": "premium",
    },
    {
        "company_name": "Gurgaon Water Works",
        "username": "gurgaonwater",
        "email": "gurgaon@waterworks.com",
        "phone": "9876543231",
        "city": "Gurgaon",
        "address": "78, Sector 18, Gurgaon - 122015",
        "experience": 8,
        "license_number": "HR/GUR/2022/15151",
        "about": "Borewell and water solutions for Gurgaon and surrounding areas. Residential and commercial experts.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "standard",
    },
    {
        "company_name": "Noida Borewell Experts",
        "username": "noidaborewell",
        "email": "noida@borewell.com",
        "phone": "9876543232",
        "city": "Noida",
        "address": "56, Sector 62, Noida - 201309",
        "experience": 10,
        "license_number": "UP/NOI/2021/16161",
        "about": "Expert borewell drilling services for Noida and Greater Noida. Modern equipment and techniques.",
        "services": ["borewell_drilling"],
        "plan_type": "standard",
    },

    # Uttar Pradesh Vendors
    {
        "company_name": "Lucknow Water Solutions",
        "username": "lucknowwater",
        "email": "info@lucknowwater.com",
        "phone": "9876543233",
        "city": "Lucknow",
        "address": "23, Gomti Nagar, Lucknow - 226010",
        "experience": 12,
        "license_number": "UP/LKO/2020/17171",
        "about": "Complete water solutions for Lucknow. Borewell drilling, irrigation, and maintenance.",
        "services": ["borewell_drilling", "irrigation_systems", "water_testing"],
        "plan_type": "premium",
    },
    {
        "company_name": "Kanpur Agro Wells",
        "username": "kanpuragro",
        "email": "kanpur@agrowells.com",
        "phone": "9876543234",
        "city": "Kanpur",
        "address": "89, Civil Lines, Kanpur - 208001",
        "experience": 15,
        "license_number": "UP/KNP/2019/18181",
        "about": "Agricultural borewell specialists for Kanpur region. 15+ years of experience.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "standard",
    },
    {
        "company_name": "Agra Water Systems",
        "username": "agrawater",
        "email": "agra@watersys.com",
        "phone": "9876543235",
        "city": "Agra",
        "address": "45, Dayalbagh, Agra - 282004",
        "experience": 9,
        "license_number": "UP/AGR/2022/19191",
        "about": "Water solutions for Agra and surrounding areas. Borewell and pump services.",
        "services": ["borewell_drilling", "water_pump_installation", "borewell_maintenance"],
        "plan_type": "basic",
    },

    # West Bengal Vendors
    {
        "company_name": "Kolkata Borewell Co",
        "username": "kolkataborewell",
        "email": "kolkata@borewellco.com",
        "phone": "9876543236",
        "city": "Kolkata",
        "address": "67, Salt Lake, Kolkata - 700091",
        "experience": 18,
        "license_number": "WB/KOL/2018/20202",
        "about": "Leading borewell company in Kolkata. Expert in deep drilling and challenging terrains.",
        "services": ["borewell_drilling", "water_testing"],
        "plan_type": "premium",
    },
    {
        "company_name": "Howrah Water Works",
        "username": "howrahwater",
        "email": "howrah@waterworks.com",
        "phone": "9876543237",
        "city": "Howrah",
        "address": "34, Shibpur, Howrah - 711102",
        "experience": 10,
        "license_number": "WB/HOW/2021/21212",
        "about": "Water solutions for Howrah and surrounding areas. Borewell drilling and pump services.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "standard",
    },

    # Madhya Pradesh Vendors
    {
        "company_name": "Indore Water Solutions",
        "username": "indorewater",
        "email": "indore@watersol.com",
        "phone": "9876543238",
        "city": "Indore",
        "address": "56, Vijay Nagar, Indore - 452010",
        "experience": 11,
        "license_number": "MP/IND/2020/23232",
        "about": "Complete water solutions for Indore and MP region. Borewell, irrigation, and maintenance.",
        "services": ["borewell_drilling", "irrigation_systems", "water_pump_installation"],
        "plan_type": "premium",
    },
    {
        "company_name": "Bhopal Borewell Services",
        "username": "bhopalborewell",
        "email": "bhopal@borewell.com",
        "phone": "9876543239",
        "city": "Bhopal",
        "address": "78, MP Nagar, Bhopal - 462011",
        "experience": 13,
        "license_number": "MP/BHOP/2019/24242",
        "about": "Expert borewell drilling in Bhopal. Agricultural and domestic specialists.",
        "services": ["borewell_drilling"],
        "plan_type": "standard",
    },

    # Andhra Pradesh Vendors
    {
        "company_name": "Visakhapatnam Water Works",
        "username": "vizagwater",
        "email": "vizag@waterworks.com",
        "phone": "9876543240",
        "city": "Visakhapatnam",
        "address": "45, MVP Colony, Visakhapatnam - 530017",
        "experience": 14,
        "license_number": "AP/VIZ/2020/25252",
        "about": "Water solutions for Coastal Andhra. Borewell drilling and irrigation systems.",
        "services": ["borewell_drilling", "irrigation_systems"],
        "plan_type": "premium",
    },
    {
        "company_name": "Vijayawada Agro Tech",
        "username": "vijayawadaagro",
        "email": "vijayawada@agrotech.com",
        "phone": "9876543241",
        "city": "Vijayawada",
        "address": "89, Benz Circle, Vijayawada - 520010",
        "experience": 10,
        "license_number": "AP/VIJ/2022/26262",
        "about": "Agricultural borewell and irrigation specialists for Krishna district.",
        "services": ["borewell_drilling", "irrigation_systems", "water_pump_installation"],
        "plan_type": "standard",
    },

    # Kerala Vendors
    {
        "company_name": "Kochi Water Solutions",
        "username": "kochiwater",
        "email": "kochi@watersol.com",
        "phone": "9876543242",
        "city": "Kochi",
        "address": "23, Kadavanthra, Kochi - 682020",
        "experience": 9,
        "license_number": "KL/KOC/2021/27272",
        "about": "Water solutions for Kochi and Kerala. Borewell drilling and pump installation.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "basic",
    },
    {
        "company_name": "Trivandrum Borewell Co",
        "username": "trivandrumbw",
        "email": "trivandrum@borewell.com",
        "phone": "9876543243",
        "city": "Thiruvananthapuram",
        "address": "67, Sasthamangalam, Trivandrum - 695010",
        "experience": 12,
        "license_number": "KL/TVM/2020/28282",
        "about": "Expert borewell services in Trivandrum. Deep drilling specialists for Kerala conditions.",
        "services": ["borewell_drilling", "water_testing"],
        "plan_type": "standard",
    },

    # Punjab Vendors
    {
        "company_name": "Ludhiana Agro Wells",
        "username": "ludhianaagro",
        "email": "ludhiana@agrowells.com",
        "phone": "9876543244",
        "city": "Ludhiana",
        "address": "34, Model Town, Ludhiana - 141002",
        "experience": 16,
        "license_number": "PB/LUD/2019/29292",
        "about": "Agricultural borewell specialists for Punjab. Serving Ludhiana and surrounding districts.",
        "services": ["borewell_drilling", "irrigation_systems"],
        "plan_type": "premium",
    },
    {
        "company_name": "Amritsar Water Works",
        "username": "amritsarwater",
        "email": "amritsar@waterworks.com",
        "phone": "9876543245",
        "city": "Amritsar",
        "address": "78, Ranjit Avenue, Amritsar - 143001",
        "experience": 11,
        "license_number": "PB/AMR/2021/30303",
        "about": "Complete water solutions for Amritsar. Borewell drilling and pump installation.",
        "services": ["borewell_drilling", "water_pump_installation", "borewell_maintenance"],
        "plan_type": "standard",
    },

    # Haryana Vendors
    {
        "company_name": "Panipat Borewell Services",
        "username": "panipatborewell",
        "email": "panipat@borewell.com",
        "phone": "9876543246",
        "city": "Panipat",
        "address": "45, Sector 25, Panipat - 132103",
        "experience": 8,
        "license_number": "HR/PAN/2022/31313",
        "about": "Borewell drilling services for Panipat and surrounding areas. Agricultural specialists.",
        "services": ["borewell_drilling"],
        "plan_type": "basic",
    },
    {
        "company_name": "Karnal Water Solutions",
        "username": "karnalwater",
        "email": "karnal@watersol.com",
        "phone": "9876543247",
        "city": "Karnal",
        "address": "67, Model Town, Karnal - 132001",
        "experience": 10,
        "license_number": "HR/KAR/2020/32323",
        "about": "Water solutions for Karnal. Borewell drilling and irrigation systems for agricultural lands.",
        "services": ["borewell_drilling", "irrigation_systems"],
        "plan_type": "standard",
    },

    # Bihar Vendors
    {
        "company_name": "Patna Water Works",
        "username": "patnawater",
        "email": "patna@waterworks.com",
        "phone": "9876543248",
        "city": "Patna",
        "experience": 13,
        "license_number": "BR/PAT/2021/33333",
        "about": "Complete water solutions for Patna and Bihar. Borewell drilling and pump installation.",
        "services": ["borewell_drilling", "water_pump_installation"],
        "plan_type": "premium",
    },
    {
        "company_name": "Gaya Borewell Experts",
        "username": "gayaborewell",
        "email": "gaya@borewell.com",
        "phone": "9876543249",
        "city": "Gaya",
        "address": "89, Bodh Gaya Road, Gaya - 823001",
        "experience": 9,
        "license_number": "BR/GAY/2022/34343",
        "about": "Expert borewell drilling in Gaya and surrounding districts. Residential and agricultural.",
        "services": ["borewell_drilling"],
        "plan_type": "basic",
    },

    # Odisha Vendors
    {
        "company_name": "Bhubaneswar Water Solutions",
        "username": "bbsrwater",
        "email": "bbsr@watersol.com",
        "phone": "9876543250",
        "city": "Bhubaneswar",
        "address": "56, Unit 1, Bhubaneswar - 751001",
        "experience": 11,
        "license_number": "OD/BBSR/2020/35353",
        "about": "Complete water solutions for Odisha capital. Borewell drilling and irrigation systems.",
        "services": ["borewell_drilling", "irrigation_systems", "water_pump_installation"],
        "plan_type": "premium",
    },
    {
        "company_name": "Cuttack Borewell Co",
        "username": "cuttackborewell",
        "email": "cuttack@borewell.com",
        "phone": "9876543251",
        "city": "Cuttack",
        "address": "78, CDA Sector 9, Cuttack - 753014",
        "experience": 10,
        "license_number": "OD/CUT/2021/36363",
        "about": "Borewell drilling services for Cuttack and surrounding areas. Expert in all soil conditions.",
        "services": ["borewell_drilling"],
        "plan_type": "standard",
    },

    # Additional Vendors - Construction Sector
    {
        "company_name": "Earth Excavators India",
        "username": "earthexcavators",
        "email": "info@earthexcavators.com",
        "phone": "9876543252",
        "city": "Delhi",
        "address": "34, Okhla Industrial Area, New Delhi - 110020",
        "experience": 15,
        "license_number": "DL/EARTH/2019/37373",
        "about": "Specialized in earth excavation for construction projects. Foundation digging and trench excavation experts.",
        "services": ["earth_excavation", "land_leveling"],
        "plan_type": "premium",
    },
    {
        "company_name": "Mumbai Construction Drilling",
        "username": "mumbaidrilling",
        "email": "mumbai@construcdrill.com",
        "phone": "9876543253",
        "city": "Mumbai",
        "address": "67, Lower Parel, Mumbai - 400013",
        "experience": 12,
        "license_number": "MH/CONST/2020/38383",
        "about": "Construction drilling specialists for Mumbai. Foundation drilling and land leveling services.",
        "services": ["earth_excavation"],
        "plan_type": "premium",
    },

    # Additional Maintenance Specialists
    {
        "company_name": "Borewell Rescue Services",
        "username": "borewellrescue",
        "email": "rescue@borewell.com",
        "phone": "9876543254",
        "city": "Hyderabad",
        "address": "45, Kondapur, Hyderabad - 500084",
        "experience": 20,
        "license_number": "TS/RESCUE/2018/39393",
        "about": "24/7 emergency borewell rescue and maintenance services. Camera inspection and restoration experts.",
        "services": ["borewell_maintenance", "water_testing"],
        "plan_type": "premium",
    },
    {
        "company_name": "Pump Repair Hub",
        "username": "pumprepairhub",
        "email": "repair@pumphub.com",
        "phone": "9876543255",
        "city": "Chennai",
        "address": "89, Ambattur, Chennai - 600053",
        "experience": 14,
        "license_number": "TN/PUMP/2021/40404",
        "about": "Authorized service center for all major pump brands. Repair and maintenance specialists.",
        "services": ["borewell_maintenance"],
        "plan_type": "standard",
    },
    {
        "company_name": "Water Quality Labs",
        "username": "waterquality",
        "email": "lab@waterquality.com",
        "phone": "9876543256",
        "city": "Bangalore",
        "address": "23, Whitefield, Bangalore - 560066",
        "experience": 8,
        "license_number": "KAR/LAB/2022/41414",
        "about": "NABL accredited water testing laboratory. Borewell water quality analysis and inspection services.",
        "services": ["water_testing"],
        "plan_type": "standard",
    },
]


# Plan pricing configuration
PLAN_CONFIG = {
    "basic": {"price": 5000, "name": "Basic Plan", "validity": 365},
    "standard": {"price": 10000, "name": "Standard Plan", "validity": 365},
    "premium": {"price": 20000, "name": "Premium Plan", "validity": 365},
}


def populate_vendors():
    """Populate sample vendors"""
    print("="*60)
    print("Vendors Data Population Script")
    print("="*60)
    print("\nPopulating vendors...")

    created_count = 0
    updated_count = 0
    error_count = 0

    for vendor_data in VENDORS_DATA:
        try:
            # Get city
            city = City.objects.get(name=vendor_data["city"])

            # Create or update user account
            user, created = User.objects.get_or_create(
                username=vendor_data["username"],
                defaults={
                    "email": vendor_data["email"],
                    "password": make_password(DEFAULT_PASSWORD),
                    "first_name": vendor_data["company_name"],
                    "is_active": True,
                }
            )

            if created:
                print(f"  ✓ Created user: {user.username}")
            else:
                # Update email if user exists
                user.email = vendor_data["email"]
                user.first_name = vendor_data["company_name"]
                user.save()
                print(f"  - Updated user: {user.username}")

            # Create or update vendor profile
            vendor, created = Vendor.objects.get_or_create(
                user=user,
                defaults={
                    "company_name": vendor_data["company_name"],
                    "phone": vendor_data["phone"],
                    "city": city,
                    "address": vendor_data.get("address", ""),
                    "experience": vendor_data["experience"],
                    "license_number": vendor_data.get("license_number", ""),
                    "about": vendor_data.get("about", ""),
                    "verification_status": "verified",
                }
            )

            if created:
                created_count += 1
                print(f"    ✓ Created vendor: {vendor.company_name} ({city.name})")

                # Create vendor plan
                plan_info = PLAN_CONFIG.get(vendor_data.get("plan_type", "basic"), PLAN_CONFIG["basic"])
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=plan_info["validity"])

                VendorPlan.objects.create(
                    vendor=vendor,
                    plan_type=vendor_data.get("plan_type", "basic"),
                    plan_name=plan_info["name"],
                    price=plan_info["price"],
                    start_date=start_date,
                    end_date=end_date,
                    status="active",
                    validity_period=plan_info["validity"],
                )
                print(f"      ✓ Created {plan_info['name']} - ₹{plan_info['price']}")
            else:
                updated_count += 1
                # Update vendor details if exists
                vendor.company_name = vendor_data["company_name"]
                vendor.phone = vendor_data["phone"]
                vendor.city = city
                vendor.address = vendor_data.get("address", "")
                vendor.experience = vendor_data["experience"]
                vendor.license_number = vendor_data.get("license_number", "")
                vendor.about = vendor_data.get("about", "")
                vendor.save()
                print(f"    - Updated vendor: {vendor.company_name} ({city.name})")

            # Link services to vendor
            services_linked = 0
            for service_id in vendor_data["services"]:
                try:
                    service = Service.objects.get(id=service_id)
                    VendorService.objects.get_or_create(
                        vendor=vendor,
                        service=service,
                        defaults={"price": random.randint(100, 200)}
                    )
                    services_linked += 1
                except Service.DoesNotExist:
                    print(f"      ! Service not found: {service_id}")

            if services_linked > 0:
                print(f"      ✓ Linked {services_linked} services")

        except City.DoesNotExist:
            print(f"      ✗ City not found: {vendor_data['city']}")
            error_count += 1
        except Exception as e:
            print(f"      ✗ Error creating vendor {vendor_data.get('username', 'unknown')}: {e}")
            error_count += 1

    print("\n" + "="*60)
    print("✓ Vendor population completed!")
    print("="*60)

    print("\nSummary:")
    print(f"  Created: {created_count}")
    print(f"  Updated: {updated_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total vendors in database: {Vendor.objects.count()}")

    print("\nLogin credentials:")
    print(f"  Username: vendor's username")
    print(f"  Password: {DEFAULT_PASSWORD}")


def clear_vendors():
    """Clear all existing vendors"""
    print("\n" + "="*60)
    print("Clearing existing vendors...")
    print("="*60)

    vendor_count = Vendor.objects.count()
    user_count = User.objects.filter(vendor__isnull=False).count()

    Vendor.objects.all().delete()
    VendorPlan.objects.all().delete()
    VendorService.objects.all().delete()
    User.objects.filter(vendor__isnull=False).delete()

    print(f"✓ Deleted {vendor_count} vendors")
    print(f"✓ Deleted {user_count} vendor users")
    print(f"✓ Deleted associated plans and services")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_vendors()
        print("\nRun script again without --clear to populate vendors.")
    else:
        populate_vendors()