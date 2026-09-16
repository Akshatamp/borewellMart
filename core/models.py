from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import RegexValidator
from decimal import Decimal
import secrets
import string


class City(models.Model):
    """City model for service locations"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    state = models.CharField(max_length=100, blank=True)
    vendor_count = models.PositiveIntegerField(default=0)
    service_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_nearby_cities(self, limit=5):
        """Get nearby cities in the same state, ordered by name"""
        if not self.state:
            return City.objects.none()
        # Get cities in the same state, excluding this one
        return City.objects.filter(
            state=self.state
        ).exclude(
            id=self.id
        ).order_by('name')[:limit]


class Sector(models.Model):
    """Sectors (e.g., Drilling, Cleaning) - formerly ServiceCategory"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='services/categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Sectors'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    """Services (e.g., Borewell Drilling, Tube Well Drilling) - formerly ServiceSubcategory"""
    id = models.CharField(max_length=50, primary_key=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='services/subcategories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ['sector', 'name']
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.sector.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class SubService(models.Model):
    """Sub-services (individual services) - formerly Service"""
    id = models.CharField(max_length=50, primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subservices')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    popular = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    per_feet_amount = models.CharField(max_length=200, blank=True, null=True, help_text='Price per feet (e.g., "₹150 per feet" or "Starting from ₹150")')

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'SubServices'

    def __str__(self):
        return self.name

    @property
    def sector(self):
        return self.service.sector if self.service else None

    @property
    def is_category(self):
        """Check if this subservice has children (is a category level)"""
        return self.children.exists()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while SubService.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """Extended user profile"""
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('partner', 'Partner'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    phone = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    state = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Vendor(models.Model):
    """Vendor/Service provider profile"""
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor')
    company_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='vendor_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='vendor_covers/', blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, related_name='vendors')
    state = models.CharField(max_length=100, blank=True)
    experience = models.PositiveIntegerField(default=0, help_text='Years of experience')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    is_bulk_registered = models.BooleanField(default=False)
    is_emergency_available = models.BooleanField(default=False)
    services_count = models.PositiveIntegerField(default=0)
    bookings_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.company_name

    def update_rating(self):
        """Recalculate vendor rating based on reviews"""
        from django.db.models import Avg
        from .models import Review
        reviews = Review.objects.filter(vendor=self)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.rating = round(avg_rating, 2) if avg_rating else 0.0
        else:
            self.rating = 0.0
        self.save()

    def get_initials(self):
        """
        Extract initials from company name for logo generation.
        Examples:
        - 'Kalaburagi Irrigation' -> 'KI'
        - 'ABC Borewell Services' -> 'AB'
        - 'X' -> 'X'
        """
        if not self.company_name:
            return 'VN'
        
        # Remove common words and get meaningful words
        words = self.company_name.split()
        
        # Filter out common business words
        common_words = {'services', 'service', 'pvt', 'ltd', 'limited', 'private', 'corporation', 
                        'company', 'enterprises', 'traders', 'works', 'industries', 'solutions',
                        'agencies', 'associates', 'partners', 'group', 'international', 'global'}
        
        meaningful_words = [word for word in words if word.lower() not in common_words]
        
        # If no meaningful words after filtering, use original words
        if not meaningful_words:
            meaningful_words = words
        
        # Get initials (first letter of each word, max 2)
        initials = ''
        for word in meaningful_words[:2]:
            if word:
                initials += word[0].upper()
        
        # If still no initials, use default
        if not initials:
            initials = 'VN'
        
        return initials

    def get_logo_color(self):
        """
        Generate a consistent color based on company name hash.
        Returns a CSS color string.
        """
        if not self.company_name:
            return '#06B6D4'
        
        # Simple hash function
        hash_value = sum(ord(c) for c in self.company_name)
        
        # Generate colors from a predefined palette
        colors = [
            '#06B6D4',  # Cyan
            '#8B5CF6',  # Purple
            '#EC4899',  # Pink
            '#F59E0B',  # Amber
            '#10B981',  # Emerald
            '#3B82F6',  # Blue
            '#EF4444',  # Red
            '#6366F1',  # Indigo
            '#14B8A6',  # Teal
            '#F97316',  # Orange
        ]
        
        return colors[hash_value % len(colors)]


class VendorService(models.Model):
    """Services offered by a vendor"""
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_services')
    subservice = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='vendor_services')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['vendor', 'subservice']
        verbose_name_plural = 'Vendor Services'

    def __str__(self):
        return f"{self.vendor.company_name} - {self.subservice.name}"


class VendorGallery(models.Model):
    """Gallery images for vendors"""
    IMAGE_TYPE_CHOICES = [
        ('work', 'Work Sample'),
        ('team', 'Team'),
        ('equipment', 'Equipment'),
        ('before_after', 'Before/After'),
        ('other', 'Other'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='vendor_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='work')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Vendor Gallery'

    def __str__(self):
        return f"{self.vendor.company_name} - {self.caption or 'Image'}"


class Booking(models.Model):
    """Service bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='bookings')
    subservice = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='bookings')
    enquiry = models.ForeignKey('Enquiry', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    date = models.DateField()
    time = models.TimeField()
    address = models.TextField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_emergency = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking by {self.customer.username} with {self.vendor.company_name}"


class BookingPayment(models.Model):
    """Payment for bookings"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='cod')
    transaction_id = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Booking Payments'

    def __str__(self):
        return f"Payment for booking {self.booking.id}"


class Review(models.Model):
    """Customer reviews for vendors"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='review')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    customer_image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'booking']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer.username} for {self.vendor.company_name}"


class FavoriteVendor(models.Model):
    """User's favorite vendors"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_vendors')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['customer', 'vendor']
        verbose_name_plural = 'Favorite Vendors'

    def __str__(self):
        return f"{self.customer.username} - {self.vendor.company_name}"


class Blog(models.Model):
    """Blog posts for knowledge center"""
    CATEGORY_CHOICES = [
        ('drilling', 'Drilling'),
        ('maintenance', 'Maintenance'),
        ('water_quality', 'Water Quality'),
        ('pump', 'Pump'),
        ('general', 'General'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Enquiry(models.Model):
    """Customer enquiries for vendors"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enquiries')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='enquiries')
    subservice = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='enquiries')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    vendor_response = models.TextField(blank=True)
    quoted_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Enquiry by {self.customer.username} to {self.vendor.company_name}"


