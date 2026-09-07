"""
City Data Population Script
Populates the database with Indian cities
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City

# Cities Data - Major Indian cities
CITIES_DATA = [
    # Maharashtra
    {"name": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Pune", "state": "Maharashtra", "latitude": 18.5204, "longitude": 73.8567},
    {"name": "Nagpur", "state": "Maharashtra", "latitude": 21.1458, "longitude": 79.0882},
    {"name": "Thane", "state": "Maharashtra", "latitude": 19.2183, "longitude": 72.9781},
    {"name": "Nashik", "state": "Maharashtra", "latitude": 19.9975, "longitude": 73.7898},
    {"name": "Aurangabad", "state": "Maharashtra", "latitude": 19.8762, "longitude": 75.3433},
    {"name": "Solapur", "state": "Maharashtra", "latitude": 17.6599, "longitude": 75.9064},

    # Karnataka
    {"name": "Bangalore", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Mysore", "state": "Karnataka", "latitude": 12.2958, "longitude": 76.6394},
    {"name": "Hubli", "state": "Karnataka", "latitude": 15.3647, "longitude": 75.1240},
    {"name": "Mangalore", "state": "Karnataka", "latitude": 12.9141, "longitude": 74.8560},
    {"name": "Belgaum", "state": "Karnataka", "latitude": 15.8608, "longitude": 74.5059},

    # Telangana
    {"name": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867},
    {"name": "Warangal", "state": "Telangana", "latitude": 17.9684, "longitude": 79.5605},
    {"name": "Nizamabad", "state": "Telangana", "latitude": 18.6725, "longitude": 78.0926},

    # Tamil Nadu
    {"name": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707},
    {"name": "Coimbatore", "state": "Tamil Nadu", "latitude": 11.0168, "longitude": 76.9558},
    {"name": "Madurai", "state": "Tamil Nadu", "latitude": 9.9252, "longitude": 78.1198},
    {"name": "Tiruchirappalli", "state": "Tamil Nadu", "latitude": 10.7905, "longitude": 78.7047},
    {"name": "Salem", "state": "Tamil Nadu", "latitude": 11.6643, "longitude": 78.1460},
    {"name": "Erode", "state": "Tamil Nadu", "latitude": 11.3410, "longitude": 77.7172},
    {"name": "Tirunelveli", "state": "Tamil Nadu", "latitude": 8.7139, "longitude": 77.5444},

    # Gujarat
    {"name": "Ahmedabad", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714},
    {"name": "Surat", "state": "Gujarat", "latitude": 21.1702, "longitude": 72.8311},
    {"name": "Vadodara", "state": "Gujarat", "latitude": 22.3107, "longitude": 73.1872},
    {"name": "Rajkot", "state": "Gujarat", "latitude": 22.2587, "longitude": 70.8043},
    {"name": "Bhavnagar", "state": "Gujarat", "latitude": 21.7632, "longitude": 72.1514},
    {"name": "Jamnagar", "state": "Gujarat", "latitude": 22.4707, "longitude": 70.0577},

    # Rajasthan
    {"name": "Jaipur", "state": "Rajasthan", "latitude": 26.9124, "longitude": 75.7873},
    {"name": "Jodhpur", "state": "Rajasthan", "latitude": 26.2989, "longitude": 73.0181},
    {"name": "Udaipur", "state": "Rajasthan", "latitude": 24.5854, "longitude": 73.7125},
    {"name": "Kota", "state": "Rajasthan", "latitude": 25.1381, "longitude": 75.8376},
    {"name": "Bikaner", "state": "Rajasthan", "latitude": 28.0039, "longitude": 73.3028},
    {"name": "Ajmer", "state": "Rajasthan", "latitude": 26.4499, "longitude": 74.6399},

    # Delhi NCR
    {"name": "Delhi", "state": "Delhi", "latitude": 28.7041, "longitude": 77.1025},
    {"name": "New Delhi", "state": "Delhi", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Gurgaon", "state": "Haryana", "latitude": 28.4594, "longitude": 77.0266},
    {"name": "Noida", "state": "Uttar Pradesh", "latitude": 28.5355, "longitude": 77.3910},
    {"name": "Faridabad", "state": "Haryana", "latitude": 28.4089, "longitude": 77.3178},
    {"name": "Ghaziabad", "state": "Uttar Pradesh", "latitude": 28.6692, "longitude": 77.4538},

    # Uttar Pradesh
    {"name": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462},
    {"name": "Kanpur", "state": "Uttar Pradesh", "latitude": 26.4499, "longitude": 80.3319},
    {"name": "Agra", "state": "Uttar Pradesh", "latitude": 27.1751, "longitude": 78.0421},
    {"name": "Varanasi", "state": "Uttar Pradesh", "latitude": 25.3176, "longitude": 82.9739},
    {"name": "Allahabad", "state": "Uttar Pradesh", "latitude": 25.4358, "longitude": 81.8463},
    {"name": "Meerut", "state": "Uttar Pradesh", "latitude": 28.9844, "longitude": 77.7064},
    {"name": "Bareilly", "state": "Uttar Pradesh", "latitude": 28.3670, "longitude": 79.4304},
    {"name": "Aligarh", "state": "Uttar Pradesh", "latitude": 27.8803, "longitude": 78.0777},

    # West Bengal
    {"name": "Kolkata", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639},
    {"name": "Howrah", "state": "West Bengal", "latitude": 22.5958, "longitude": 88.2636},
    {"name": "Durgapur", "state": "West Bengal", "latitude": 23.5204, "longitude": 87.3119},
    {"name": "Asansol", "state": "West Bengal", "latitude": 23.6738, "longitude": 86.9524},
    {"name": "Siliguri", "state": "West Bengal", "latitude": 26.7271, "longitude": 88.3947},

    # Madhya Pradesh
    {"name": "Indore", "state": "Madhya Pradesh", "latitude": 22.7196, "longitude": 75.8577},
    {"name": "Bhopal", "state": "Madhya Pradesh", "latitude": 23.2599, "longitude": 77.4126},
    {"name": "Jabalpur", "state": "Madhya Pradesh", "latitude": 23.1815, "longitude": 79.9864},
    {"name": "Gwalior", "state": "Madhya Pradesh", "latitude": 26.2183, "longitude": 78.1828},
    {"name": "Ujjain", "state": "Madhya Pradesh", "latitude": 23.1826, "longitude": 75.7772},

    # Andhra Pradesh
    {"name": "Visakhapatnam", "state": "Andhra Pradesh", "latitude": 17.6868, "longitude": 83.2185},
    {"name": "Vijayawada", "state": "Andhra Pradesh", "latitude": 16.5062, "longitude": 80.6480},
    {"name": "Guntur", "state": "Andhra Pradesh", "latitude": 16.2998, "longitude": 80.4576},
    {"name": "Tirupati", "state": "Andhra Pradesh", "latitude": 13.6288, "longitude": 79.4188},
    {"name": "Kakinada", "state": "Andhra Pradesh", "latitude": 16.9892, "longitude": 82.2476},

    # Kerala
    {"name": "Kochi", "state": "Kerala", "latitude": 9.9312, "longitude": 76.2673},
    {"name": "Thiruvananthapuram", "state": "Kerala", "latitude": 8.5241, "longitude": 76.9366},
    {"name": "Kozhikode", "state": "Kerala", "latitude": 11.2588, "longitude": 75.7804},
    {"name": "Kollam", "state": "Kerala", "latitude": 8.8808, "longitude": 76.5956},

    # Odisha
    {"name": "Bhubaneswar", "state": "Odisha", "latitude": 20.2961, "longitude": 85.8245},
    {"name": "Cuttack", "state": "Odisha", "latitude": 20.4625, "longitude": 85.8831},
    {"name": "Rourkela", "state": "Odisha", "latitude": 22.2517, "longitude": 84.8484},
    {"name": "Berhampur", "state": "Odisha", "latitude": 19.3059, "longitude": 84.7972},

    # Punjab
    {"name": "Ludhiana", "state": "Punjab", "latitude": 30.9010, "longitude": 75.8573},
    {"name": "Amritsar", "state": "Punjab", "latitude": 31.6340, "longitude": 74.8723},
    {"name": "Jalandhar", "state": "Punjab", "latitude": 31.3260, "longitude": 75.5760},
    {"name": "Patiala", "state": "Punjab", "latitude": 30.3398, "longitude": 76.3869},

    # Haryana
    {"name": "Panipat", "state": "Haryana", "latitude": 29.3893, "longitude": 76.9698},
    {"name": "Ambala", "state": "Haryana", "latitude": 30.3782, "longitude": 76.7794},
    {"name": "Karnal", "state": "Haryana", "latitude": 29.6857, "longitude": 76.9905},
    {"name": "Hisar", "state": "Haryana", "latitude": 29.1492, "longitude": 75.7210},

    # Bihar
    {"name": "Patna", "state": "Bihar", "latitude": 25.5941, "longitude": 85.1376},
    {"name": "Gaya", "state": "Bihar", "latitude": 24.7914, "longitude": 85.0002},
    {"name": "Bhagalpur", "state": "Bihar", "latitude": 25.2551, "longitude": 86.9977},
    {"name": "Muzaffarpur", "state": "Bihar", "latitude": 26.1224, "longitude": 85.3925},

    # Jharkhand
    {"name": "Ranchi", "state": "Jharkhand", "latitude": 23.3441, "longitude": 85.3096},
    {"name": "Jamshedpur", "state": "Jharkhand", "latitude": 22.8046, "longitude": 86.2028},
    {"name": "Dhanbad", "state": "Jharkhand", "latitude": 23.7957, "longitude": 86.4304},

    # Chhattisgarh
    {"name": "Raipur", "state": "Chhattisgarh", "latitude": 21.2514, "longitude": 81.5988},
    {"name": "Bhilai", "state": "Chhattisgarh", "latitude": 21.2146, "longitude": 81.4022},
    {"name": "Bilaspur", "state": "Chhattisgarh", "latitude": 22.0897, "longitude": 82.1415},

    # Assam
    {"name": "Guwahati", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362},
    {"name": "Dibrugarh", "state": "Assam", "latitude": 27.4827, "longitude": 94.9080},
    {"name": "Silchar", "state": "Assam", "latitude": 24.8333, "longitude": 92.7936},

    # Uttarakhand
    {"name": "Dehradun", "state": "Uttarakhand", "latitude": 30.3165, "longitude": 78.0304},
    {"name": "Haridwar", "state": "Uttarakhand", "latitude": 29.9455, "longitude": 78.1635},

    # Goa
    {"name": "Panaji", "state": "Goa", "latitude": 15.4909, "longitude": 73.8123},
    {"name": "Margao", "state": "Goa", "latitude": 15.2769, "longitude": 73.9598},

    # Jammu & Kashmir
    {"name": "Srinagar", "state": "Jammu & Kashmir", "latitude": 34.0837, "longitude": 74.7973},
    {"name": "Jammu", "state": "Jammu & Kashmir", "latitude": 32.7266, "longitude": 74.8570},

    # Himachal Pradesh
    {"name": "Shimla", "state": "Himachal Pradesh", "latitude": 31.1048, "longitude": 77.1734},
]


def populate_cities():
    """Populate cities in the database"""
    print("="*50)
    print("City Data Population Script")
    print("="*50)
    print("\nPopulating cities...")

    created_count = 0
    existing_count = 0

    for city_data in CITIES_DATA:
        city, created = City.objects.get_or_create(
            name=city_data["name"],
            defaults={
                "state": city_data["state"],
                "latitude": city_data["latitude"],
                "longitude": city_data["longitude"],
            }
        )
        if created:
            created_count += 1
            print(f"  ✓ Created city: {city.name}, {city.state}")
        else:
            existing_count += 1
            print(f"  - City already exists: {city.name}, {city.state}")

    print("\n" + "="*50)
    print(f"✓ Completed! Created: {created_count}, Existing: {existing_count}")
    print(f"Total cities in database: {City.objects.count()}")
    print("="*50)


if __name__ == "__main__":
    populate_cities()
