#!/usr/bin/env python
"""
Complete Database Population Script
Run this inside Django shell: python manage.py shell < complete_population.py
"""

import os
from datetime import datetime

print("Starting complete database population...")
print("=" * 70)

# Import all data
exec(open('db_populated.py').read())

# Import models - safely import only what exists
from django.contrib.auth import get_user_model

# Try to import each model, skip if it doesn't exist
imported_models = {}

User = get_user_model()

model_names = [
    'Blog', 'Booking', 'BookingPayment', 'City', 'Community', 'CommunityComment',
    'CommunityLike', 'CommunityMember', 'CommunityPost', 'Enquiry', 'EquipmentInquiry',
    'FavoriteVendor', 'ForumCategory', 'ForumPost', 'ForumTag', 'ForumThread',
    'ForumThreadService', 'ForumThreadTag', 'ForumVote', 'PlanNotification',
    'Review', 'Sector', 'Service', 'SubService', 'UserProfile', 'Vendor', 'VendorEquipment',
    'VendorGallery', 'VendorPayment', 'VendorPlan', 'VendorService'
]

for model_name in model_names:
    try:
        imported_models[model_name] = __import__('core.models', fromlist=[model_name]).__dict__[model_name]
    except KeyError:
        print(f"⚠ Model {model_name} not found - skipping")
        pass

# Create local references for convenience
Blog = imported_models.get('Blog')
Booking = imported_models.get('Booking')
BookingPayment = imported_models.get('BookingPayment')
City = imported_models.get('City')
Community = imported_models.get('Community')
CommunityComment = imported_models.get('CommunityComment')
CommunityLike = imported_models.get('CommunityLike')
CommunityMember = imported_models.get('CommunityMember')
CommunityPost = imported_models.get('CommunityPost')
Enquiry = imported_models.get('Enquiry')
EquipmentInquiry = imported_models.get('EquipmentInquiry')
FavoriteVendor = imported_models.get('FavoriteVendor')
ForumCategory = imported_models.get('ForumCategory')
ForumPost = imported_models.get('ForumPost')
ForumTag = imported_models.get('ForumTag')
ForumThread = imported_models.get('ForumThread')
ForumThreadService = imported_models.get('ForumThreadService')
ForumThreadTag = imported_models.get('ForumThreadTag')
ForumVote = imported_models.get('ForumVote')
PlanNotification = imported_models.get('PlanNotification')
Review = imported_models.get('Review')
Sector = imported_models.get('Sector')
Service = imported_models.get('Service')
SubService = imported_models.get('SubService')
UserProfile = imported_models.get('UserProfile')
Vendor = imported_models.get('Vendor')
VendorEquipment = imported_models.get('VendorEquipment')
VendorGallery = imported_models.get('VendorGallery')
VendorPayment = imported_models.get('VendorPayment')
VendorPlan = imported_models.get('VendorPlan')
VendorService = imported_models.get('VendorService')

# Counter for tracking inserts
insert_count = {}

def safe_insert(model, data_list, model_name):
    """Safely insert data using get_or_create"""
    count = 0
    errors = 0
    
    if not data_list:
        return 0, 0
    
    for data in data_list:
        try:
            # Extract id for get_or_create
            if 'id' in data:
                obj_id = data['id']
                defaults = {k: v for k, v in data.items() if k != 'id'}
                obj, created = model.objects.get_or_create(id=obj_id, defaults=defaults)
            else:
                # For models without explicit id
                obj = model.objects.create(**data)
                created = True
            
            if created:
                count += 1
        except Exception as e:
            errors += 1
            if errors <= 3:  # Only print first 3 errors
                print(f"  ⚠ Error in {model_name}: {str(e)[:60]}")
    
    return count, errors


def collect_auth_user_ids():
    """Collect user IDs referenced by exported tables."""
    auth_id_keys = {'user_id', 'author_id', 'customer_id', 'created_by_id'}
    ids = set()

    for name, value in globals().items():
        if name.startswith('data_core_') and isinstance(value, list):
            for row in value:
                if isinstance(row, dict):
                    for key in auth_id_keys.intersection(row.keys()):
                        ids.add(row[key])

    return {user_id for user_id in ids if isinstance(user_id, int)}


def ensure_auth_user(user_id):
    """Create a minimal auth user record in the database."""
    if not user_id or User.objects.filter(id=user_id).exists():
        return

    username_field = getattr(User, 'USERNAME_FIELD', 'username')
    field_names = {f.name for f in User._meta.get_fields() if hasattr(f, 'attname')}
    defaults = {}

    if username_field == 'email':
        defaults['email'] = f'user_{user_id}@example.com'
        if 'username' in field_names:
            defaults['username'] = f'user_{user_id}'
    else:
        defaults['username'] = f'user_{user_id}'
        if 'email' in field_names:
            defaults['email'] = f'user_{user_id}@example.com'

    if 'password' in field_names:
        defaults['password'] = ''

    User.objects.update_or_create(id=user_id, defaults=defaults)


