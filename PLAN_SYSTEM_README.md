# Vendor Plan & Expiry Notification System - Implementation Guide

## Overview
This system allows vendors to create subscription plans with validity dates (from day X to day Y) and automatically sends expiry notifications 7, 3, and 1 day before the plan expires.

## What's Been Implemented

### 1. Database Models
- **VendorPlan** - Stores vendor subscription plans with custom start/end dates
- **PlanNotification** - Tracks all notifications sent to vendors

### 2. Django Admin Interface
- Full CRUD operations for plans
- Color-coded status badges (Active/Expired)
- Days until expiry display
- Inline notification viewer
- Delivery status tracking (email/SMS)

### 3. Vendor Dashboard
- View all their plans with validity periods
- Create new plans
- Edit plan details (name & description)
- Renew expired or expiring plans
- View complete notification history

### 4. Automated Notification System
- Management command: `send_plan_notifications`
- Sends notifications at configurable intervals (7, 3, 1 day before expiry)
- Email delivery tracking
- Automatic plan status updates

### 5. Email Notifications
- Professional HTML email templates
- Plan expiry reminder (7, 3, 1 day before)
- Plan expired urgent alert
- Renewal links included

## Files Created/Modified

### New Models
- `/core/models.py` - Added `VendorPlan` and `PlanNotification` models

### New Management Command
- `/core/management/commands/send_plan_notifications.py` - Sends notifications

### New Views
- `/core/views.py` - Added plan management views (6 new views)

### New URL Routes
- `/core/urls.py` - Added 6 new URL patterns

### New Templates
- `/templates/vendor_plans.html` - Plan list dashboard
- `/templates/plan_detail.html` - View plan details and notifications
- `/templates/create_plan.html` - Create new plan form
- `/templates/edit_plan.html` - Edit plan details
- `/templates/renew_plan.html` - Renew expired plan
- `/templates/plan_notifications.html` - Notification history
- `/templates/emails/plan_expiry_notification.html` - Email template
- `/templates/emails/plan_expired_notification.html` - Expiry alert template

### Database Migration
- `/core/migrations/0015_vendorplan_plannotification.py` - Created automatically

## How It Works

### Creating a Plan
1. Vendor goes to `/vendor/plans/create/`
2. Fills in: Plan Type, Name, Price, Start Date, End Date, Description
3. Plan is stored in database
4. Status automatically set to 'active' or 'expired' based on dates

### Automated Notifications
1. Run: `python manage.py send_plan_notifications`
2. For each active plan:
   - Check days until expiry
   - If it's 7, 3, or 1 day before expiry → create notification
   - Send email to vendor
   - Track delivery status
3. For expired plans:
   - Send urgent "plan expired" email
   - Update status to 'expired'

### Renewing a Plan
1. Vendor goes to `/vendor/plans/<id>/renew/`
2. Specifies new start and end dates
3. New plan is created based on old one
4. Old plan marked as 'cancelled'
5. Notifications restart for new plan

### Viewing Notifications
1. Vendor can view all notifications at `/vendor/plans/<id>/notifications/`
2. Timeline view shows:
   - Notification type and date
   - Message content
   - Delivery status (email sent, SMS pending, etc.)
   - When notification was sent

## URL Routes

```
/vendor/plans/                              - List all plans
/vendor/plans/create/                       - Create new plan
/vendor/plans/<id>/                         - View plan details
/vendor/plans/<id>/edit/                    - Edit plan
/vendor/plans/<id>/renew/                   - Renew plan
/vendor/plans/<id>/notifications/           - View notifications
```

## Admin Routes

```
Django Admin → VendorPlan                   - Manage all plans
Django Admin → PlanNotification            - View notifications
```

## Database Fields

### VendorPlan
| Field | Type | Description |
|-------|------|-------------|
| id | pk | Primary key |
| vendor | ForeignKey | Link to Vendor |
| plan_type | CharField | basic/premium/professional |
| plan_name | CharField | Custom plan name |
| price | DecimalField | Subscription price |
| start_date | DateField | When plan becomes active |
| end_date | DateField | When plan expires |
| status | CharField | active/expired/cancelled |
| description | TextField | Plan features/benefits |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

