# Quick Start Guide - Vendor Plan System

## 🎯 What You Got

A complete vendor plan management system with:
- Create plans with custom validity dates (from day X to day Y)
- Automatic expiry notifications (7, 3, 1 day before)
- Plan renewal workflow
- Email notifications
- Admin dashboard
- Vendor dashboard

## 🚀 Getting Started (5 Minutes)

### 1. Access the Vendor Dashboard
```
URL: http://localhost:8000/vendor/plans/
Login with vendor account first
```

### 2. Create Your First Plan
```
Click "Add New Plan"
Fill in:
- Plan Type: Premium Plan
- Plan Name: My Monthly Plan
- Price: ₹999
- Start Date: Today's date
- End Date: 30 days from today
- Description: Plan features
Click "Create Plan"
```

### 3. View Plan Details
```
Click on the plan from the list
See:
- Plan validity (from X to Y date)
- Days until expiry
- Current status (Active/Expired)
- Notifications sent
```

### 4. Test Notifications
```bash
# Open terminal and run:
python manage.py send_plan_notifications

# Output:
# Successfully processed notifications:
# - Notifications created: X
# - Emails sent: Y
```

## 📋 Available URLs

| URL | Purpose |
|-----|---------|
| `/vendor/plans/` | View all your plans |
| `/vendor/plans/create/` | Create new plan |
| `/vendor/plans/<id>/` | View plan details |
| `/vendor/plans/<id>/edit/` | Edit plan |
| `/vendor/plans/<id>/renew/` | Renew expired plan |
| `/vendor/plans/<id>/notifications/` | View notifications |

## 🔧 Admin Dashboard

Access at: `http://localhost:8000/admin/core/vendorplan/`

Features:
- View all vendor plans
- Filter by status/type
- See color-coded status badges
- View days until expiry
- Inline notification viewer

## 📊 Database Info

**VendorPlan Table:**
- Stores plan data
- Tracks: name, price, dates, status
- Links to Vendor

**PlanNotification Table:**
- Stores notification records
- Tracks: type, date sent, delivery status
- Links to VendorPlan

## ⚙️ Daily Automation

To send notifications automatically every day at 9 AM:

**Option 1: Manual Testing**
```bash
python manage.py send_plan_notifications
```

**Option 2: Linux/Mac Cron**
```bash
# Edit crontab
crontab -e

# Add line:
0 9 * * * cd /home/user/borewell && python manage.py send_plan_notifications
```

**Option 3: Windows Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9 AM
4. Set action: Run `python manage.py send_plan_notifications`

## 💾 Email Configuration

For production email sending, update `settings.py`:

```python
# Gmail example
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # NOT your regular password!
DEFAULT_FROM_EMAIL = 'noreply@borewellmart.com'
```

## 🎬 Example Workflow

### Create a Plan
1. Go to `/vendor/plans/create/`
2. Fill form with plan details
3. Plan created with status "Active"

### View the Plan
1. Go to `/vendor/plans/`
2. See plan in table with validity dates
3. Click plan name to view details

### System Sends Notifications
1. Notifications sent automatically or via command
2. 7 days before expiry: "Your plan expires in 7 days"
3. 3 days before expiry: "Your plan expires in 3 days"
4. 1 day before expiry: "Your plan expires tomorrow"
5. On expiry date: "Your plan has expired"

### Renew Plan
1. Plan expires
2. Status changes to "Expired"
3. Click "Renew Plan" button
4. Set new dates
5. New plan created, old marked "Cancelled"

## 🔍 Checking Everything Works

```bash
# 1. Validate Django setup
python manage.py check

# 2. Test notification command
python manage.py send_plan_notifications

# 3. Access vendor dashboard
# http://localhost:8000/vendor/plans/

# 4. Check admin
# http://localhost:8000/admin/core/vendorplan/
```

## 📧 Email Templates

Two email templates included:

**1. Expiry Reminder**
- Subject: "Your Plan Expires in X Days"
- Sent 7, 3, 1 day before expiry
- Includes renewal link

**2. Expiry Alert**
- Subject: "Your Plan Has Expired"
- Sent on expiry date
- Urgent tone with renewal link

## 🐛 Troubleshooting

### Plan Not Showing?
- Check login (must be vendor account)
- Check vendor is linked to user
- Refresh page

### Notifications Not Sending?
- Check plan end_date
- Run: `python manage.py send_plan_notifications`
- Check EMAIL settings in settings.py
- Verify vendor email is set

### Getting Errors?
- Run: `python manage.py check`
- Check database migration: `python manage.py migrate`
- Check templates exist: `templates/vendor_plans.html` etc.

## 📝 Files Created

### Models
- `core/models.py` - VendorPlan, PlanNotification

### Views
- `core/views.py` - 6 plan management views

### URLs
- `core/urls.py` - 6 new URL patterns

### Templates
- `templates/vendor_plans.html`
- `templates/plan_detail.html`
- `templates/create_plan.html`
- `templates/edit_plan.html`
- `templates/renew_plan.html`
- `templates/plan_notifications.html`
- `templates/emails/plan_expiry_notification.html`
- `templates/emails/plan_expired_notification.html`

### Management Command
- `core/management/commands/send_plan_notifications.py`

### Migration
- `core/migrations/0015_vendorplan_plannotification.py`

## 🔐 Important Notes

- Only vendors can see their own plans
- Only name and description can be edited
- To change dates/price, must renew plan
- Notifications are sent once per date
- Admin can view all plans across all vendors
- Emails require proper EMAIL configuration

## ✅ What's Ready to Use

✓ Database models and migrations applied
✓ All views created and URL routes added
✓ Templates created and tested
✓ Admin interface configured
✓ Management command ready
✓ Email templates created
✓ Vendor dashboard functional
✓ Plan renewal workflow complete

## 🎁 Bonus Features

- Color-coded status badges
- Days until expiry display
- Notification history timeline
- Email delivery tracking
- Plan type categorization
- Bulk vendor operations
- Admin filters and search

## 📞 Support

Issues? Check:
1. PLAN_SYSTEM_README.md for detailed docs
2. Django check: `python manage.py check`
3. Admin dashboard for data
4. Database migrations: `python manage.py migrate --list`

---

**Ready to use!** Just test it out at `/vendor/plans/`
