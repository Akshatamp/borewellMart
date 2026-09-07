import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from core.models import City

# List of cities with their states
cities_with_states = {
    'Agra': 'Uttar Pradesh',
    'Akodia': 'Madhya Pradesh',
    'Ambikapur': 'Chhattisgarh',
    'Anakapalle': 'Andhra Pradesh',
    'Anantapur': 'Andhra Pradesh',
    'Angul': 'Odisha',
    'Aranmanaipudur': 'Tamil Nadu',
    'Aranthangi': 'Tamil Nadu',
    'Ashadha': 'Madhya Pradesh',
    'Attur': 'Tamil Nadu',
    'Ayodhya': 'Uttar Pradesh',
    'Badi Kheri': 'Uttar Pradesh',
    'Bangalore': 'Karnataka',
    'Bareilly': 'Uttar Pradesh',
    'Barwani': 'Madhya Pradesh',
    'Bathalapalli': 'Andhra Pradesh',
    'Belagavi': 'Karnataka',
    'Belpahar': 'Odisha',
    'Beohari': 'Madhya Pradesh',
    'Berchha': 'Madhya Pradesh',
    'Betul': 'Madhya Pradesh',
    'Bhopal': 'Madhya Pradesh',
    'Bhubaneswar': 'Odisha',
    'Bikshandarkoil': 'Tamil Nadu',
    'Bilaspur': 'Chhattisgarh',
    'Brahmapur': 'Odisha',
    'Chandrasekharprasad': 'Odisha',
    'Chapda': 'Madhya Pradesh',
    'Chennai': 'Tamil Nadu',
    'Chhindwara': 'Madhya Pradesh',
    'Chhuikhadan': 'Chhattisgarh',
    'Chittoor': 'Andhra Pradesh',
    'Chowdavaram': 'Andhra Pradesh',
    'Coimbatore': 'Tamil Nadu',
    'Cuttack': 'Odisha',
    'Dabra': 'Madhya Pradesh',
    'Damalcheruvu': 'Andhra Pradesh',
    'Damoh': 'Madhya Pradesh',
    'Dharwad': 'Karnataka',
    'Dongargarh': 'Chhattisgarh',
    'Erode': 'Tamil Nadu',
    'Fatehpur': 'Uttar Pradesh',
    'GCF Jabalpur': 'Madhya Pradesh',
    'Ghaziabad': 'Uttar Pradesh',
    'Ghughari': 'Madhya Pradesh',
    'Gopalgoan': 'Maharashtra',
    'Gundur': 'Andhra Pradesh',
    'Guntur': 'Andhra Pradesh',
    'Gurugram': 'Haryana',
    'Hanuman Junction': 'Andhra Pradesh',
    'Hosur': 'Tamil Nadu',
    'Hubli': 'Karnataka',
    'Inagalur': 'Tamil Nadu',
    'Indore': 'Madhya Pradesh',
    'Ingoriya': 'Madhya Pradesh',
    'Itarsi': 'Madhya Pradesh',
    'Jabalpur': 'Madhya Pradesh',
    'Jhansi': 'Uttar Pradesh',
    'Jharsuguda': 'Odisha',
    'Kabrai': 'Uttar Pradesh',
    'Kacchi mohalla mahamaya ward': 'Madhya Pradesh',
    'Kalapatti': 'Tamil Nadu',
    'Kallakurichi': 'Tamil Nadu',
    'Kanakkam Palayam Pirivu': 'Tamil Nadu',
    'Kangeyam': 'Tamil Nadu',
    'Kanpur': 'Uttar Pradesh',
    'Karur': 'Tamil Nadu',
    'Katni': 'Madhya Pradesh',
    'Keelapatti Rasiyamangalam': 'Tamil Nadu',
    'Keolari': 'Madhya Pradesh',
    'Ketka Road Manpur Manpur Chowk Manpur': 'Madhya Pradesh',
    'Khandwa': 'Madhya Pradesh',
    'Khargone': 'Madhya Pradesh',
    'Koduru': 'Andhra Pradesh',
    'Kondapalli': 'Andhra Pradesh',
    'Krishnagiri': 'Tamil Nadu',
    'Kurnool': 'Andhra Pradesh',
    'Kusmaniya': 'Madhya Pradesh',
    'Kutteripattu': 'Tamil Nadu',
    'Lohta': 'Uttar Pradesh',
    'Lucknow': 'Uttar Pradesh',
    'Madakalavaripalle': 'Andhra Pradesh',
    'Madurai': 'Tamil Nadu',
    'Manavadi': 'Tamil Nadu',
    'Mandla': 'Madhya Pradesh',
    'Mangalagiri': 'Andhra Pradesh',
    'Markapur': 'Andhra Pradesh',
    'Masanganj': 'Madhya Pradesh',
    'Matasula Bhuriya': 'Madhya Pradesh',
    'Mathpurena': 'Madhya Pradesh',
    'Multai': 'Madhya Pradesh',
    'Mysore': 'Karnataka',
    'Nagari': 'Andhra Pradesh',
    'Namakkal': 'Tamil Nadu',
    'Narasannapeta': 'Andhra Pradesh',
    'Narmadapuram': 'Madhya Pradesh',
    'New Adaresh Colony': 'Madhya Pradesh',
    'Noida': 'Uttar Pradesh',
    'Ongole': 'Andhra Pradesh',
    'Palamaner': 'Andhra Pradesh',
    'Pathapatnam': 'Andhra Pradesh',
    'Pattukkottai': 'Tamil Nadu',
    'Perambalur': 'Tamil Nadu',
    'Periyakulam': 'Tamil Nadu',
    'Piduguralla': 'Andhra Pradesh',
    'Pollachi': 'Tamil Nadu',
    'Puducherry': 'Puducherry',
    'Pukhrayan': 'Uttar Pradesh',
    'Punganur': 'Andhra Pradesh',
    'Puthagaram': 'Tamil Nadu',
    'Pykara': 'Tamil Nadu',
    'RK Rice Mill Tiruchengode road': 'Tamil Nadu',
    'ROAD MEENAKSHINAYAKKANPATTI STREET': 'Tamil Nadu',
    'Raigarh': 'Chhattisgarh',
    'Raipur': 'Chhattisgarh',
    'Rairangpur': 'Odisha',
    'Rajamahendravaram': 'Andhra Pradesh',
    'Ratlam': 'Madhya Pradesh',
    'Rayachoty': 'Andhra Pradesh',
    'Rewa': 'Madhya Pradesh',
    'Robertsganj': 'Uttar Pradesh',
    'Rourkela': 'Odisha',
    'Sagar': 'Madhya Pradesh',
    'Salem': 'Tamil Nadu',
    'Saloni': 'Madhya Pradesh',
    'Sambalpur': 'Odisha',
    'Santhanathapuram': 'Tamil Nadu',
    'Sarangpur': 'Madhya Pradesh',
    'Sathyamangalam': 'Tamil Nadu',
    'Satna': 'Madhya Pradesh',
    'Sattenapalle': 'Andhra Pradesh',
    'Sehore': 'Madhya Pradesh',
    'Seoni': 'Madhya Pradesh',
    'Seoni Malwa': 'Madhya Pradesh',
    'Shahdol': 'Madhya Pradesh',
    'Sikandar Khedi': 'Madhya Pradesh',
    'Singanallur': 'Tamil Nadu',
    'Singori': 'Madhya Pradesh',
    'Sipat': 'Chhattisgarh',
    'Sitapur': 'Uttar Pradesh',
    'Sundergarh': 'Odisha',
    'Tadepalligudem': 'Andhra Pradesh',
    'Talpur': 'Madhya Pradesh',
    'Temra': 'Madhya Pradesh',
    'Thanjavur': 'Tamil Nadu',
    'Thendal Nagar': 'Tamil Nadu',
    'Thevaiyur South': 'Tamil Nadu',
    'Thuraiyur': 'Tamil Nadu',
    'Tikrapara': 'Odisha',
    'Tilda Newra': 'Chhattisgarh',
    'Tiruchengode': 'Tamil Nadu',
    'Tiruchirappalli': 'Tamil Nadu',
    'Tirupati': 'Andhra Pradesh',
    'Tiruvannamalai': 'Tamil Nadu',
    'Tiruvuru': 'Andhra Pradesh',
    'Ujjain': 'Madhya Pradesh',
    'Utai': 'Madhya Pradesh',
    'Vadakadu': 'Tamil Nadu',
    'Vadakkuvalliyur': 'Tamil Nadu',
    'Varanasi': 'Uttar Pradesh',
    'Vellore': 'Tamil Nadu',
    'Vidisha': 'Madhya Pradesh',
    'Vijayawada': 'Andhra Pradesh',
    'Visakhapatnam': 'Andhra Pradesh',
    'Vizianagaram': 'Andhra Pradesh',
    'Waidhan': 'Madhya Pradesh',
    'seoni': 'Madhya Pradesh',
    'thurayur main road ezhilagam complex': 'Tamil Nadu'
}

created_count = 0
skipped_count = 0
existing_cities = set(City.objects.values_list('name', flat=True))

print("Populating cities...")
print("=" * 50)

for city_name, state in cities_with_states.items():
    try:
        city, created = City.objects.get_or_create(name=city_name)
        # Update state if it's different or empty
        if city.state != state:
            city.state = state
            city.save()
            if not created:
                print(f"✓ Updated state: {city_name} -> {state}")
        
        if created:
            print(f"✓ Created: {city_name} ({state})")
            created_count += 1
        else:
            if city.state == state:
                print(f"⚠ Skipped (already exists): {city_name}")
            skipped_count += 1
    except Exception as e:
        # Handle slug conflict by generating unique slug
        base_slug = slugify(city_name)
        slug = base_slug
        counter = 1
        while City.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        city = City.objects.create(name=city_name, slug=slug, state=state)
        print(f"✓ Created (with unique slug): {city_name} ({state})")
        created_count += 1

print("\n" + "=" * 50)
print("Summary:")
print(f"  Created: {created_count} cities")
print(f"  Skipped: {skipped_count} cities (already existed)")
print(f"  Total: {created_count + skipped_count} cities processed")
print("=" * 50)