### PlanNotification
| Field | Type | Description |
|-------|------|-------------|
| id | pk | Primary key |
| plan | ForeignKey | Link to VendorPlan |
| notification_type | CharField | 7_day_before/3_day_before/1_day_before/expired |
| notification_date | DateField | Date notification was scheduled |
| is_sent | Boolean | Whether notification sent |
| email_sent | Boolean | Email delivery status |
| sms_sent | Boolean | SMS delivery status |
| notification_text | TextField | Message content |
| sent_at | DateTimeField | When notification sent |

## Key Features

✅ **Custom Date Ranges** - Each plan can have any start/end date
✅ **Automatic Status** - Plan status updates automatically based on current date
✅ **Multiple Reminders** - Notifications at 7, 3, and 1 day before expiry
✅ **Email Delivery** - Beautiful HTML emails with renewal links
✅ **Notification History** - View all notifications sent for each plan
✅ **Admin Dashboard** - Full management in Django admin
✅ **Vendor Dashboard** - Self-service plan management
✅ **Renewal Workflow** - Easy plan renewal process
✅ **Status Tracking** - Know which emails were delivered

## Setup Instructions

### Step 1: Apply Migrations (Already Done)
```bash
python manage.py migrate core
```

### Step 2: Configure Email (In settings.py)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@borewellmart.com'
```

### Step 3: Set Up Scheduled Task
Run the notification command daily:

**Linux/Mac (Crontab):**
```bash
0 9 * * * cd /path/to/project && python manage.py send_plan_notifications
```

**Windows (Task Scheduler):**
```
Create scheduled task to run:
python c:\path\to\manage.py send_plan_notifications
```

**Or use Celery:**
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-plan-notifications': {
        'task': 'core.tasks.send_plan_notifications_task',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
}
```

### Step 4: Test Locally
```bash
python manage.py send_plan_notifications
```

## Example Usage

### Creating a Test Plan
1. Go to Django admin
2. Click "Add VendorPlan"
3. Fill in:
   - Vendor: Select your vendor
   - Plan Type: Premium Plan
   - Plan Name: "Monthly Premium"
   - Price: 1000
   - Start Date: 2024-06-17
   - End Date: 2024-07-17
   - Description: "Full access to all features"
4. Save

### Viewing Plans
1. Go to `/vendor/plans/`
2. See all plans with:
   - Validity period
   - Days until expiry
   - Status badge
   - Action buttons

### Triggering Notifications Manually
```bash
python manage.py send_plan_notifications
```

Output:
```
Starting plan notification process...
Successfully processed notifications:
- Notifications created: 2
- Emails sent: 2
```

## Troubleshooting

### Email Not Sending?
1. Check EMAIL settings in settings.py
2. Run: `python manage.py send_mail_test`
3. Check plan end_date is close enough
4. Verify vendor has valid email

### Notifications Not Appearing?
1. Check PlanNotification model in admin
2. Verify plan status is 'active'
3. Check if notification already exists for that date
4. Ensure end_date is correct

### Migration Issues?
```bash
python manage.py migrate core
python manage.py migrate core --fake-initial  # if conflicts
```

## Query Examples

### Get all active plans for a vendor
```python
from core.models import VendorPlan, Vendor

vendor = Vendor.objects.get(id=1)
active_plans = VendorPlan.objects.filter(vendor=vendor, status='active')
```

### Get notifications for a plan
```python
from core.models import VendorNotification

notifications = PlanNotification.objects.filter(plan_id=1).order_by('-sent_at')
```

### Check days until expiry
```python
plan = VendorPlan.objects.get(id=1)
days_left = plan.days_until_expiry()
print(f"Days until expiry: {days_left}")
```

### Manually update plan status
```python
plan = VendorPlan.objects.get(id=1)
plan.update_status()  # Updates based on current date
```

## Performance Considerations

- Plans are checked daily, not on every request
- Notifications are cached to prevent duplicates
- Use database indexes on vendor_id and status
- Consider batch processing for many plans

## Future Enhancements

- SMS notifications
- SMS renewal reminders
- Plan upgrade/downgrade
- Recurring automatic renewal
- Payment gateway integration
- Analytics dashboard
- Custom notification schedules

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review admin logs in `/logs/` directory
3. Run `python manage.py check` to validate setup
4. Check email configuration in settings
