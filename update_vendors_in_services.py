#!/usr/bin/env python
"""
Update vendors in services_data.json with the new vendor mapping
"""

import json

# Load the services data
with open('core/management/commands/services_data.json', 'r', encoding='utf-8') as f:
    services_data = json.load(f)

# Load the updated vendors data
with open('core/management/commands/updated_vendors_data.json', 'r', encoding='utf-8') as f:
    vendors_data = json.load(f)

# Update the vendors section
services_data['vendors'] = vendors_data['vendors']

# Save back to services_data.json
with open('core/management/commands/services_data.json', 'w', encoding='utf-8') as f:
    json.dump(services_data, f, indent=2, ensure_ascii=False)

print(f"Updated services_data.json with {len(vendors_data['vendors'])} vendors")
print("Vendors have been successfully integrated!")