def seed_missing_auth_users():
    """Seed missing user records before inserting FK-dependent data."""
    user_ids = collect_auth_user_ids()
    if not user_ids:
        return

    print(f"Seeding {len(user_ids)} missing auth user records...")
    for user_id in sorted(user_ids):
        ensure_auth_user(user_id)


# Seed auth users referenced by exported data before FK-dependent inserts
seed_missing_auth_users()

# List of all data tables
tables_to_insert = [
    (Sector, data_core_sector if 'data_core_sector' in dir() else [], 'Sector'),
    (City, data_core_city if 'data_core_city' in dir() else [], 'City'),
    (Service, data_core_service if 'data_core_service' in dir() else [], 'Service'),
    (SubService, data_core_subservice if 'data_core_subservice' in dir() else [], 'SubService'),
    (UserProfile, data_core_userprofile if 'data_core_userprofile' in dir() else [], 'UserProfile'),
    (Vendor, data_core_vendor if 'data_core_vendor' in dir() else [], 'Vendor'),
    (VendorService, data_core_vendorservice if 'data_core_vendorservice' in dir() else [], 'VendorService'),
    (VendorPlan, data_core_vendorplan if 'data_core_vendorplan' in dir() else [], 'VendorPlan'),
    (VendorPayment, data_core_vendorpayment if 'data_core_vendorpayment' in dir() else [], 'VendorPayment'),
    (VendorEquipment, data_core_vendorequipment if 'data_core_vendorequipment' in dir() else [], 'VendorEquipment'),
    (VendorGallery, data_core_vendorgallery if 'data_core_vendorgallery' in dir() else [], 'VendorGallery'),
    (FavoriteVendor, data_core_favoritevendor if 'data_core_favoritevendor' in dir() else [], 'FavoriteVendor'),
    (Blog, data_core_blog if 'data_core_blog' in dir() else [], 'Blog'),
    (Review, data_core_review if 'data_core_review' in dir() else [], 'Review'),
    (Enquiry, data_core_enquiry if 'data_core_enquiry' in dir() else [], 'Enquiry'),
    (EquipmentInquiry, data_core_equipmentinquiry if 'data_core_equipmentinquiry' in dir() else [], 'EquipmentInquiry'),
    (Community, data_core_community if 'data_core_community' in dir() else [], 'Community'),
    (CommunityMember, data_core_communitymember if 'data_core_communitymember' in dir() else [], 'CommunityMember'),
    (CommunityPost, data_core_communitypost if 'data_core_communitypost' in dir() else [], 'CommunityPost'),
    (CommunityComment, data_core_communitycomment if 'data_core_communitycomment' in dir() else [], 'CommunityComment'),
    (CommunityLike, data_core_communitylike if 'data_core_communitylike' in dir() else [], 'CommunityLike'),
    (ForumCategory, data_core_forumcategory if 'data_core_forumcategory' in dir() else [], 'ForumCategory'),
    (ForumThread, data_core_forumthread if 'data_core_forumthread' in dir() else [], 'ForumThread'),
    (ForumThreadTag, data_core_forumthreadtag if 'data_core_forumthreadtag' in dir() else [], 'ForumThreadTag'),
    (ForumThreadService, data_core_forumthreadservice if 'data_core_forumthreadservice' in dir() else [], 'ForumThreadService'),
    (ForumPost, data_core_forumpost if 'data_core_forumpost' in dir() else [], 'ForumPost'),
    (ForumTag, data_core_forumtag if 'data_core_forumtag' in dir() else [], 'ForumTag'),
    (ForumVote, data_core_forumvote if 'data_core_forumvote' in dir() else [], 'ForumVote'),
    (Booking, data_core_booking if 'data_core_booking' in dir() else [], 'Booking'),
    (BookingPayment, data_core_bookingpayment if 'data_core_bookingpayment' in dir() else [], 'BookingPayment'),
    (PlanNotification, data_core_plannotification if 'data_core_plannotification' in dir() else [], 'PlanNotification'),
]

# Insert all data
total_inserted = 0
total_errors = 0

for model, data_list, name in tables_to_insert:
    if data_list:
        inserted, errors = safe_insert(model, data_list, name)
        if inserted > 0 or errors > 0:
            status = f"✓ {inserted} inserted" if inserted > 0 else "✗ 0 inserted"
            error_msg = f", {errors} errors" if errors > 0 else ""
            print(f"{name:.<50} {status}{error_msg}")
            total_inserted += inserted
            total_errors += errors

print("=" * 70)
print(f"\n✓ POPULATION COMPLETE!")
print(f"Total records inserted: {total_inserted}")
if total_errors > 0:
    print(f"Total errors: {total_errors}")
print("\n✓ Your database is now fully populated with data!")