class VendorPayment(models.Model):
    """Vendor payments and plans"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]

    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='payment')
    plan_type = models.CharField(max_length=50, default='free')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gateway_response = models.TextField(blank=True, null=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Vendor Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vendor.company_name} - {self.plan_type}"

    def mark_completed(self, transaction_id='', paid_amount=None, gateway_response=None):
        """Mark payment as completed"""
        from datetime import date
        from django.utils import timezone
        self.status = 'completed'
        self.transaction_id = transaction_id
        if paid_amount is not None:
            self.paid_amount = paid_amount
        if gateway_response is not None:
            self.gateway_response = gateway_response
        self.is_active = True
        self.valid_from = date.today()
        self.payment_date = timezone.now()
        # Set validity to 1 year from now for free plans, or use existing valid_until
        if not self.valid_until:
            from datetime import timedelta
            self.valid_until = date.today() + timedelta(days=365)
        self.save()


class VendorPlan(models.Model):
    """Vendor subscription plans"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    PLAN_TYPE_CHOICES = [
        ('basic', 'Basic Plan'),
        ('premium', 'Premium Plan'),
        ('professional', 'Professional Plan'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='plans')
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPE_CHOICES)
    plan_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    validity_period = models.PositiveIntegerField(default=30, help_text='Validity period in days')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vendor Plans'

    def __str__(self):
        return f"{self.vendor.company_name} - {self.plan_name}"

    @property
    def is_expired(self):
        from datetime import date
        return self.end_date < date.today()

    def days_until_expiry(self):
        from datetime import date
        if self.is_expired:
            return 0
        return (self.end_date - date.today()).days

    def update_status(self):
        """Update plan status based on current date and end date"""
        from datetime import date
        if self.status == 'cancelled':
            return
        if self.end_date < date.today():
            self.status = 'expired'
            self.save()
        elif self.status == 'expired' and self.end_date >= date.today():
            # Plan was expired but is now valid (e.g., plan was renewed)
            self.status = 'active'
            self.save()

    def get_notification_days(self):
        """Return list of days before expiry to send notifications"""
        return [7, 3, 1]


