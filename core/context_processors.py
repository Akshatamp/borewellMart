from .models import SubService, Sector, Service, Enquiry, City


def services_context(request):
    """Provide hierarchical service structure for navigation"""
    sectors = Sector.objects.prefetch_related(
        'services__subservices'
    ).all().order_by('order')

    # Also provide services and subservices for other templates
    services = Service.objects.prefetch_related(
        'subservices'
    ).select_related('sector').all().order_by('sector__order', 'order')

    subservices = SubService.objects.select_related(
        'service__sector'
    ).all().order_by('service__sector__order', 'service__order', 'order')

    # Get all cities for the search bar
    cities = City.objects.all().order_by('name')

    return {
        'nav_sectors': sectors,
        'nav_services': services,
        'all_subservices': subservices,
        'all_cities': cities
    }


def notification_context(request):
    """Add notification counts to context for authenticated users"""
    notification_count = 0
    notification_type = None

    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile

            # For vendors: count pending enquiries
            if user_profile.user_type == 'vendor':
                try:
                    notification_count = Enquiry.objects.filter(
                        vendor=request.user.vendor,
                        status='pending'
                    ).count()
                    notification_type = 'enquiry'
                except:
                    notification_count = 0

            # For customers: count responded enquiries
            elif user_profile.user_type == 'customer':
                notification_count = Enquiry.objects.filter(
                    customer=request.user,
                    status='responded'
                ).count()
                notification_type = 'response'

        except:
            notification_count = 0

    return {
        'notification_count': notification_count,
        'notification_type': notification_type
    }


def base_template_context(request):
    """Determine the correct base template based on user type and path"""
    # Check if the request is for community or forum pages
    community_forum_paths = ['/communities/', '/forum/']

    # Default to base.html for most pages
    base_template = 'base.html'

    # Check if current path is for communities or forum
    is_community_forum = any(request.path.startswith(path) for path in community_forum_paths)

    if is_community_forum:
        if request.user.is_authenticated:
            try:
                user_profile = request.user.userprofile
                if user_profile.user_type == 'vendor':
                    base_template = 'vendor_base.html'
                elif user_profile.user_type == 'is_superuser':
                    base_template = 'admin/base.html'
            except:
                base_template = 'base.html'

    return {
        'base_template': base_template
    }
