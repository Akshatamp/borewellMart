from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from datetime import date
from .models import (
    City, SubService, Sector, Service, Vendor,
    VendorService, Booking, Review, UserProfile, Blog, Enquiry,
    FavoriteVendor, VendorGallery, VendorPlan, PlanNotification,
    ForumCategory, ForumThread, ForumPost, ForumVote, ForumTag,
    ForumThreadTag, ForumThreadService, Community, CommunityMember,
    CommunityPost, VisitorTracking, Partner, PartnerCoupon, PartnerReferral, WebsiteRequest
)
from .utils import send_whatsapp_vendor_approval_notification


# Inline classes for related objects
class SubServiceInline(admin.TabularInline):
    model = SubService
    extra = 0
    fields = ['id', 'name', 'description', 'popular', 'order']
    show_change_link = True


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ['id', 'name', 'description', 'icon', 'order']
    show_change_link = True


class VendorServiceInline(admin.TabularInline):
    model = VendorService
    extra = 0
    fields = ['subservice', 'price', 'description']
    autocomplete_fields = ['subservice']


class VendorGalleryInline(admin.TabularInline):
    model = VendorGallery
    extra = 0
    fields = ['image', 'caption', 'image_type']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor_count', 'service_count', 'latitude', 'longitude']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'vendor_count', 'service_count']
    prepopulated_fields = {}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'image')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Statistics', {
            'fields': ('vendor_count', 'service_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['bulk_update_coordinates']

    def vendor_count(self, obj):
        return obj.vendor_count
    vendor_count.short_description = 'Vendors'

    def service_count(self, obj):
        return obj.service_count
    service_count.short_description = 'Services'


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'order', 'service_count', 'subservice_count', 'created_at']
    search_fields = ['name', 'description', 'id']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'service_count', 'subservice_count']
    prepopulated_fields = {}
    inlines = [ServiceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'icon')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Organization', {
            'fields': ('order',)
        }),
        ('Statistics', {
            'fields': ('service_count', 'subservice_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['bulk_reorder_services']

    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = 'Services'

    def subservice_count(self, obj):
        return SubService.objects.filter(service__sector=obj).count()
    subservice_count.short_description = 'Total SubServices'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sector', 'order', 'subservice_count', 'created_at']
    search_fields = ['name', 'description', 'id', 'sector__name']
    list_filter = ['sector', 'created_at']
    readonly_fields = ['created_at', 'subservice_count']
    autocomplete_fields = ['sector']
    inlines = [SubServiceInline]
    fieldsets = (
        ('Sector', {
            'fields': ('sector',)
        }),
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'icon')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Organization', {
            'fields': ('order',)
        }),
        ('Statistics', {
            'fields': ('subservice_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['bulk_reorder_subservices']

    def subservice_count(self, obj):
        return obj.subservices.count()
    subservice_count.short_description = 'SubServices'


@admin.register(SubService)
class SubServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'sector', 'per_feet_amount', 'popular', 'order', 'vendor_count', 'created_at']
    search_fields = ['name', 'description', 'id', 'service__name']
    list_filter = ['service__sector', 'service', 'popular', 'created_at']
    readonly_fields = ['created_at', 'sector', 'vendor_count']
    autocomplete_fields = ['service']
    fieldsets = (
        ('Service', {
            'fields': ('service', 'sector')
        }),
        ('Basic Information', {
            'fields': ('id', 'name', 'description')
        }),
        ('Pricing', {
            'fields': ('per_feet_amount',)
        }),
        ('Features', {
            'fields': ('features', 'popular')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Organization', {
            'fields': ('order',)
        }),
        ('Statistics', {
            'fields': ('vendor_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_popular', 'mark_as_not_popular', 'bulk_update_order']

    def sector(self, obj):
        try:
            return obj.service.sector.name if obj.service and obj.service.sector else 'N/A'
        except:
            return 'N/A'
    sector.short_description = 'Sector'

    def vendor_count(self, obj):
        return obj.vendor_services.count()
    vendor_count.short_description = 'Vendors'

    def mark_as_popular(self, request, queryset):
        queryset.update(popular=True)
        self.message_user(request, f'{queryset.count()} subservices marked as popular.')
    mark_as_popular.short_description = 'Mark selected as popular'

    def mark_as_not_popular(self, request, queryset):
        queryset.update(popular=False)
        self.message_user(request, f'{queryset.count()} subservices marked as not popular.')
    mark_as_not_popular.short_description = 'Mark selected as not popular'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'city', 'experience', 'rating', 'verification_status', 'services_count', 'is_emergency_available', 'created_at']
    search_fields = ['company_name', 'user__username', 'phone', 'email', 'license_number']
    list_filter = ['verification_status', 'city', 'is_emergency_available', 'created_at']
    readonly_fields = ['created_at', 'rating', 'services_count', 'bookings_count']
    autocomplete_fields = ['user', 'city']
    inlines = [VendorServiceInline, VendorGalleryInline]
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Details', {
            'fields': ('company_name', 'logo', 'cover_image', 'license_number', 'certifications')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'city')
        }),
        ('Professional Details', {
            'fields': ('experience', 'rating', 'verification_status', 'is_emergency_available')
        }),
        ('Statistics', {
            'fields': ('services_count', 'bookings_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_vendors', 'suspend_vendors', 'enable_emergency', 'disable_emergency']

    def services_count(self, obj):
        return obj.services_count
    services_count.short_description = 'Services'

    def bookings_count(self, obj):
        return obj.bookings_count
    bookings_count.short_description = 'Bookings'

    def approve_vendors(self, request, queryset):
        vendor_ids = list(queryset.values_list('id', flat=True))
        queryset.update(verification_status='verified')
        self.message_user(request, f'{queryset.count()} vendors approved.')
        # Send WhatsApp notification to approved vendors
        for vendor_id in vendor_ids:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
                print(f"[DEBUG] Attempting to send WhatsApp approval notification to: {vendor.company_name}, Phone: {vendor.phone}")
                success, response = send_whatsapp_vendor_approval_notification(vendor)
                print(f"[DEBUG] WhatsApp notification result - Success: {success}, Response: {response}")
                if not success:
                    print(f"[ERROR] Failed to send WhatsApp to {vendor.company_name}: {response}")
            except Vendor.DoesNotExist:
                print(f"[ERROR] Vendor with id {vendor_id} not found")
            except Exception as e:
                print(f"[ERROR] Failed to send WhatsApp approval notification: {e}")
    approve_vendors.short_description = 'Approve selected vendors'

    def suspend_vendors(self, request, queryset):
        queryset.update(verification_status='suspended')
        self.message_user(request, f'{queryset.count()} vendors suspended.')
    suspend_vendors.short_description = 'Suspend selected vendors'

    def enable_emergency(self, request, queryset):
        queryset.update(is_emergency_available=True)
        self.message_user(request, f'Emergency service enabled for {queryset.count()} vendors.')
    enable_emergency.short_description = 'Enable emergency service'

    def disable_emergency(self, request, queryset):
        queryset.update(is_emergency_available=False)
        self.message_user(request, f'Emergency service disabled for {queryset.count()} vendors.')
    disable_emergency.short_description = 'Disable emergency service'


@admin.register(VendorService)
class VendorServiceAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'subservice', 'sector', 'service', 'price', 'created_at']
    search_fields = ['vendor__company_name', 'subservice__name', 'description']
    list_filter = ['subservice__service__sector', 'subservice__service', 'created_at']
    autocomplete_fields = ['vendor', 'subservice']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Association', {
            'fields': ('vendor', 'subservice')
        }),
        ('Pricing', {
            'fields': ('price', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['bulk_update_prices']

    def sector(self, obj):
        try:
            return obj.subservice.service.sector.name if obj.subservice and obj.subservice.service and obj.subservice.service.sector else 'N/A'
        except:
            return 'N/A'
    sector.short_description = 'Sector'

    def service(self, obj):
        try:
            return obj.subservice.service.name if obj.subservice and obj.subservice.service else 'N/A'
        except:
            return 'N/A'
    service.short_description = 'Service'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'vendor', 'subservice', 'date', 'time', 'status', 'is_emergency', 'created_at']
    search_fields = ['customer__username', 'vendor__company_name', 'subservice__name']
    list_filter = ['status', 'is_emergency', 'date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['customer', 'vendor', 'subservice', 'enquiry']
    fieldsets = (
        ('Booking Details', {
            'fields': ('customer', 'vendor', 'subservice', 'enquiry')
        }),
        ('Schedule', {
            'fields': ('date', 'time', 'is_emergency')
        }),
        ('Location', {
            'fields': ('address', 'description')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_completed', 'mark_as_cancelled', 'accept_bookings']

    def accept_bookings(self, request, queryset):
        queryset.filter(status='pending').update(status='accepted')
        self.message_user(request, 'Selected bookings have been accepted.')
    accept_bookings.short_description = 'Accept pending bookings'

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f'{queryset.count()} bookings marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f'{queryset.count()} bookings marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark as cancelled'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vendor', 'booking', 'rating', 'created_at']
    search_fields = ['customer__username', 'vendor__company_name', 'comment']
    list_filter = ['rating', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['customer', 'vendor', 'booking']
    fieldsets = (
        ('Review', {
            'fields': ('customer', 'vendor', 'booking', 'rating', 'comment')
        }),
        ('Customer Image', {
            'fields': ('customer_image',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    actions = ['delete_selected_reviews']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'user_type', 'city', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    list_filter = ['user_type', 'city', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user', 'city']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('phone', 'user_type', 'city', 'address')
        }),
        ('Profile Image', {
            'fields': ('profile_image',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'author', 'created_at', 'updated_at']
    search_fields = ['title', 'slug', 'content', 'author__username']
    list_filter = ['category', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'category')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Author', {
            'fields': ('author',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'vendor', 'subservice', 'status', 'quoted_amount', 'created_at', 'updated_at']
    search_fields = ['customer__username', 'vendor__company_name', 'subservice__name', 'message']
    list_filter = ['status', 'created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['customer', 'vendor', 'subservice']
    fieldsets = (
        ('Enquiry Details', {
            'fields': ('customer', 'vendor', 'subservice', 'message')
        }),
        ('Vendor Response', {
            'fields': ('status', 'vendor_response', 'quoted_amount')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_responded', 'mark_as_closed', 'mark_as_pending']

    def mark_as_responded(self, request, queryset):
        queryset.update(status='responded')
        self.message_user(request, f'{queryset.count()} enquiries marked as responded.')
    mark_as_responded.short_description = 'Mark as responded'

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f'{queryset.count()} enquiries marked as closed.')
    mark_as_closed.short_description = 'Mark as closed'

    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, f'{queryset.count()} enquiries marked as pending.')
    mark_as_pending.short_description = 'Mark as pending'


@admin.register(FavoriteVendor)
class FavoriteVendorAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vendor', 'created_at']
    search_fields = ['customer__username', 'vendor__company_name']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['customer', 'vendor']


@admin.register(VendorGallery)
class VendorGalleryAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'image_type', 'caption', 'created_at']
    search_fields = ['vendor__company_name', 'caption']
    list_filter = ['image_type', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['vendor']
    fieldsets = (
        ('Vendor', {
            'fields': ('vendor',)
        }),
        ('Image', {
            'fields': ('image', 'caption', 'image_type')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class PlanNotificationInline(admin.TabularInline):
    model = PlanNotification
    extra = 0
    readonly_fields = ['sent_at', 'notification_date', 'is_sent', 'email_sent', 'sms_sent']
    fields = ['notification_type', 'notification_date', 'is_sent', 'email_sent', 'sms_sent', 'sent_at']
    can_delete = False


@admin.register(VendorPlan)
class VendorPlanAdmin(admin.ModelAdmin):
    list_display = ['vendor_company_name', 'plan_type', 'price', 'validity_period', 'status_badge', 'days_until_expiry_display', 'created_at']
    search_fields = ['vendor__company_name', 'plan_name']
    list_filter = ['status', 'plan_type', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'is_expired', 'days_until_expiry', 'get_notification_days']
    autocomplete_fields = ['vendor']
    inlines = [PlanNotificationInline]

    fieldsets = (
        ('Vendor & Plan Type', {
            'fields': ('vendor', 'plan_type', 'plan_name')
        }),
        ('Pricing & Validity', {
            'fields': ('price', 'start_date', 'end_date', 'validity_period')
        }),
        ('Status & Details', {
            'fields': ('status', 'is_expired', 'days_until_expiry', 'description')
        }),
        ('Notification Settings', {
            'fields': ('get_notification_days',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def vendor_company_name(self, obj):
        return obj.vendor.company_name
    vendor_company_name.short_description = 'Vendor'

    def validity_period(self, obj):
        return f"{obj.start_date} to {obj.end_date}"
    validity_period.short_description = 'Validity Period'

    def days_until_expiry_display(self, obj):
        days = obj.days_until_expiry()
        if days <= 0:
            return format_html('<span style="color: red;">Expired</span>')
        elif days <= 7:
            return format_html('<span style="color: orange;">{} days left</span>', days)
        else:
            return format_html('<span style="color: green;">{} days left</span>', days)
    days_until_expiry_display.short_description = 'Days Until Expiry'

    def status_badge(self, obj):
        colors = {
            'active': 'green',
            'expired': 'red',
            'cancelled': 'gray',
        }
        color = colors.get(obj.status, 'blue')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(PlanNotification)
class PlanNotificationAdmin(admin.ModelAdmin):
    list_display = ['plan_vendor', 'notification_type', 'notification_date', 'is_sent_badge', 'sent_at']
    search_fields = ['plan__vendor__company_name']
    list_filter = ['notification_type', 'is_sent', 'email_sent', 'sms_sent', 'sent_at']
    readonly_fields = ['sent_at', 'plan', 'notification_date']

    fieldsets = (
        ('Plan Information', {
            'fields': ('plan', 'notification_date')
        }),
        ('Notification Details', {
            'fields': ('notification_type', 'notification_text', 'is_sent')
        }),
        ('Delivery Status', {
            'fields': ('email_sent', 'sms_sent')
        }),
        ('Metadata', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )

    def plan_vendor(self, obj):
        return f"{obj.plan.vendor.company_name} - {obj.plan.plan_name}"
    plan_vendor.short_description = 'Plan'

    def is_sent_badge(self, obj):
        color = 'green' if obj.is_sent else 'red'
        status = 'Sent' if obj.is_sent else 'Pending'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            status
        )
    is_sent_badge.short_description = 'Status'

    def has_add_permission(self, request):
        return False  # Prevent manual creation; notifications are auto-generated


# ==================== Forum Admin Classes ====================

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'is_service_related', 'sector_link', 'thread_count', 'post_count', 'order']
    search_fields = ['name', 'description', 'slug']
    list_filter = ['is_service_related', 'created_at']
    readonly_fields = ['created_at', 'thread_count', 'post_count', 'slug']
    autocomplete_fields = ['sector']
    prepopulated_fields = {}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'icon')
        }),
        ('Category Type', {
            'fields': ('is_service_related', 'sector')
        }),
        ('Organization', {
            'fields': ('order',)
        }),
        ('Statistics', {
            'fields': ('thread_count', 'post_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['recalculate_counts']

    def sector_link(self, obj):
        return obj.sector.name if obj.sector else 'N/A'
    sector_link.short_description = 'Sector'

    def recalculate_counts(self, request, queryset):
        for category in queryset:
            category.thread_count = category.threads.count()
            category.post_count = ForumPost.objects.filter(thread__category=category).count()
            category.save()
        self.message_user(request, f'Counts recalculated for {queryset.count()} categories.')
    recalculate_counts.short_description = 'Recalculate counts'


@admin.register(ForumTag)
class ForumTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'thread_count', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['created_at', 'slug', 'thread_count']
    prepopulated_fields = {}
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug')
        }),
        ('Statistics', {
            'fields': ('thread_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


class ForumThreadTagInline(admin.TabularInline):
    model = ForumThreadTag
    extra = 0
    autocomplete_fields = ['tag']


class ForumThreadServiceInline(admin.TabularInline):
    model = ForumThreadService
    extra = 0
    autocomplete_fields = ['subservice']


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'author', 'status', 'is_pinned', 'like_count_display', 'reply_count', 'views', 'created_at']
    search_fields = ['title', 'slug', 'author__username', 'content']
    list_filter = ['category', 'status', 'is_pinned', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'slug', 'like_count_display', 'reply_count', 'views']
    autocomplete_fields = ['author', 'category']
    inlines = [ForumThreadTagInline, ForumThreadServiceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Status & Settings', {
            'fields': ('status', 'is_pinned')
        }),
        ('Statistics', {
            'fields': ('like_count_display', 'reply_count', 'views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_solved', 'mark_as_open', 'pin_threads', 'unpin_threads', 'close_threads']

    def like_count_display(self, obj):
        return obj.like_count
    like_count_display.short_description = 'Likes'

    def mark_as_solved(self, request, queryset):
        queryset.update(status='solved')
        self.message_user(request, f'{queryset.count()} threads marked as solved.')
    mark_as_solved.short_description = 'Mark as solved'

    def mark_as_open(self, request, queryset):
        queryset.update(status='open')
        self.message_user(request, f'{queryset.count()} threads marked as open.')
    mark_as_open.short_description = 'Mark as open'

    def pin_threads(self, request, queryset):
        queryset.update(is_pinned=True)
        self.message_user(request, f'{queryset.count()} threads pinned.')
    pin_threads.short_description = 'Pin selected'

    def unpin_threads(self, request, queryset):
        queryset.update(is_pinned=False)
        self.message_user(request, f'{queryset.count()} threads unpinned.')
    unpin_threads.short_description = 'Unpin selected'

    def close_threads(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f'{queryset.count()} threads closed.')
    close_threads.short_description = 'Close selected'


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'thread_title', 'author', 'is_best_answer', 'helpful_count_display', 'created_at']
    search_fields = ['content', 'author__username', 'thread__title']
    list_filter = ['is_best_answer', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'is_vendor_verified_display', 'helpful_count_display']
    autocomplete_fields = ['thread', 'author']
    fieldsets = (
        ('Thread & Author', {
            'fields': ('thread', 'author')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Status', {
            'fields': ('is_best_answer', 'is_vendor_verified_display')
        }),
        ('Statistics', {
            'fields': ('helpful_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_best_answer', 'remove_best_answer']

    def thread_title(self, obj):
        return obj.thread.title[:50] + '...' if len(obj.thread.title) > 50 else obj.thread.title
    thread_title.short_description = 'Thread'

    def is_vendor_verified_display(self, obj):
        return obj.is_vendor_verified
    is_vendor_verified_display.short_description = 'Vendor Verified'

    def helpful_count_display(self, obj):
        return obj.helpful_votes_count
    helpful_count_display.short_description = 'Helpful Votes'

    def mark_as_best_answer(self, request, queryset):
        queryset.update(is_best_answer=True)
        # Update thread status to solved
        for post in queryset:
            post.thread.status = 'solved'
            post.thread.save()
        self.message_user(request, f'{queryset.count()} posts marked as best answers.')
    mark_as_best_answer.short_description = 'Mark as best answer'

    def remove_best_answer(self, request, queryset):
        queryset.update(is_best_answer=False)
        self.message_user(request, f'{queryset.count()} posts removed from best answers.')
    remove_best_answer.short_description = 'Remove best answer'


@admin.register(ForumVote)
class ForumVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'vote_target', 'vote_type', 'created_at']
    search_fields = ['user__username']
    list_filter = ['vote_type', 'created_at']
    readonly_fields = ['created_at']
    autocomplete_fields = ['user', 'thread', 'post']

    def vote_target(self, obj):
        if obj.thread:
            return f"Thread: {obj.thread.title[:30]}..."
        elif obj.post:
            return f"Post by {obj.post.author.username}"
        return 'N/A'
    vote_target.short_description = 'Target'


# Customize admin site header and title
admin.site.site_header = 'BorewellMart Administration'
admin.site.site_title = 'BorewellMart Admin'
admin.site.index_title = 'Welcome to BorewellMart Admin Panel'


# ==================== Visitor Tracking Admin ====================

@admin.register(VisitorTracking)
class VisitorTrackingAdmin(admin.ModelAdmin):
    """Admin interface for visitor tracking"""
    list_display = ['identifier', 'user', 'ip_address', 'first_visit', 'last_visit', 'visit_count']
    list_filter = ['first_visit', 'last_visit']
    search_fields = ['session_key', 'ip_address', 'user__username', 'user_agent']
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'first_visit', 'last_visit']
    date_hierarchy = 'first_visit'

    def identifier(self, obj):
        if obj.user:
            return obj.user.username
        return obj.ip_address or 'Anonymous'
    identifier.short_description = 'Visitor'

    def has_add_permission(self, request):
        return False  # Only allow adding via middleware

    def has_change_permission(self, request, obj=None):
        return False  # Read-only


# ==================== Partner Admin ====================

class PartnerCouponInline(admin.TabularInline):
    model = PartnerCoupon
    extra = 0
    fields = ['code', 'is_active', 'max_uses', 'times_used', 'created_at']
    readonly_fields = ['times_used', 'created_at']


class PartnerReferralInline(admin.TabularInline):
    model = PartnerReferral
    extra = 0
    fields = ['vendor', 'source', 'coupon', 'created_at']
    readonly_fields = ['vendor', 'source', 'coupon', 'created_at']

    def has_add_permission(self, request, obj=None):
        return False


class PartnerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'referral_code', 'status', 'max_coupons', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['company_name', 'user__username', 'user__email', 'referral_code', 'phone']
    readonly_fields = ['referral_code', 'created_at']
    inlines = [PartnerCouponInline, PartnerReferralInline]


class PartnerCouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'partner', 'is_active', 'times_used', 'max_uses', 'created_at']
    list_filter = ['is_active', 'partner']
    search_fields = ['code', 'partner__company_name']


class PartnerReferralAdmin(admin.ModelAdmin):
    list_display = ['partner', 'vendor', 'source', 'coupon', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['partner__company_name', 'vendor__company_name']
    autocomplete_fields = ['vendor']

    def has_add_permission(self, request):
        return False


admin.site.register(Partner, PartnerAdmin)
admin.site.register(PartnerCoupon, PartnerCouponAdmin)
admin.site.register(PartnerReferral, PartnerReferralAdmin)


# ==================== Website Request Admin ====================

@admin.register(WebsiteRequest)
class WebsiteRequestAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'title', 'request_type', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'request_type', 'created_at']
    search_fields = ['vendor__company_name', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['vendor']
    
    fieldsets = (
        ('Vendor & Request', {
            'fields': ('vendor', 'request_type', 'title', 'description')
        }),
        ('Status & Notes', {
            'fields': ('status', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_in_progress', 'mark_as_rejected']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f'{queryset.count()} website requests marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f'{queryset.count()} website requests marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as in progress'
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} website requests marked as rejected.')
    mark_as_rejected.short_description = 'Mark as rejected'
