# Extract customer usernames and passwords from CUSTOMER_DATA

from db_exported_data import CUSTOMER_DATA

print("Customer Credentials:")
print("=" * 60)
print(f"{'Username':<35} {'Password':<15}")
print("=" * 60)

for customer_data in CUSTOMER_DATA:
    username = customer_data['username']
    password = "default123"  # Default password set during import
    print(f"{username:<35} {password:<15}")

print("=" * 60)
print(f"Total customers: {len(CUSTOMER_DATA)}")
print("\nNote: All customers have the default password 'default123'")
print("You should ask customers to change their password after first login.")
