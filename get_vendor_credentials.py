# Extract vendor usernames and passwords from VENDOR_DATA

from db_exported_data import VENDOR_DATA

print("Vendor Credentials:")
print("=" * 60)
print(f"{'Username':<35} {'Password':<15}")
print("=" * 60)

for vendor_data in VENDOR_DATA:
    username = vendor_data['company_name'].lower().replace(' ', '_').replace('-', '_')[:30]
    password = "default123"
    print(f"{username:<35} {password:<15}")

print("=" * 60)
print(f"Total vendors: {len(VENDOR_DATA)}")
print("\nNote: All vendors have the default password 'default123'")
print("You should ask vendors to change their password after first login.")
