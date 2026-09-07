import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borewellmart.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

# Check if admin user exists
admin_user = User.objects.filter(username='admin').first()

if admin_user:
    print(f"Admin user exists: {admin_user.username}")
    
    # Check if user has a profile
    if hasattr(admin_user, 'userprofile'):
        print(f"Current user_type: {admin_user.userprofile.user_type}")
        # Update to admin
        admin_user.userprofile.user_type = 'admin'
        admin_user.userprofile.save()
        print(f"Updated user_type to: {admin_user.userprofile.user_type}")
    else:
        print("No UserProfile found. Creating one...")
        UserProfile.objects.create(
            user=admin_user,
            phone='9876543210',
            user_type='admin'
        )
        print("Created UserProfile with user_type='admin'")
else:
    print("No admin user found. Creating one...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@borewellmart.com',
        password='admin123'
    )
    UserProfile.objects.create(
        user=admin_user,
        phone='9876543210',
        user_type='admin'
    )
    print("Created admin user with UserProfile")

print("\nYou can now login with:")
print("Username: admin")
print("Password: admin123")
print("\nThe admin dashboard link will appear in the navigation bar when logged in as admin.")
