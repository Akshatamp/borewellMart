# Vendor Verification Access Control System

## Overview

Only **verified vendors** (verified by admin) can access all features including:
- Dashboard
- Bookings
- Enquiries  
- Services
- Plans
- Gallery
- Payment

## Verification Status Levels

### 1. ✅ Verified (Green Status)
- Full access to all features
- Can create and manage plans
- Can add/edit services
- Can upload gallery images
- Can respond to enquiries and bookings

### 2. ⏳ Pending (Yellow Status)
- Awaiting admin verification
- Redirected to payment page with warning message
- Cannot access dashboard features
- Message: "Your account is pending admin verification. Please wait for approval."

### 3. ⛔ Suspended (Red Status)
- Account blocked by admin
- Redirected with error message
- Cannot access any features
- Message: "Your account has been suspended. Please contact admin."

## Verification Check Implementation

### Protected Views (6 plan views)

All plan views now include verification check:

```python
# Check if vendor is verified
is_verified, redirect_url = check_vendor_verification(vendor)
if not is_verified:
    if vendor.verification_status == 'pending':
        messages.warning(request, 'Your account is pending admin verification...')
    elif vendor.verification_status == 'suspended':
        messages.error(request, 'Your account has been suspended...')
    return redirect('vendor_payment_page')
```

**Protected Plan Views:**
1. `vendor_plans()` - List all plans
2. `plan_detail()` - View plan details
3. `create_plan()` - Create new plan
4. `edit_plan()` - Edit plan
5. `renew_plan()` - Renew plan
6. `plan_notifications()` - View notifications

### Other Protected Vendor Views (Already had checks)

- `vendor_dashboard()` - Main dashboard
- `vendor_bookings()` - Manage bookings
- `vendor_enquiries()` - View enquiries
- `vendor_services()` - View services
- `vendor_service_add()` - Add new service
- `vendor_service_edit()` - Edit service
- `vendor_profile_edit()` - Edit profile
- `vendor_gallery_add()` - Add gallery images

## Sidebar Updates

### Verification Status Badge
- Added at bottom of sidebar
- Shows real-time verification status with visual indicator:
  - **Green dot** - Verified ✓
  - **Yellow pulsing dot** - Pending
  - **Red dot** - Suspended

### New Plans Menu
- Added "PLANS" section to sidebar
- "My Plans" link for accessing plan management
- Only visible after vendor login

## User Experience Flow

### For Verified Vendors
```
Login → Full Dashboard Access → All Features Available
                               ├── View Plans
                               ├── Create Plans
                               ├── Manage Services
                               ├── View Bookings
                               ├── Respond Enquiries
                               ├── Upload Gallery
                               └── Manage Profile
```

### For Pending Vendors
```
Login → Warning: "Pending Verification" → Redirect to Payment
                                            ├── Cannot Access Plans
                                            ├── Cannot Add Services
                                            ├── Cannot Upload Gallery
                                            └── Cannot Manage Profile
```

### For Suspended Vendors
```
Login → Error: "Account Suspended" → Redirect to Home
                                      All Features Blocked
```

## Admin Verification

### How to Verify a Vendor
1. Go to Django Admin
2. Click "Vendor" in core app
3. Select vendor with status "pending"
4. Change status to "verified"
5. Save
6. Vendor gets full access immediately

### Admin Commands
```python
# Approve a vendor
vendor = Vendor.objects.get(id=1)
vendor.verification_status = 'verified'
vendor.save()

# Suspend a vendor
vendor = Vendor.objects.get(id=1)
vendor.verification_status = 'suspended'
vendor.save()
```

## Messages Displayed

### Pending Message
```
⚠️ Your account is pending admin verification. Please wait for approval.
(Shown when accessing any protected feature)
```

### Suspended Message
```
❌ Your account has been suspended. Please contact admin.
(Shown when accessing any protected feature)
```

### Feature-Specific Messages

**For Plans:** "Your account is pending admin verification. Please wait for approval to access plans."

**For Services:** "Your account is pending admin verification. Please wait for approval."

**For Gallery:** "Your account is pending admin verification. Please wait for approval to manage your gallery."

**For Profile:** "Your account is pending admin verification. Please wait for approval to edit your profile."

## Sidebar Navigation

The vendor sidebar now shows:

```
VENDOR PANEL
├─ MAIN
│  ├─ Dashboard
│  ├─ Bookings
│  └─ Enquiry
├─ SERVICE
│  ├─ Add Service
│  └─ View Services
├─ PLANS (NEW)
│  └─ My Plans
├─ ACCOUNT
│  ├─ Payment
│  └─ Logout
└─ STATUS (Dynamic)
   └─ Verified / Pending / Suspended
```

## Database Field

Verification status is stored in the Vendor model:

```python
verification_status = CharField(
    max_length=20,
    choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('suspended', 'Suspended'),
    ],
    default='pending'
)
```

## Status Change Flow

### When Vendor Registers
```
Status: pending (default)
```

### After Admin Approves
```python
vendor.verification_status = 'verified'
vendor.save()
```
- Vendor gets immediate access to all features
- No need to login again (checks happen at view level)

### When Admin Suspends
```python
vendor.verification_status = 'suspended'
vendor.save()
```
- Vendor immediately loses access
- Redirected with error message on next page access

## Testing Verification

### Test 1: Create Test Vendor
1. Register new vendor account
2. Status should be "pending"
3. Try to access /vendor/plans/ → Should be redirected

### Test 2: Verify in Admin
1. Go to `/admin/core/vendor/`
2. Find the test vendor
3. Change status to "verified"
4. Save
5. Logout and login as vendor
6. Should have full access

### Test 3: Suspend Account
1. In admin, find verified vendor
2. Change status to "suspended"
3. Vendor should be redirected on next access
4. Error message displayed

## Related Views

All these views have verification checks:

| View | URL | Status | Message |
|------|-----|--------|---------|
| vendor_plans | /vendor/plans/ | ✅ | "...to access plans." |
| plan_detail | /vendor/plans/<id>/ | ✅ | "...to access plans." |
| create_plan | /vendor/plans/create/ | ✅ | "...to create plans." |
| edit_plan | /vendor/plans/<id>/edit/ | ✅ | "...to edit plans." |
| renew_plan | /vendor/plans/<id>/renew/ | ✅ | "...to renew plans." |
| plan_notifications | /vendor/plans/<id>/notifications/ | ✅ | "...to view notifications." |

## Summary

✅ **Only verified vendors have access to all features**
✅ **Real-time status checks on every view**
✅ **Clear messages for pending and suspended accounts**
✅ **Visual status indicator in sidebar**
✅ **Secure redirect to safe pages**
✅ **Admin can control access with one click**

Vendors must be verified by admin to use plans, services, and other features!
