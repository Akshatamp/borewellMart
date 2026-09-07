"""
BorewellMart - Complete Project Documentation
=============================================

A Django-based two-sided marketplace connecting customers with
borewell and agriculture service vendors.

Author: BorewellMart Team
Version: 1.0.0
License: Proprietary
"""

# =============================================================================
# PROJECT OVERVIEW
# =============================================================================

PROJECT_NAME = "BorewellMart"
PROJECT_TYPE = "Two-sided Marketplace Web Application"
FRAMEWORK = "Django 5.2.15"
LANGUAGE = "Python 3.10+"
DATABASE = "SQLite (configurable to PostgreSQL)"
PAYMENT_GATEWAY = "Razorpay"

PROJECT_DESCRIPTION = """
BorewellMart is a digital marketplace platform that connects customers
who need borewell and agricultural services with verified local vendors
who provide those services.

Business Model:
- Vendors pay ₹999 registration fee to join the platform
- Customers can browse, compare, and book services for free
- Admin approves vendors and manages all platform content
"""

# =============================================================================
# USER TYPES & ROLES
# =============================================================================

USER_TYPES = {
    "customer": {
        "description": "End users who need borewell/agriculture services",
        "features": [
            "Browse services by city/category",
            "Search for vendors",
            "Send enquiries to vendors",
            "Book services online",
            "Leave reviews and ratings",
            "Save favorite vendors",
            "Track booking status"
        ]
    },
    "vendor": {
        "description": "Service providers who offer borewell/agriculture services",
        "features": [
            "Register with payment (₹999)",
            "Create detailed profile",
            "List services with pricing",
            "Upload gallery images",
            "Receive and respond to enquiries",
            "Manage bookings",
            "Build reputation through reviews"
        ]
    },
    "admin": {
        "description": "Platform administrators",
        "features": [
            "Approve/reject vendors",
            "Manage all content (cities, services, blogs)",
            "View analytics and statistics",
            "Handle payments",
            "Bulk vendor registration",
            "Suspend problematic vendors"
        ]
    }
}

# =============================================================================
# DATABASE MODELS
# =============================================================================