class PlanNotification(models.Model):
    """Notifications for plan expiry"""
    plan = models.ForeignKey(VendorPlan, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)
    notification_text = models.TextField(blank=True)
    notification_date = models.DateField()
    is_sent = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['notification_date']
        verbose_name_plural = 'Plan Notifications'

    def __str__(self):
        return f"Notification for {self.plan.plan_name}"


# ==================== Forum Models ====================

class ForumCategory(models.Model):
    """Forum categories - can be linked to services or standalone"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_service_related = models.BooleanField(default=False, help_text='If True, linked to a sector')
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_categories')
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    thread_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Forum Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ForumThread(models.Model):
    """Forum discussion threads/questions"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('solved', 'Solved'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250, blank=True, null=True)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_threads')
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    is_pinned = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        verbose_name_plural = 'Forum Threads'

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:100]
            slug = base_slug
            counter = 1
            while ForumThread.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def best_answer(self):
        return self.posts.filter(is_best_answer=True).first()

    @property
    def tags(self):
        """Get tags from linked services or custom tags"""
        related_services = self.related_services.all()
        if related_services.exists():
            return [s.subservice.name for s in related_services[:3]]
        return []


class ForumPost(models.Model):
    """Individual posts/replies within a thread"""
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    is_best_answer = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_best_answer', 'created_at']
        verbose_name_plural = 'Forum Posts'

    def __str__(self):
        return f"Reply by {self.author.username} in {self.thread.title}"

    @property
    def is_vendor_verified(self):
        """Check if author is a verified vendor"""
        try:
            vendor = self.author.vendor
            return vendor.verification_status == 'verified'
        except Vendor.DoesNotExist:
            return False

    @property
    def helpful_votes_count(self):
        return self.votes.filter(vote_type='up').count()


class ForumVote(models.Model):
    """Votes on threads and posts"""
    VOTE_TYPE_CHOICES = [
        ('up', 'Upvote/Like'),
        ('down', 'Downvote'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'thread'] or ['user', 'post']
        verbose_name_plural = 'Forum Votes'

    def __str__(self):
        target = self.thread or self.post
        return f"{self.user.username} {self.vote_type}s {target}"


class ForumTag(models.Model):
    """Custom tags for forum threads"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, max_length=50)
    thread_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Forum Tags'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ForumThreadTag(models.Model):
    """Many-to-many relationship between threads and tags"""
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='thread_tags')
    tag = models.ForeignKey(ForumTag, on_delete=models.CASCADE, related_name='tagged_threads')

    class Meta:
        unique_together = ['thread', 'tag']
        verbose_name_plural = 'Forum Thread Tags'


class ForumThreadService(models.Model):
    """Link forum threads to subservices for service-related discussions"""
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='related_services')
    subservice = models.ForeignKey(SubService, on_delete=models.CASCADE, related_name='forum_threads')

    class Meta:
        unique_together = ['thread', 'subservice']
        verbose_name_plural = 'Forum Thread Services'


# ==================== Community Models ====================

class Community(models.Model):
    """Communities for customers and vendors to connect and share"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='communities/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='communities/covers/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    member_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Communities'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Community.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def post_count(self):
        return self.posts.count()

    @property
    def member_list(self):
        return User.objects.filter(community_members__community=self).order_by('-community_members__joined_at')


class CommunityMember(models.Model):
    """Membership of users in communities"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_members')
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'community']
        verbose_name_plural = 'Community Members'

    def __str__(self):
        return f"{self.user.username} - {self.community.name} ({self.role})"

    def save(self, *args, **kwargs):
        is_new = self.id is None
        super().save(*args, **kwargs)
        if is_new:
            # Update community member count
            self.community.member_count = self.community.members.count()
            self.community.save()

    def delete(self, *args, **kwargs):
        community = self.community
        super().delete(*args, **kwargs)
        # Update community member count
        community.member_count = community.members.count()
        community.save()


class CommunityPost(models.Model):
    """Posts within communities"""
    POST_TYPE_CHOICES = [
        ('post', 'Post'),
        ('announcement', 'Announcement'),
        ('question', 'Question'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='post')
    image = models.ImageField(upload_to='community_posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Community Posts'

    def __str__(self):
        return f"{self.author.username} in {self.community.name}"

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def like_count(self):
        return self.likes.count()

    def is_liked_by_user(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class CommunityComment(models.Model):
    """Comments on community posts"""
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Community Comments'

    def __str__(self):
        return f"Comment by {self.author.username}"


class CommunityLike(models.Model):
    """Likes on community posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_likes')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        verbose_name_plural = 'Community Likes'

    def __str__(self):
        return f"{self.user.username} likes post in {self.post.community.name}"


class VendorEquipment(models.Model):
    """Equipment/machines that vendors want to sell"""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('excellent', 'Excellent - Like New'),
        ('good', 'Good - Minor Wear'),
        ('fair', 'Fair - Moderate Wear'),
        ('for_parts', 'For Parts Only'),
    ]

    CATEGORY_CHOICES = [
        ('drilling_machine', 'Drilling Machine'),
        ('pump', 'Water Pump'),
        ('pipe', 'Pipes & Fittings'),
        ('motor', 'Electric Motor'),
        ('generator', 'Generator'),
        ('compressor', 'Air Compressor'),
        ('tools', 'Hand Tools'),
        ('other', 'Other Equipment'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='equipment')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='drilling_machine')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_negotiable = models.BooleanField(default=True)
    image = models.ImageField(upload_to='vendor_equipment/', blank=True, null=True)
    year_manufactured = models.PositiveIntegerField(blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, help_text='Location of the equipment')
    is_available = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Vendor Equipment'

    def __str__(self):
        return f"{self.title} by {self.vendor.company_name}"

    @property
    def condition_display(self):
        return dict(self.CONDITION_CHOICES).get(self.condition, self.condition)

    @property
    def category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)


