from django.shortcuts import redirect
from datetime import date
from django.utils import timezone


class VendorAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Check if the user is a vendor
                if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'vendor':
                    path = request.path

                    # Always allow logout, static files, media, and favicon
                    if path.startswith('/logout/') or path.startswith('/static/') or path.startswith('/media/') or path == '/favicon.ico':
                        return self.get_response(request)

                    # Paths that don't require plan check (registration, payment, plan selection)
                    plan_free_prefixes = [
                        '/vendor/register/',
                        '/vendor/payment/',
                        '/vendor/plans/',
                        '/api/create-order/',
                        '/api/verify-payment/',
                        '/api/cities-by-state/',
                        '/send-otp/',
                        '/verify-otp/',
                    ]

                    # Check if this is a plan-free path
                    for prefix in plan_free_prefixes:
                        if path.startswith(prefix):
                            return self.get_response(request)

                    # Get vendor profile
                    try:
                        vendor = request.user.vendor
                    except Exception:
                        # No vendor profile, redirect to registration
                        return redirect('vendor_register')

                    # Check if vendor is verified
                    if vendor.verification_status != 'verified':
                        if vendor.verification_status == 'pending':
                            from django.contrib import messages
                            messages.warning(request, 'Your account is pending admin verification.')
                        elif vendor.verification_status == 'suspended':
                            from django.contrib import messages
                            messages.error(request, 'Your account has been suspended. Please contact admin.')
                        return redirect('vendor_payment_page')

                    # Check if vendor has an active plan (trial or paid)
                    from core.models import VendorPlan
                    plan = VendorPlan.objects.filter(vendor=vendor).order_by('-created_at').first()

                    if not plan:
                        # No plan exists - redirect to plan selection
                        from django.contrib import messages
                        messages.info(request, 'Please select a plan to access vendor features.')
                        return redirect('vendor_plans')

                    # Update and check plan status
                    plan.update_status()

                    if plan.status == 'expired':
                        from django.contrib import messages
                        messages.error(request, 'Your plan has expired. Please renew to continue.')
                        return redirect('vendor_plans')

                    # Vendor has an active plan - allow access to all vendor paths
                    # No further restrictions needed
            except Exception:
                pass

        return self.get_response(request)


class VisitorTrackingMiddleware:
    """Track unique visitors to the website"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip tracking for admin, static, and media files
        skip_paths = ['/admin/', '/static/', '/media/', '/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)

        from .models import VisitorTracking

        # Get session key for anonymous users, user for authenticated
        session_key = None
        user = None
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        if request.user.is_authenticated:
            user = request.user
            session_key = request.session.session_key
        else:
            # Ensure session exists for anonymous visitors
            if not request.session.exists(request.session.session_key):
                request.session.create()
            session_key = request.session.session_key

        # Try to find existing visitor record
        visitor = None

        # First check by user (for authenticated users)
        if user:
            visitor = VisitorTracking.objects.filter(user=user).first()

        # If not found, check by session key
        if not visitor and session_key:
            visitor = VisitorTracking.objects.filter(session_key=session_key).first()

        # If still not found, check by IP (fallback)
        if not visitor and ip_address:
            visitor = VisitorTracking.objects.filter(
                ip_address=ip_address,
                user__isnull=True
            ).order_by('-last_visit').first()

        if visitor:
            # Update existing visitor
            visitor.last_visit = timezone.now()
            visitor.visit_count += 1
            if user:
                visitor.user = user
                visitor.session_key = session_key
            visitor.save(update_fields=['last_visit', 'visit_count', 'user', 'session_key'])
        else:
            # Create new visitor record
            VisitorTracking.objects.create(
                session_key=session_key,
                ip_address=ip_address,
                user=user,
                user_agent=user_agent
            )

        return self.get_response(request)

    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