MODELS = {
    "City": {
        "fields": [
            "name (CharField, unique=True)",
            "image (ImageField, optional)",
            "description (TextField, optional)",
            "latitude (DecimalField, optional)",
            "longitude (DecimalField, optional)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "properties": [
            "vendor_count - Count of vendors in this city",
            "service_count - Count of unique services offered",
            "get_nearby_cities(limit=5) - Find nearby cities using Haversine formula"
        ],
        "purpose": "Geographic organization of vendors and services"
    },

    "ServiceCategory": {
        "fields": [
            "id (CharField, primary_key=True)",
            "name (CharField)",
            "description (TextField)",
            "icon (CharField, optional)",
            "image (ImageField, optional)",
            "order (PositiveIntegerField, default=0)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "examples": ["Borewell", "Agriculture"],
        "purpose": "Top-level service categorization"
    },

    "ServiceSubcategory": {
        "fields": [
            "category (ForeignKey to ServiceCategory)",
            "id (CharField, primary_key=True)",
            "name (CharField)",
            "description (TextField)",
            "icon (CharField, optional)",
            "image (ImageField, optional)",
            "order (PositiveIntegerField, default=0)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "examples": ["Borewell Drilling", "Pump Repair", "Irrigation Systems"],
        "purpose": "Second-level service categorization"
    },

    "Service": {
        "fields": [
            "subcategory (ForeignKey to ServiceSubcategory)",
            "id (CharField, primary_key=True)",
            "name (CharField)",
            "description (TextField)",
            "features (JSONField, list of features)",
            "starting_price (DecimalField, optional)",
            "per_feet_amount (DecimalField, optional) - Rate per feet for drilling",
            "image (ImageField, optional)",
            "popular (BooleanField, default=False)",
            "order (PositiveIntegerField, default=0)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "properties": [
            "category - Returns parent category through subcategory"
        ],
        "purpose": "Individual services that vendors can offer"
    },

    "UserProfile": {
        "fields": [
            "user (OneToOne to User)",
            "phone (CharField, with validation)",
            "user_type (CharField, choices: customer/vendor)",
            "city (ForeignKey to City, optional)",
            "address (TextField, optional)",
            "profile_image (ImageField, optional)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "purpose": "Extended user information with role classification"
    },

    "Vendor": {
        "fields": [
            "user (OneToOne to User)",
            "company_name (CharField)",
            "logo (ImageField, optional)",
            "cover_image (ImageField, optional)",
            "city (ForeignKey to City)",
            "experience (PositiveIntegerField) - Years",
            "phone (CharField)",
            "email (EmailField)",
            "address (TextField)",
            "license_number (CharField, optional)",
            "certifications (TextField, optional)",
            "rating (DecimalField, default=0.0)",
            "verification_status (CharField, choices: pending/verified/suspended)",
            "is_emergency_available (BooleanField, default=False)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "properties": [
            "services_count - Count of offered services",
            "bookings_count - Total bookings received",
            "completed_bookings_count - Count of completed bookings",
            "update_rating() - Recalculate rating from reviews"
        ],
        "purpose": "Vendor profile with verification and rating system"
    },

    "VendorPayment": {
        "fields": [
            "vendor (OneToOne to Vendor)",
            "amount (DecimalField, default=999.00)",
            "status (CharField, choices: pending/processing/completed/failed/refunded)",
            "payment_method (CharField, choices: razorpay/stripe/bank_transfer/upi/other)",
            "transaction_id (CharField, optional)",
            "razorpay_order_id (CharField, optional)",
            "payment_date (DateTimeField, optional)",
            "paid_amount (DecimalField, optional)",
            "gateway_response (JSONField, optional)",
            "notes (TextField, optional)",
            "created_at (DateTimeField, auto_now_add=True)",
            "updated_at (DateTimeField, auto_now=True)"
        ],
        "methods": [
            "mark_completed(transaction_id, paid_amount, gateway_response) - Mark as complete"
        ],
        "purpose": "Track vendor registration payments"
    },

    "VendorService": {
        "fields": [
            "vendor (ForeignKey to Vendor)",
            "service (ForeignKey to Service)",
            "price (DecimalField) - Starting price",
            "description (TextField, optional)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "constraints": [
            "unique_together: ['vendor', 'service']"
        ],
        "purpose": "Services offered by specific vendors with custom pricing"
    },

    "Booking": {
        "fields": [
            "customer (ForeignKey to User)",
            "vendor (ForeignKey to Vendor)",
            "service (ForeignKey to Service)",
            "enquiry (ForeignKey to Enquiry, optional)",
            "date (DateField)",
            "time (TimeField)",
            "address (TextField)",
            "description (TextField, optional)",
            "status (CharField, choices: pending/accepted/in_progress/completed/cancelled)",
            "is_emergency (BooleanField, default=False)",
            "created_at (DateTimeField, auto_now_add=True)",
            "updated_at (DateTimeField, auto_now=True)"
        ],
        "constraints": [
            "unique_together: ['customer', 'vendor', 'service', 'date', 'time']"
        ],
        "purpose": "Service bookings between customers and vendors"
    },

    "Enquiry": {
        "fields": [
            "customer (ForeignKey to User)",
            "vendor (ForeignKey to Vendor)",
            "service (ForeignKey to Service)",
            "message (TextField)",
            "status (CharField, choices: pending/responded/closed)",
            "vendor_response (TextField, optional)",
            "quoted_amount (DecimalField, optional)",
            "created_at (DateTimeField, auto_now_add=True)",
            "updated_at (DateTimeField, auto_now=True)"
        ],
        "ordering": ["-created_at"],
        "purpose": "Pre-booking enquiries for detailed quotes"
    },

    "Review": {
        "fields": [
            "customer (ForeignKey to User)",
            "vendor (ForeignKey to Vendor)",
            "booking (ForeignKey to Booking, optional)",
            "rating (PositiveIntegerField, choices: 1-5)",
            "comment (TextField)",
            "customer_image (ImageField, optional)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "constraints": [
            "unique_together: ['customer', 'vendor']"
        ],
        "purpose": "Customer reviews for vendors"
    },

    "VendorGallery": {
        "fields": [
            "vendor (ForeignKey to Vendor)",
            "image (ImageField)",
            "caption (CharField, optional)",
            "image_type (CharField, choices: drilling_machine/previous_work/team/other)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "purpose": "Vendor portfolio images"
    },

    "FavoriteVendor": {
        "fields": [
            "customer (ForeignKey to User)",
            "vendor (ForeignKey to Vendor)",
            "created_at (DateTimeField, auto_now_add=True)"
        ],
        "constraints": [
            "unique_together: ['customer', 'vendor']"
        ],
        "purpose": "Customer's saved vendors"
    },

    "Blog": {
        "fields": [
            "title (CharField)",
            "slug (SlugField, unique=True)",
            "image (ImageField, optional)",
            "content (TextField)",
            "category (CharField, choices: borewell_maintenance/water_conservation/pump_maintenance/government_schemes)",
            "author (ForeignKey to User)",
            "created_at (DateTimeField, auto_now_add=True)",
            "updated_at (DateTimeField, auto_now=True)"
        ],
        "purpose": "Content management for SEO and user education"
    }
}

# =============================================================================
# URL ROUTES STRUCTURE
# =============================================================================

URL_STRUCTURE = {
    "Public Pages": [
        ("/", "home - Homepage with cities, categories, featured vendors"),
        ("/about/", "about - About page"),
        ("/contact/", "contact - Contact page"),
        ("/cities/", "city_list - All cities listing"),
        ("/cities/<int:city_id>/", "city_detail - City with vendors"),
        ("/services/", "service_list - All services with filters"),
        ("/services/<str:service_id>/", "service_detail - Service with vendors"),
        ("/services/subcategory/<str:subcategory_id>/", "subcategory_detail - Subcategory services"),
        ("/vendors/", "vendor_list - All vendors with filters"),
        ("/vendors/<int:vendor_id>/", "vendor_detail - Vendor profile"),
        ("/blogs/", "blog_list - Blog listing"),
        ("/blogs/<slug:slug>/", "blog_detail - Blog post"),
        ("/search/", "search - Search results")
    ],

    "Authentication": [
        ("/register/", "register - User type selection"),
        ("/register/customer/", "customer_register - Customer registration"),
        ("/register/vendor/", "vendor_user_register - Vendor registration"),
        ("/login/", "custom_login - Login page"),
        ("/logout/", "custom_logout - Logout"),
        ("/password_reset/", "Password reset flow"),
        ("/password_reset/done/", "Password reset done"),
        ("/reset/<uidb64>/<token>/", "Password reset confirm"),
        ("/reset/done/", "Password reset complete")
    ],

    "Customer Dashboard": [
        ("/dashboard/customer/", "customer_dashboard - Customer dashboard"),
        ("/enquiry/customer/", "customer_enquiries - Customer's enquiries"),
        ("/favorite/<int:vendor_id>/add/", "add_favorite - Add vendor to favorites"),
        ("/favorite/<int:vendor_id>/remove/", "remove_favorite - Remove favorite"),
        ("/review/<int:vendor_id>/add/", "add_review - Add review"),
        ("/review/<int:vendor_id>/add/<int:booking_id>/", "add_review_with_booking - Review after booking"),
        ("/book/<int:vendor_id>/<str:service_id>/", "book_service - Book a service"),
        ("/enquiry/send/<int:vendor_id>/", "send_enquiry - Send enquiry to vendor"),
        ("/notifications/", "notifications - View notifications"),
        ("/notifications/<int:enquiry_id>/dismiss/", "dismiss_notification - Dismiss notification")
    ],

    "Vendor Dashboard": [
        ("/dashboard/vendor/", "vendor_dashboard - Vendor dashboard"),
        ("/vendor/profile/edit/", "vendor_profile_edit - Edit vendor profile"),
        ("/vendor/register/", "vendor_register - Vendor registration form"),
        ("/vendor/payment/", "vendor_payment_page - Payment page"),
        ("/vendor/payment/callback/", "vendor_payment_callback - Razorpay callback"),
        ("/vendor/service/add/", "vendor_service_add - Add service"),
        ("/vendor/service/<int:service_id>/edit/", "vendor_service_edit - Edit service"),
        ("/vendor/service/<int:service_id>/delete/", "vendor_service_delete - Delete service"),
        ("/vendor/gallery/add/", "vendor_gallery_add - Add gallery image"),
        ("/vendor/gallery/<int:gallery_id>/delete/", "vendor_gallery_delete - Delete gallery image"),
        ("/enquiry/vendor/", "vendor_enquiries - View enquiries"),
        ("/enquiry/respond/<int:enquiry_id>/", "respond_enquiry - Respond to enquiry"),
        ("/booking/<int:booking_id>/<str:status>/", "booking_update_status - Update booking status")
    ],

    "Admin Dashboard": [
        ("/dashboard/admin/", "admin_dashboard - Admin dashboard"),
        ("/dashboard/admin/vendors/all/", "all_vendors - All vendors list"),
        ("/dashboard/admin/vendors/<int:vendor_id>/edit/", "admin_vendor_edit - Edit vendor"),
        ("/dashboard/admin/vendors/<int:vendor_id>/approve/", "approve_vendor - Approve vendor"),
        ("/dashboard/admin/vendors/<int:vendor_id>/reject/", "reject_vendor - Reject vendor"),
        ("/dashboard/admin/vendors/<int:vendor_id>/suspend/", "suspend_vendor - Suspend vendor"),
        ("/dashboard/admin/vendors/<int:vendor_id>/activate/", "activate_vendor - Activate vendor"),
        ("/dashboard/admin/vendors/<int:vendor_id>/delete/", "delete_vendor - Delete vendor"),
        ("/dashboard/admin/payments/", "vendor_payments_list - Payment list"),
        ("/dashboard/admin/payments/<int:payment_id>/", "vendor_payment_detail - Payment detail"),
        ("/dashboard/admin/cities/", "admin_cities - Manage cities"),
        ("/dashboard/admin/categories/", "admin_categories - Manage categories"),
        ("/dashboard/admin/services/", "admin_services - Manage services"),
        ("/dashboard/admin/blogs/", "admin_blogs - Manage blogs"),
        ("/dashboard/admin/bulk-registration/", "bulk_vendor_registration - Bulk upload")
    ]
}

# =============================================================================
# CORE WORKFLOWS
# =============================================================================

WORKFLOWS = {

    "Customer_Registration_and_Booking": """
    Step 1: Customer Registration
    ──────────────────────────────
    1. Customer visits /register/customer/
    2. Fills: username, email, password, phone, city
    3. User and UserProfile created
    4. Logged in automatically
    5. Welcome email sent

    Step 2: Browse/Search
    ───────────────────
    1. Homepage shows cities, categories, featured vendors
    2. Can browse by city or service category
    3. Search by service name, vendor name, location
    4. View vendor profiles with ratings, reviews, services

    Step 3: Send Enquiry (Optional)
    ─────────────────────────────
    1. Click "Send Enquiry" on vendor profile
    2. Select service and describe requirements
    3. Enquiry created with status 'pending'
    4. Vendor receives notification
    5. Vendor responds with quote and details
    6. Customer receives notification of response

    Step 4: Book Service
    ─────────────────
    1. Click "Book Now" on vendor service
    2. Or click "Book" from enquiry response
    3. Fill: date, time, address, description
    4. Booking created with status 'pending'
    5. If from enquiry, enquiry marked as 'closed'
    6. Vendor receives notification

    Step 5: Service Delivery
    ──────────────────────
    1. Vendor updates status: accepted → in_progress → completed
    2. Customer can track status in dashboard
    3. After completion, customer prompted to review

    Step 6: Leave Review
    ─────────────────
    1. Customer receives prompt after booking completion
    2. Can rate 1-5 stars and write comment
    3. Can upload optional photo
    4. Review saved and vendor rating recalculated
    """,

    "Vendor_Registration_and_Payment": """
    Step 1: Vendor User Registration
    ───────────────────────────────
    1. Vendor visits /register/vendor/
    2. Fills: username, email, password, phone, city
    3. Also fills: company_name, experience, address, license_number
    4. User, UserProfile, and Vendor created
    5. Verification status: 'pending'
    6. Logged in automatically

    Step 2: Complete Vendor Profile
    ──────────────────────────────
    1. Redirected to /vendor/register/
    2. Uploads: logo, cover_image
    3. Fills additional details: certifications, emergency availability
    4. Profile saved

    Step 3: Payment
    ─────────────
    1. Redirected to /vendor/payment/
    2. VendorPayment record created with status 'pending'
    3. Razorpay order created for ₹999.00
    4. Customer presented with payment options
    5. Completes payment via Razorpay

    Step 4: Payment Verification
    ────────────────────────────
    1. Razorpay sends callback to /vendor/payment/callback/
    2. Signature verified
    3. Payment status updated to 'completed'
    4. Transaction ID and details saved
    5. Vendor redirected to dashboard

    Step 5: Admin Approval
    ────────────────────
    1. Admin sees vendor in pending list
    2. Admin reviews profile and payment
    3. Admin clicks "Approve" or "Reject"
    4. Verification status updated
    5. Approval/rejection email sent to vendor

    Step 6: Setup Services
    ────────────────────
    1. Approved vendor can add services
    2. For each service: selects service, sets price, adds description
    3. Can upload gallery images
    4. Vendor now visible in public listings
    """,

    "Enquiry_to_Booking_Conversion": """
    Step 1: Customer Sends Enquiry
    ──────────────────────────────
    POST /enquiry/send/<vendor_id>/
    - customer: authenticated user
    - vendor: selected vendor
    - service: selected service
    - message: customer's requirements
    - status: 'pending'

    Step 2: Vendor Receives Notification
    ───────────────────────────────────
    - Vendor sees enquiry in dashboard
    - Notification shows pending enquiry count
    - Can view all enquiries with status filter

    Step 3: Vendor Responds
    ──────────────────────
    POST /enquiry/respond/<enquiry_id>/
    - vendor_response: detailed pricing and service info
    - quoted_amount: total amount in ₹
    - status: updated to 'responded'

    Step 4: Customer Receives Response
    ─────────────────────────────────
    - Customer sees responded enquiries
    - Can view full response with quote
    - "Book Now" button available with pre-filled details

    Step 5: Booking Creation
    ────────────────────────
    POST /book/<vendor_id>/<service_id>/?enquiry=<enquiry_id>
    - enquiry: linked to booking
    - date, time, address, description: customer inputs
    - status: 'pending'
    - Enquiry status updated to 'closed'
    - Vendor receives booking notification
    """
}

# =============================================================================
# FORMS
# =============================================================================

FORMS = {
    "UserRegisterForm": {
        "purpose": "General user registration with user type selection",
        "fields": ["username", "email", "password1", "password2", "phone", "user_type", "city"],
        "creates": ["User", "UserProfile"]
    },

    "VendorUserRegisterForm": {
        "purpose": "Combined vendor user and profile registration",
        "fields": ["username", "email", "password1", "password2", "phone", "city",
                   "company_name", "experience", "address", "license_number"],
        "creates": ["User", "UserProfile (vendor)", "Vendor (pending)"]
    },

    "CustomerRegisterForm": {
        "purpose": "Customer-specific registration",
        "fields": ["username", "email", "password1", "password2", "phone", "city"],
        "creates": ["User", "UserProfile (customer)"]
    },

    "VendorProfileForm": {
        "purpose": "Complete vendor profile editing",
        "fields": ["company_name", "logo", "cover_image", "city", "experience",
                   "phone", "email", "address", "license_number", "certifications",
                   "is_emergency_available"]
    },

    "VendorServiceForm": {
        "purpose": "Add/edit vendor services",
        "fields": ["service", "price", "description"]
    },

    "BookingForm": {
        "purpose": "Create service bookings",
        "fields": ["date", "time", "address", "description"]
    },

    "ReviewForm": {
        "purpose": "Submit vendor reviews",
        "fields": ["rating", "comment", "customer_image"]
    },

    "EnquiryForm": {
        "purpose": "Send enquiries to vendors",
        "fields": ["service", "message"]
    },

    "EnquiryResponseForm": {
        "purpose": "Vendor responds to enquiries",
        "fields": ["vendor_response", "quoted_amount"]
    },

    "BulkVendorRegistrationForm": {
        "purpose": "Excel upload for bulk vendor registration",
        "fields": ["excel_file"],
        "validation": "Must be .xlsx or .xls, max 100 vendors per day"
    }
}

# =============================================================================
# DEPENDENCIES
# =============================================================================

DEPENDENCIES = {
    "core": [
        "Django==5.2.15",
        "asgiref==3.11.1",
        "sqlparse==0.5.5"
    ],
    "forms": [
        "django-crispy-forms==2.6",
        "crispy-bootstrap5==2026.3",
        "django-widget-tweaks==1.5.1"
    ],
    "payments": [
        "razorpay==2.0.1"
    ],
    "data_processing": [
        "pandas (optional - for bulk registration)",
        "openpyxl==3.1.5"
    ],
    "images": [
        "Pillow==12.2.0"
    ],
    "config": [
        "python-decouple==3.8"
    ],
    "static_files": [
        "whitenoise==6.12.0"
    ],
    "http": [
        "requests==2.34.2",
        "urllib3==2.7.0"
    ]
}

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

ENVIRONMENT_CONFIG = {
    "required": {
        "SECRET_KEY": "Django secret key for cryptographic signing",
        "RAZORPAY_KEY_ID": "Razorpay API key ID",
        "RAZORPAY_KEY_SECRET": "Razorpay API key secret"
    },
    "optional": {
        "DEBUG": "Debug mode (default: True)",
        "ALLOWED_HOSTS": "Comma-separated allowed hosts (default: localhost,127.0.0.1)",
        "RAZORPAY_CURRENCY": "Payment currency (default: INR)",
        "RAZORPAY_VENDOR_REGISTRATION_AMOUNT": "Registration fee in paise (default: 99900)",
        "RAZORPAY_WEBHOOK_SECRET": "Razorpay webhook secret",
        "EMAIL_BACKEND": "Email backend (default: SMTP)",
        "EMAIL_HOST": "SMTP server (default: smtp.gmail.com)",
        "EMAIL_PORT": "SMTP port (default: 587)",
        "EMAIL_USE_TLS": "Use TLS (default: True)",
        "EMAIL_HOST_USER": "SMTP username",
        "EMAIL_HOST_PASSWORD": "SMTP password",
        "DEFAULT_FROM_EMAIL": "From email address",
        "FRONTEND_URL": "Frontend URL for email links (default: http://localhost:8000)"
    }
}

# =============================================================================
# SECURITY FEATURES
# =============================================================================

SECURITY_FEATURES = {
    "authentication": "Django's built-in authentication system",
    "csrf_protection": "CSRF middleware enabled globally",
    "password_validation": [
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator"
    ],
    "payment_security": "Razorpay signature verification on callback",
    "authorization": [
        "@login_required decorator on protected views",
        "User type checks (customer/vendor/admin)",
        "Superuser verification for admin pages"
    ],
    "sql_injection": "Protected by Django ORM parameterized queries",
    "xss_protection": "Django template auto-escaping",
    "file_upload": [
        "ImageField validation",
        "Upload to non-executable directories",
        "File size limits"
    ]
}

# =============================================================================
# DEPLOYMENT GUIDE
# =============================================================================

DEPLOYMENT_STEPS = """
1. Prepare Environment
   ───────────────────
   - Create virtual environment: python -m venv venv
   - Activate: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)
   - Install dependencies: pip install -r requirements.txt

2. Configure Environment
   ──────────────────────
   - Create .env file in project root
   - Add required environment variables
   - Set DEBUG=False and configure ALLOWED_HOSTS

3. Database Setup
   ──────────────
   - For SQLite: No action needed (default)
   - For PostgreSQL:
     * Install PostgreSQL
     * Create database
     * Update DATABASES in settings.py
     * Run migrations

4. Run Migrations
   ──────────────
   python manage.py makemigrations
   python manage.py migrate

5. Create Superuser
   ────────────────
   python manage.py createsuperuser

6. Load Sample Data (Optional)
   ───────────────────────────
   python manage.py load_services
   python manage.py load_sample_data

7. Collect Static Files
   ─────────────────────
   python manage.py collectstatic

8. Test Application
   ────────────────
   python manage.py runserver

9. Production Deployment
   ────────────────────
   - Use WSGI server (Gunicorn, uWSGI)
   - Configure web server (Nginx, Apache)
   - Set up SSL certificate
   - Configure static file serving
   - Set up process manager (systemd, supervisor)

10. Monitoring
   ───────────
    - Set up logging
    - Configure error tracking (Sentry)
    - Set up backups
    - Monitor performance
"""

# =============================================================================
# PROJECT STATISTICS
# =============================================================================

PROJECT_STATS = {
    "python_files": "20+",
    "total_lines_of_code": "~5,000+",
    "views_lines": "~2,229",
    "models_count": "13+",
    "url_routes": "130+",
    "html_templates": "50+",
    "forms": "10",
    "management_commands": "3",
    "middleware": "6 (Django default)",
    "context_processors": "4 (2 Django + 2 custom)"
}

# =============================================================================
# FUTURE ENHANCEMENTS
# =============================================================================

FUTURE_ENHANCEMENTS = [
    "Mobile Application (React Native/Flutter)",
    "Real-time Notifications (WebSocket/Django Channels)",
    "Advanced Analytics Dashboard",
    "Commission System (Per-booking revenue)",
    "REST API Development (Django REST Framework)",
    "Multi-language Support (i18n)",
    "Live Vendor Tracking",
    "Escrow Payment System",
    "Customer Support Chat",
    "SMS Notifications",
    "Vendor Subscription Plans",
    "Featured Listings",
    "Promotional Banners",
    "Referral System",
    " loyalty Program",
    "Advanced Search Filters",
    "Price Comparison Tool",
    "Service Availability Calendar"
]

# =============================================================================
# COMMON ISSUES AND SOLUTIONS
# =============================================================================

TROUBLESHOOTING = {
    "payment_not_working": """
    Issue: Razorpay payment not processing
    Solutions:
    1. Check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env
    2. Verify Razorpay account is active
    3. Check if callback URL is accessible
    4. Enable debug mode to see error details
    """,

    "emails_not_sending": """
    Issue: Registration emails not received
    Solutions:
    1. Verify SMTP settings in .env
    2. For Gmail, use App Password instead of regular password
    3. Check EMAIL_HOST and EMAIL_PORT
    4. Verify EMAIL_USE_TLS is enabled
    5. Check spam folder
    """,

    "static_files_not_loading": """
    Issue: CSS/JS files not loading in production
    Solutions:
    1. Run: python manage.py collectstatic
    2. Configure STATIC_ROOT in settings
    3. Set up static file serving in web server
    4. Check file permissions
    """,

    "vendor_dashboard_access_denied": """
    Issue: Vendors cannot access dashboard after payment
    Solutions:
    1. Verify payment status is 'completed' in database
    2. Check VendorPayment record exists
    3. Ensure check_vendor_payment() function returns True
    4. Clear cache and retry
    """
}

# =============================================================================
# API ENDPOINTS (Future - If REST API is Added)
# =============================================================================

PLANNED_API_ENDPOINTS = {
    "authentication": [
        "POST /api/auth/register/",
        "POST /api/auth/login/",
        "POST /api/auth/logout/",
        "POST /api/auth/password/reset/"
    ],
    "vendors": [
        "GET /api/vendors/",
        "GET /api/vendors/{id}/",
        "POST /api/vendors/",
        "PUT /api/vendors/{id}/",
        "DELETE /api/vendors/{id}/"
    ],
    "services": [
        "GET /api/services/",
        "GET /api/services/{id}/",
        "GET /api/categories/",
        "GET /api/categories/{id}/services/"
    ],
    "bookings": [
        "GET /api/bookings/",
        "POST /api/bookings/",
        "PUT /api/bookings/{id}/status/",
        "GET /api/bookings/{id}/"
    ],
    "enquiries": [
        "GET /api/enquiries/",
        "POST /api/enquiries/",
        "PUT /api/enquiries/{id}/respond/"
    ]
}

# =============================================================================
# DATABASE OPTIMIZATION QUERIES
# =============================================================================

OPTIMIZED_QUERIES = {
    "home_page": """
    # Optimized query for homepage
    featured_vendors = Vendor.objects.filter(
        verification_status='verified'
    ).prefetch_related(
        'vendor_services__service'
    ).select_related('city').annotate(
        booking_count=Count('bookings')
    ).order_by('-experience', '-rating', '-booking_count')[:6]
    """,

    "vendor_list": """
    # Optimized query for vendor listing
    vendors = Vendor.objects.filter(
        verification_status='verified'
    ).prefetch_related(
        'vendor_services__service__subcategory__category'
    ).select_related('city').annotate(
        booking_count=Count('bookings')
    )
    """,

    "service_detail": """
    # Optimized query for service detail page
    vendor_services = VendorService.objects.filter(
        service=service,
        vendor__verification_status='verified',
        vendor__city=user_city
    ).select_related('vendor', 'vendor__city').order_by('price')
    """
}

# =============================================================================
# TESTING STRATEGY
# =============================================================================

TESTING_PLAN = """
Unit Tests:
- Model tests for all models
- Form validation tests
- View function tests
- Utility function tests

Integration Tests:
- User registration flow
- Vendor registration and payment flow
- Booking creation flow
- Enquiry response flow
- Admin approval flow

End-to-End Tests:
- Complete customer journey
- Complete vendor journey
- Admin management workflows

Performance Tests:
- Load testing for concurrent users
- Database query optimization
- Static file serving performance

Security Tests:
- SQL injection attempts
- XSS vulnerability scanning
- CSRF token validation
- Payment security verification
"""

# =============================================================================
# MAINTENANCE TASKS
# =============================================================================

MAINTENANCE_CHECKLIST = [
    "Daily: Backup database",
    "Daily: Check error logs",
    "Weekly: Review pending vendors",
    "Weekly: Verify payment processing",
    "Monthly: Update dependencies",
    "Monthly: Review and optimize slow queries",
    "Monthly: Clean up old sessions",
    "Quarterly: Security audit",
    "Quarterly: Performance review",
    "Annually: Disaster recovery test"
]

# =============================================================================
# CLIENT COMMUNICATION
# =============================================================================

CLIENT_SUMMARY = """
BorewellMart is a production-ready marketplace platform that connects
customers needing borewell and agricultural services with verified
local vendors.

Key Features for Customers:
- Search vendors by location and service type
- Compare prices and read reviews
- Send enquiries for detailed quotes
- Book services online 24/7
- Track service status
- Leave reviews

Key Features for Vendors:
- Register and verify their business
- List services with custom pricing
- Showcase work through gallery
- Receive enquiries and bookings
- Build reputation through reviews
- Reach more customers

Key Features for Admin:
- Approve and manage vendors
- Handle payments and disputes
- Manage all platform content
- View analytics and reports
- Bulk vendor registration
- Full control over platform

The platform is:
- Built on Django (proven, secure framework)
- Integrated with Razorpay for payments
- Fully responsive and mobile-friendly
- SEO optimized with blog functionality
- Ready for deployment with proper configuration
"""

# =============================================================================
# END OF DOCUMENTATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BorewellMart - Complete Project Documentation")
    print("=" * 70)
    print(f"\nProject: {PROJECT_NAME}")
    print(f"Type: {PROJECT_TYPE}")
    print(f"Framework: {FRAMEWORK}")
    print(f"Database: {DATABASE}")
    print(f"Payment: {PAYMENT_GATEWAY}")
    print("\n" + "=" * 70)
    print("For detailed documentation, review the constants in this file.")
    print("=" * 70)