class EquipmentInquiry(models.Model):
    """Inquiries about vendor equipment"""
    equipment = models.ForeignKey(VendorEquipment, on_delete=models.CASCADE, related_name='inquiries')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equipment_inquiries')
    message = models.TextField()
    is_contacted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Equipment Inquiries'

    def __str__(self):
        return f"Inquiry by {self.customer.username} for {self.equipment.title}"


# ==================== Analytics Models ====================

class VisitorTracking(models.Model):
    """Track unique visitors to the website"""
    session_key = models.CharField(max_length=200, unique=True, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_agent = models.TextField(blank=True)
    first_visit = models.DateTimeField(auto_now_add=True)
    last_visit = models.DateTimeField(auto_now=True)
    visit_count = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Visitor'
        verbose_name_plural = 'Visitors'
        ordering = ['-first_visit']

    def __str__(self):
        identifier = self.user.username if self.user else self.ip_address or 'Anonymous'
        return f"Visitor {identifier} - {self.first_visit.strftime('%Y-%m-%d')}"


# ==================== Partner / Referral Models ====================

def generate_partner_code(length=8):
    """Generate a unique random alphanumeric code"""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not Partner.objects.filter(referral_code=code).exists() and \
           not PartnerCoupon.objects.filter(code=code).exists():
            return code


class Partner(models.Model):
    """Partner profile - referral agents who onboard vendors"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner_profile')
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    max_coupons = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = generate_partner_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company_name} ({self.referral_code})"

    @property
    def is_active(self):
        return self.status == 'active'

    def get_referral_link(self, request=None):
        from django.conf import settings
        base_url = settings.FRONTEND_URL
        return f"{base_url.rstrip('/')}/register/vendor/?ref={self.referral_code}"

    @property
    def total_referrals(self):
        return self.referrals.count()

    @property
    def converted_referrals(self):
        """Vendors who completed the registration payment"""
        return self.referrals.filter(
            vendor__payment__status='completed'
        ).count()


class PartnerCoupon(models.Model):
    """Tracking coupon codes created/shared by partners (no discount)"""
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='coupons')
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text='Leave blank for unlimited')
    times_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partner Coupon'
        verbose_name_plural = 'Partner Coupons'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_partner_code(10)
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.partner.status != 'active':
            return False
        if self.max_uses is not None and self.times_used >= self.max_uses:
            return False
        return True


class PartnerReferral(models.Model):
    """Permanent record of which partner referred which vendor"""
    SOURCE_CHOICES = [
        ('link', 'Referral Link'),
        ('coupon', 'Coupon Code'),
    ]

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='referrals')
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='referral')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='link')
    coupon = models.ForeignKey(PartnerCoupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partner Referral'
        verbose_name_plural = 'Partner Referrals'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.partner.company_name} -> {self.vendor.company_name}"
