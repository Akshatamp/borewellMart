from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import datetime
from datetime import date
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
import razorpay
import json
import hashlib
import hmac
from urllib.parse import quote
from .models import (
    City, SubService, Sector, Service, Vendor, VendorService, Booking, Review,
    UserProfile, VendorGallery, FavoriteVendor, Blog, Enquiry, VendorPayment, VendorPlan, PlanNotification, BookingPayment,
    ForumCategory, ForumThread, ForumPost, ForumVote, ForumTag, ForumThreadTag, ForumThreadService,
    Community, CommunityMember, CommunityPost, CommunityComment, CommunityLike,
    VendorEquipment, EquipmentInquiry, VisitorTracking,
    Partner, PartnerCoupon, PartnerReferral
)
from .forms import (
    UserRegisterForm, VendorUserRegisterForm, CustomerProfileForm, VendorProfileForm, VendorServiceForm,
    BookingForm, ReviewForm, VendorGalleryForm, CityForm, SubServiceForm, BlogForm,
    EnquiryForm, EnquiryResponseForm, BulkVendorRegistrationForm, BookingPaymentForm,
    ForumThreadForm, ForumPostForm, ForumCategoryForm, CommunityForm, CommunityPostForm, CommunityCommentForm,
    VendorEquipmentForm, EquipmentInquiryForm, PartnerUserRegisterForm, PartnerCouponForm
)
from .utils import (
    send_registration_email,
    send_vendor_registration_email,
    send_whatsapp_enquiry_notification,
    send_whatsapp_booking_confirmation,
    send_whatsapp_vendor_registration_notification,
    send_whatsapp_vendor_approval_notification,
    send_whatsapp_payment_completion_notification,
    send_whatsapp_plan_renewal_notification
)

# Try to import pandas for Excel processing
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def check_vendor_payment(vendor):
    """
    Helper function to check if vendor has completed payment.
    Returns tuple: (has_completed_payment, redirect_url)
    If payment is completed, returns (True, None)
    If payment is not completed, returns (False, 'vendor_payment_page')
    """
    try:
        payment = VendorPayment.objects.get(vendor=vendor)
        if payment.status == 'completed':
            return True, None
        else:
            return False, 'vendor_payment_page'
    except VendorPayment.DoesNotExist:
        return False, 'vendor_payment_page'


def check_vendor_verification(vendor):
    """
    Helper function to check if vendor is verified by admin.
    Returns tuple: (is_verified, redirect_url)
    If verified, returns (True, None)
    If not verified, returns (False, 'home')
    """
    if vendor.verification_status != 'verified':
        return False, 'home'
    return True, None


def get_request_payload(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return None
    return request.POST


def parse_order_amount_paise(payload):
    amount = payload.get('amount') if payload else None
    if amount in (None, ''):
        return None

    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        return None

    # API clients send paise. The existing vendor page sends rupees.
    if payload.get('amount_unit') == 'rupees':
        amount_value *= 100

    return int(round(amount_value))


def razorpay_api_error_response(exc):
    status_code = getattr(exc, 'status_code', None)
    error_payload = getattr(exc, 'error', {}) or {}
    description = error_payload.get('description') or str(exc) or 'Razorpay API error'
    response = {
        'error': 'Unable to create Razorpay order',
        'details': description,
        'key_id': settings.RAZORPAY_KEY_ID,
    }

    if status_code == 401 or 'auth' in description.lower():
        response['error'] = 'Razorpay authentication failed. Check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET, then restart the server.'
        return JsonResponse(response, status=401)

    return JsonResponse(response, status=500)


def verify_razorpay_signature(order_id, payment_id, razorpay_signature):
    message = f'{order_id}|{payment_id}'.encode('utf-8')
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
        message,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(generated_signature, razorpay_signature)


def check_vendor_plan(vendor):
    """
    Helper function to check if vendor has an active plan.
    Returns tuple: (has_active_plan, redirect_url, days_remaining)
    If has active plan, returns (True, None, days_remaining)
    If no active plan or expired, returns (False, 'vendor_plans', 0)
    """
    from datetime import date

    # Get the most recent plan for the vendor
    plan = VendorPlan.objects.filter(vendor=vendor).order_by('-created_at').first()

    if not plan:
        # No plan exists - redirect to create one
        return False, 'vendor_plans', 0

    # Update plan status if needed
    plan.update_status()

    if plan.status == 'expired':
        # Plan has expired - redirect to plans page
        return False, 'vendor_plans', 0

    # Plan is active - return days remaining
    days_remaining = plan.days_until_expiry()
    return True, None, days_remaining


def home(request):
    # Redirect admin users away from home page
    if request.user.is_authenticated:
        # Check for superuser first
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        # Vendors can stay on home page - they will be redirected when they try to access dashboard

    cities = City.objects.all()

    # Get unique states for filtering
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').order_by('state')

    # Get all services with their subservices
    services = Service.objects.prefetch_related(
        'subservices'
    ).select_related('sector').all().order_by('sector__order', 'order')

    # Also get sectors for filtering
    sectors = Sector.objects.prefetch_related('services').all()

    # Get all subservices for the search dropdown
    subservices = SubService.objects.select_related('service__sector').all()

    # Filter by user's city if logged in
    user_city = None
    if request.user.is_authenticated:
        try:
            user_city = request.user.userprofile.city
        except UserProfile.DoesNotExist:
            pass

    if user_city:
        featured_vendors = Vendor.objects.filter(
            city=user_city,
            verification_status='verified'
        ).annotate(
            booking_count=Count('bookings')
        ).order_by('-experience', '-rating', '-booking_count')[:6]
    else:
        featured_vendors = Vendor.objects.filter(
            verification_status='verified'
        ).annotate(
            booking_count=Count('bookings')
        ).order_by('-experience', '-rating', '-booking_count')[:6]

    context = {
        'cities': cities,
        'states': states,
        'sectors': sectors,
        'nav_sectors': sectors,
        'services': services,
        'subservices': subservices,
        'featured_vendors': featured_vendors,
        'user_city': user_city,
    }
    return render(request, 'home.html', context)


def city_list(request):
    # Get all cities, ordered by name
    cities = City.objects.all().order_by('name')

    # Get unique states from cities
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').exclude(state__isnull=True).order_by('state')

    # Filter by state if selected
    selected_state = request.GET.get('state')
    if selected_state:
        cities = cities.filter(state=selected_state)

    # Get featured vendors
    featured_vendors = Vendor.objects.filter(
        verification_status='verified'
    ).annotate(
        booking_count=Count('bookings')
    ).order_by('-experience', '-rating', '-booking_count')[:6]

    context = {
        'cities': cities,
        'states': states,
        'selected_state': selected_state,
        'featured_vendors': featured_vendors,
    }
    return render(request, 'cities.html', context)


def city_detail(request, city_id):
    city = get_object_or_404(City, id=city_id)
    sector_filter = request.GET.get('sector', 'all')
    service_filter = request.GET.get('service')

    # Filter vendors and subservices by sector/service
    if sector_filter == 'all':
        vendors = Vendor.objects.filter(city=city, verification_status='verified')
        subservices = SubService.objects.filter(vendor_services__vendor__city=city).distinct()
    elif sector_filter:
        vendors = Vendor.objects.filter(
            city=city,
            verification_status='verified',
            vendor_services__subservice__service__sector__id=sector_filter
        ).distinct()
        subservices = SubService.objects.filter(
            vendor_services__vendor__city=city,
            service__sector__id=sector_filter
        ).distinct()
    else:
        vendors = Vendor.objects.filter(city=city, verification_status='verified')
        subservices = SubService.objects.filter(vendor_services__vendor__city=city).distinct()

    # Further filter by service
    if service_filter:
        vendors = vendors.filter(vendor_services__subservice__service__id=service_filter).distinct()
        subservices = subservices.filter(service__id=service_filter).distinct()

    context = {
        'city': city,
        'vendors': vendors,
        'subservices': subservices,
        'sector_filter': sector_filter,
        'service_filter': service_filter,
        'sectors': Sector.objects.prefetch_related('services').all(),
    }
    return render(request, 'city_detail.html', context)


def service_list(request):
    # Get filter parameters
    sector_id = request.GET.get('sector')

    # Build the services queryset
    services = Service.objects.select_related('sector').all()

    # If filtering by sector
    if sector_id:
        services = services.filter(sector_id=sector_id)

    # Get featured vendors
    featured_vendors = Vendor.objects.filter(
        verification_status='verified'
    ).order_by('-experience', '-rating')[:6]

    context = {
        'services': services,
        'selected_sector': sector_id,
        'sectors': Sector.objects.all(),
        'nav_sectors': Sector.objects.prefetch_related('services').all(),
        'featured_vendors': featured_vendors,
    }
    return render(request, 'services.html', context)


def service_detail(request, service_id):
    # Fetch SubService (individual service item)
    service = get_object_or_404(SubService, id=service_id)

    # Get city from query parameter or user profile
    city_id = request.GET.get('city')
    user_city = None

    if city_id:
        # Use city from query parameter (from city_detail page)
        user_city = get_object_or_404(City, id=city_id)
    elif request.user.is_authenticated:
        # Fall back to user's profile city
        try:
            user_city = request.user.userprofile.city
        except UserProfile.DoesNotExist:
            pass

    # Filter vendors by the determined city if available
    if user_city:
        vendor_subservices = VendorService.objects.filter(
            subservice=service,
            vendor__verification_status='verified',
            vendor__city=user_city
        ).select_related('vendor', 'subservice').order_by('price')

        # If no vendors in user's city, get recommendations from nearby cities
        if not vendor_subservices.exists():
            nearby_cities = user_city.get_nearby_cities(limit=3)
            recommended_vendor_subservices = []
            for city in nearby_cities:
                city_vendor_subservices = VendorService.objects.filter(
                    subservice=service,
                    vendor__verification_status='verified',
                    vendor__city=city
                ).select_related('vendor', 'subservice').order_by('price')[:2]
                recommended_vendor_subservices.extend(city_vendor_subservices)

            context = {
                'service': service,
                'vendor_subservices': vendor_subservices,
                'user_city': user_city,
                'nearby_cities': nearby_cities,
                'recommended_vendor_subservices': recommended_vendor_subservices,
                'show_recommendations': True,
            }
        else:
            context = {
                'service': service,
                'vendor_subservices': vendor_subservices,
                'user_city': user_city,
                'show_recommendations': False,
            }
    else:
        vendor_subservices = VendorService.objects.filter(
            subservice=service,
            vendor__verification_status='verified'
        ).select_related('vendor', 'subservice').order_by('price')

        context = {
            'service': service,
            'vendor_subservices': vendor_subservices,
            'show_recommendations': False,
        }

    return render(request, 'service_detail.html', context)


def subcategory_detail(request, subcategory_id):
    """View all subservices within a service"""
    service = get_object_or_404(Service, id=subcategory_id)
    
    # Get subservices - separate parent subservices (categories) from leaf subservices
    parent_subservices = service.subservices.filter(parent=None).order_by('order')
    leaf_subservices = service.subservices.exclude(parent=None).order_by('order')
    
    # Get popular subservices for highlighting
    popular_subservices = service.subservices.filter(popular=True).order_by('order')

    # Get vendors that offer services in this category
    vendors = Vendor.objects.filter(
        verification_status='verified',
        vendor_services__subservice__service=service
    ).distinct().order_by('-rating', '-experience')

    context = {
        'service': service,
        'parent_subservices': parent_subservices,
        'leaf_subservices': leaf_subservices,
        'popular_subservices': popular_subservices,
        'sector': service.sector,
        'vendors': vendors,
    }
    return render(request, 'subcategory_detail.html', context)


def subservice_detail(request, subservice_id):
    """View child subservices of a parent subservice or vendors for leaf subservice"""
    subservice = get_object_or_404(SubService, id=subservice_id)
    
    # Check if this subservice has children (is a category)
    if subservice.children.exists():
        # Show child subservices
        child_subservices = subservice.children.all().order_by('order')
        
        context = {
            'subservice': subservice,
            'child_subservices': child_subservices,
            'service': subservice.service,
            'sector': subservice.service.sector,
        }
        return render(request, 'subservice_detail.html', context)
    else:
        # This is a leaf subservice - show vendors (redirect to service_detail)
        return service_detail(request, subservice_id)


def vendor_list(request):
    vendors = Vendor.objects.filter(verification_status='verified')

    # Get user's city if logged in
    user_city = None
    if request.user.is_authenticated:
        try:
            user_city = request.user.userprofile.city
        except UserProfile.DoesNotExist:
            pass

    state_filter = request.GET.get('state')
    city_filter = request.GET.get('city')
    subservice_filter = request.GET.get('subservice')
    sector_filter = request.GET.get('sector')
    service_filter = request.GET.get('service')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')
    sort_by = request.GET.get('sort_by')

    # Default to user's city if no filter specified and user is logged in
    if not city_filter and not state_filter and user_city:
        city_filter = user_city.id

    if state_filter:
        vendors = vendors.filter(city__state=state_filter)
    if city_filter:
        vendors = vendors.filter(city_id=city_filter)
    if subservice_filter:
        vendors = vendors.filter(vendor_services__subservice_id=subservice_filter).distinct()
    if sector_filter:
        vendors = vendors.filter(vendor_services__subservice__service__sector__id=sector_filter).distinct()
    if service_filter:
        vendors = vendors.filter(vendor_services__subservice__service__id=service_filter).distinct()
    if min_price:
        vendors = vendors.filter(vendor_services__price__gte=min_price).distinct()
    if max_price:
        vendors = vendors.filter(vendor_services__price__lte=max_price).distinct()
    if min_rating:
        vendors = vendors.filter(rating__gte=min_rating)

    if sort_by == 'popular':
        vendors = vendors.annotate(booking_count=Count('bookings')).order_by('-booking_count')
    elif sort_by == 'rating':
        vendors = vendors.order_by('-rating')
    elif sort_by == 'newest':
        vendors = vendors.order_by('-created_at')
    else:
        vendors = vendors.order_by('-experience', '-rating')

    # Get unique states from cities
    states = City.objects.values_list('state', flat=True).distinct().order_by('state')

    # Filter cities based on selected state
    if state_filter:
        cities = City.objects.filter(state=state_filter).order_by('name')
    else:
        cities = City.objects.all().order_by('name')

    subservices = SubService.objects.select_related('service__sector').all()
    sectors = Sector.objects.prefetch_related('services').all()

    # Get recommendations if no vendors found in user's city
    recommended_vendors = []
    show_recommendations = False
    if user_city and not vendors.exists() and not city_filter and not state_filter:
        nearby_cities = user_city.get_nearby_cities(limit=3)
        for city in nearby_cities:
            city_vendors = Vendor.objects.filter(
                city=city,
                verification_status='verified'
            ).order_by('-rating')[:2]
            recommended_vendors.extend(city_vendors)
        show_recommendations = True

    context = {
        'vendors': vendors,
        'states': states,
        'cities': cities,
        'subservices': subservices,
        'sectors': sectors,
        'selected_state': state_filter,
        'selected_city': city_filter,
        'selected_subservice': subservice_filter,
        'sector_filter': sector_filter,
        'service_filter': service_filter,
        'user_city': user_city,
        'recommended_vendors': recommended_vendors,
        'show_recommendations': show_recommendations,
    }
    return render(request, 'vendors.html', context)


def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor_services = vendor.vendor_services.all()
    gallery = vendor.gallery.all()
    reviews = Review.objects.filter(vendor=vendor).order_by('-created_at')
    available_subservices = SubService.objects.filter(per_feet_amount__isnull=False)

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteVendor.objects.filter(
            customer=request.user,
            vendor=vendor
        ).exists()

    context = {
        'vendor': vendor,
        'vendor_services': vendor_services,
        'gallery': gallery,
        'reviews': reviews,
        'is_favorite': is_favorite,
        'available_subservices': available_subservices,
    }
    return render(request, 'vendor_detail.html', context)


@login_required
def book_service(request, vendor_id, subservice_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    subservice = get_object_or_404(SubService, id=subservice_id)
    vendor_service = get_object_or_404(VendorService, vendor=vendor, subservice=subservice)

    # Superusers cannot book services
    if request.user.is_superuser:
        messages.error(request, 'Admins cannot book services.')
        return redirect('vendor_detail', vendor_id=vendor_id)

    # Get enquiry ID if booking from enquiry response
    enquiry_id = request.GET.get('enquiry')
    enquiry = None
    if enquiry_id:
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        # Validate that the enquiry belongs to the customer
        if enquiry.customer != request.user:
            messages.error(request, 'Access denied.')
            return redirect('customer_dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.vendor = vendor
            booking.subservice = subservice
            booking.enquiry = enquiry
            booking.is_emergency = request.POST.get('is_emergency') == 'on'
            try:
                booking.save()
                # Mark enquiry as closed after booking to remove from notifications
                if enquiry:
                    enquiry.status = 'closed'
                    enquiry.save()
                # Send WhatsApp notification to customer
                try:
                    send_whatsapp_booking_confirmation(booking)
                except Exception as e:
                    print(f"Failed to send WhatsApp booking confirmation: {e}")
                messages.success(request, 'Booking confirmed successfully!')
                return redirect('customer_dashboard')
            except:
                messages.error(request, 'A booking already exists for this date and time.')
    else:
        form = BookingForm()

    context = {
        'vendor': vendor,
        'subservice': subservice,
        'vendor_service': vendor_service,
        'form': form,
        'enquiry': enquiry,
    }
    return render(request, 'book_service.html', context)


@login_required
def booking_payment(request, booking_id):
    """Handle payment for a booking via UPI"""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    vendor = booking.vendor

    # Get or create payment record
    payment, created = BookingPayment.objects.get_or_create(
        booking=booking,
        defaults={'amount': 0}  # Will be set below
    )

    # Calculate amount from vendor service
    if created or payment.amount == 0:
        from core.models import VendorService
        vendor_service = VendorService.objects.filter(
            vendor=vendor,
            subservice=booking.subservice
        ).first()
        payment.amount = vendor_service.price if vendor_service else 0
        payment.save()

    payment_completed = payment.status == 'completed'
    qr_code_url = None

    if not payment_completed and getattr(vendor, 'upi_id', None):
        try:
            import base64
            from .utils import generate_booking_qr_code
            qr_code_file = generate_booking_qr_code(booking)
            # Convert to base64 for display in template
            qr_code_file.seek(0)  # Ensure we're at the beginning of the file
            qr_code_data = qr_code_file.read()
            qr_code_base64 = base64.b64encode(qr_code_data).decode('utf-8')
            qr_code_url = 'data:image/png;base64,' + qr_code_base64
        except ImportError as e:
            # qrcode library not installed
            messages.warning(request, f'QR code generation library not available: {e}')
        except Exception as e:
            # Log error but don't show to user
            import sys
            print(f"QR code generation error: {e}", file=sys.stderr)

    if request.method == 'POST':
        form = BookingPaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_method = 'upi'
            payment.status = 'pending'  # Will be verified by vendor/admin
            payment.save()

            messages.success(
                request,
                f'Payment details submitted! Your booking will be confirmed once the vendor verifies the payment. '
                f'Transaction ID: {payment.transaction_id}'
            )
            return redirect('customer_dashboard')
    else:
        form = BookingPaymentForm(instance=payment)

    context = {
        'booking': booking,
        'vendor': vendor,
        'payment': payment,
        'amount': payment.amount,
        'payment_completed': payment_completed,
        'qr_code_url': qr_code_url,
        'form': form,
    }
    return render(request, 'booking_payment.html', context)


@login_required
def customer_dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    favorite_vendors = FavoriteVendor.objects.filter(customer=request.user)
    
    total_bookings = bookings.count()
    active_bookings = bookings.filter(status__in=['pending', 'accepted', 'in_progress']).count()
    completed_bookings = bookings.filter(status='completed').count()
    
    # Get communities and user's memberships
    communities = Community.objects.filter(is_active=True).order_by('-created_at')
    user_communities = CommunityMember.objects.filter(
        user=request.user
    ).values_list('community_id', flat=True)

    context = {
        'profile': profile,
        'bookings': bookings,
        'favorite_vendors': favorite_vendors,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'communities': communities,
        'user_communities': user_communities,
    }
    return render(request, 'customer_dashboard.html', context)


@login_required
def customer_profile(request):
    """Display customer profile information"""
    profile = get_object_or_404(UserProfile, user=request.user)
    context = {
        'profile': profile,
    }
    return render(request, 'customer_profile.html', context)


@login_required
def customer_profile_edit(request):
    """Edit customer profile information"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.user.userprofile.user_type != 'customer':
        messages.error(request, 'Only customers can edit this profile.')
        return redirect('customer_profile')

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('customer_profile')
    else:
        form = CustomerProfileForm(instance=profile, user=request.user)

    return render(request, 'customer_profile_edit.html', {'form': form})


@login_required
def vendor_dashboard(request):
    """Vendor dashboard - requires active plan (trial or paid)"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not registered as a vendor.')
        return redirect('vendor_register')

    # Note: Verification and plan checks are now handled by middleware
    # If this view is reached, vendor is verified and has an active plan

    # Get vendor's current plan
    current_plan = VendorPlan.objects.filter(vendor=vendor).order_by('-created_at').first()
    days_remaining = current_plan.days_until_expiry() if current_plan and current_plan.status == 'active' else 0

    # Show warning if plan is expiring soon (3 days or less)
    if days_remaining <= 3 and days_remaining > 0:
        messages.warning(request, f'Your plan will expire in {days_remaining} day(s). Please renew to continue services.')
    elif days_remaining == 0:
        messages.error(request, 'Your plan has expired. Please renew to continue services.')

    # Get payment information to show on dashboard
    try:
        payment = VendorPayment.objects.get(vendor=vendor)
    except VendorPayment.DoesNotExist:
        payment = None

    bookings = Booking.objects.filter(vendor=vendor).order_by('-created_at')
    vendor_services = vendor.vendor_services.select_related('subservice__service__sector').order_by('subservice__service__sector__order', 'subservice__service__order', 'subservice__order')
    gallery = vendor.gallery.all()
    enquiries = Enquiry.objects.filter(vendor=vendor).order_by('-created_at')

    # Get sector filter from query parameter
    sector_filter = request.GET.get('sector', 'all')

    # Filter services by sector if specified
    if sector_filter != 'all':
        vendor_services = vendor_services.filter(subservice__service__sector__id=sector_filter)

    # Group services by sector and service
    grouped_services = {}
    for vs in vendor_services:
        sector = vs.subservice.service.sector
        service = vs.subservice.service

        if sector.name not in grouped_services:
            grouped_services[sector.name] = {
                'category': sector,
                'subcategories': {}
            }

        if service.name not in grouped_services[sector.name]['subcategories']:
            grouped_services[sector.name]['subcategories'][service.name] = {
                'subcategory': service,
                'services': []
            }

        grouped_services[sector.name]['subcategories'][service.name]['services'].append(vs)

    # Calculate total subservices count for each category
    for category_name in grouped_services:
        total_count = 0
        for subcategory_name in grouped_services[category_name]['subcategories']:
            total_count += len(grouped_services[category_name]['subcategories'][subcategory_name]['services'])
        grouped_services[category_name]['total_subservices'] = total_count

    total_bookings = bookings.count()
    pending_requests = bookings.filter(status='pending').count()
    completed_bookings = bookings.filter(status='completed').count()
    pending_enquiries = enquiries.filter(status='pending').count()

    monthly_earnings = 0
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    month_ago = timezone.now() - timedelta(days=30)

    # Calculate notification counts
    unread_notifications_count = pending_enquiries  # Pending enquiries count as notifications
    if days_remaining <= 3 and days_remaining > 0:
        unread_notifications_count += 1  # Add plan expiry warning
    elif days_remaining == 0:
        unread_notifications_count += 1  # Add plan expired notification

    # Get communities and user's memberships
    communities = Community.objects.filter(is_active=True).order_by('-created_at')
    user_communities = CommunityMember.objects.filter(
        user=request.user
    ).values_list('community_id', flat=True)

    context = {
        'vendor': vendor,
        'bookings': bookings,
        'grouped_services': grouped_services,
        'gallery': gallery,
        'enquiries': enquiries,
        'total_bookings': total_bookings,
        'pending_requests': pending_requests,
        'completed_bookings': completed_bookings,
        'pending_enquiries': pending_enquiries,
        'monthly_earnings': monthly_earnings,
        'payment': payment,
        'registration_amount': 999.00,
        'sector_filter': sector_filter,
        'sectors': Sector.objects.all().order_by('order'),
        'current_plan': current_plan,
        'days_remaining': days_remaining,
        'pending_enquiries_count': pending_enquiries,
        'unread_notifications_count': unread_notifications_count,
        'communities': communities,
        'user_communities': user_communities,
    }
    return render(request, 'vendor_dashboard.html', context)


@login_required
def vendor_communities(request):
    """Vendor communities page - requires active plan (trial or paid)"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not registered as a vendor.')
        return redirect('vendor_register')

    # Note: Plan check is now handled by middleware
    # Vendors without a plan are automatically redirected to vendor_plans

    # Get communities and user's memberships
    communities = Community.objects.filter(is_active=True).annotate(
        total_posts=Count('posts')
    ).order_by('-created_at')

    user_communities = list(CommunityMember.objects.filter(
        user=request.user
    ).values_list('community_id', flat=True))

    # Get vendor's current plan for display
    current_plan = VendorPlan.objects.filter(vendor=vendor).order_by('-created_at').first()
    days_remaining = current_plan.days_until_expiry() if current_plan and current_plan.status == 'active' else 0

    context = {
        'vendor': vendor,
        'communities': communities,
        'user_communities': user_communities,
        'current_plan': current_plan,
        'days_remaining': days_remaining,
    }
    return render(request, 'vendor_communities.html', context)


@login_required
def vendor_bookings(request):
    """Vendor bookings page - requires active plan"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not registered as a vendor.')
        return redirect('vendor_register')

    # Note: Verification and plan checks are handled by middleware
    bookings = Booking.objects.filter(vendor=vendor).select_related('customer', 'subservice').order_by('-created_at')

    # Calculate notification counts
    pending_enquiries = Enquiry.objects.filter(vendor=vendor, status='pending').count()
    unread_notifications_count = pending_enquiries

    context = {
        'vendor': vendor,
        'bookings': bookings,
        'total_bookings': bookings.count(),
        'pending_requests': bookings.filter(status='pending').count(),
        'completed_bookings': bookings.filter(status='completed').count(),
        'pending_enquiries_count': pending_enquiries,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'vendor_bookings.html', context)


@login_required
def vendor_services(request):
    """Vendor services page - requires active plan"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not registered as a vendor.')
        return redirect('vendor_register')

    # Note: Verification and plan checks are handled by middleware
    vendor_services = vendor.vendor_services.select_related('subservice__service__sector').order_by('subservice__service__sector__order', 'subservice__service__order', 'subservice__order')

    # Get sector filter from query parameter
    sector_filter = request.GET.get('sector', 'all')

    # Filter services by sector if specified
    if sector_filter != 'all':
        vendor_services = vendor_services.filter(subservice__service__sector__id=sector_filter)

    # Group services by sector and service
    grouped_services = {}
    for vs in vendor_services:
        sector = vs.subservice.service.sector
        service = vs.subservice.service

        if sector.name not in grouped_services:
            grouped_services[sector.name] = {
                'category': sector,
                'subcategories': {}
            }

        if service.name not in grouped_services[sector.name]['subcategories']:
            grouped_services[sector.name]['subcategories'][service.name] = {
                'subcategory': service,
                'services': []
            }

        grouped_services[sector.name]['subcategories'][service.name]['services'].append(vs)

    # Calculate total subservices count for each category
    for category_name in grouped_services:
        total_count = 0
        for subcategory_name in grouped_services[category_name]['subcategories']:
            total_count += len(grouped_services[category_name]['subcategories'][subcategory_name]['services'])
        grouped_services[category_name]['total_subservices'] = total_count

    # Calculate notification counts
    pending_enquiries = Enquiry.objects.filter(vendor=vendor, status='pending').count()
    unread_notifications_count = pending_enquiries

    context = {
        'vendor': vendor,
        'grouped_services': grouped_services,
        'pending_enquiries_count': pending_enquiries,
        'unread_notifications_count': unread_notifications_count,
        'sector_filter': sector_filter,
        'sectors': Sector.objects.all().order_by('order'),
    }

    # Return JSON for AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'includes/service_cards.html', context)

    return render(request, 'vendor_services.html', context)


@login_required
def vendor_profile_edit(request):
    """Edit vendor profile - requires active plan"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('vendor_register')

    # Note: Verification and plan checks are handled by middleware
    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('vendor_services')
    else:
        form = VendorProfileForm(instance=vendor)
    
    return render(request, 'vendor_profile_edit.html', {'form': form})


@login_required
def vendor_service_add(request):
    """Add a service for vendor - requires active plan"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('vendor_register')

    # Note: Verification and plan checks are handled by middleware
    if request.method == 'POST':
        form = VendorServiceForm(request.POST)
        if form.is_valid():
            selected_sector = form.cleaned_data.get('sector')
            selected_service = form.cleaned_data.get('service')
            service_name_input = form.cleaned_data.get('service_name')
            subservice_name_input = form.cleaned_data.get('subservice_name')

            if selected_service:
                service = selected_service
            else:
                service = Service.objects.filter(
                    name__iexact=service_name_input,
                    sector=selected_sector
                ).first()

                if not service:
                    unique_id = f"{selected_sector.id.lower().replace(' ', '_')}_{service_name_input.lower().replace(' ', '_')}"
                    service = Service.objects.create(
                        id=unique_id,
                        name=service_name_input,
                        sector=selected_sector,
                        order=999,
                        slug=f"{unique_id}"
                    )

            existing_subservice = SubService.objects.filter(
                name__iexact=subservice_name_input,
                service=service
            ).first()

            if existing_subservice:
                subservice = existing_subservice
                messages.info(request, f'Service "{subservice.name}" already exists for "{service.name}" and has been added to your services.')
            else:
                # Generate unique ID for subservice
                import uuid
                unique_id = f"sub_{uuid.uuid4().hex[:8]}"
                subservice = SubService.objects.create(
                    id=unique_id,
                    name=subservice_name_input,
                    service=service,
                    description=f'{subservice_name_input} service'
                )
                messages.success(request, f'New subservice "{subservice.name}" has been created under "{selected_sector.name} - {service.name}" and added to your services.')

            # Check if vendor already has this subservice
            if VendorService.objects.filter(vendor=vendor, subservice=subservice).exists():
                messages.error(request, f'This subservice "{subservice.name}" is already added to your profile.')
                return redirect('vendor_service_add')

            try:
                VendorService.objects.create(
                    vendor=vendor,
                    subservice=subservice,
                    description=form.cleaned_data.get('description', '')
                )
                return redirect('vendor_services')
            except Exception:
                messages.error(request, 'This service is already added to your profile.')
    else:
        form = VendorServiceForm()

    # Get sectors, services and subservices for the form
    sectors = Sector.objects.all().order_by('order')
    services = Service.objects.select_related('sector').all().order_by('sector__order', 'order')
    subservices = SubService.objects.select_related('service__sector').all().order_by('service__sector__order', 'service__order', 'name')

    context = {
        'form': form,
        'action': 'Add',
        'sectors': sectors,
        'services': services,
        'subservices': subservices,
    }
    return render(request, 'vendor_service_form.html', context)


@login_required
def vendor_service_edit(request, service_id):
    """Edit a vendor service - requires active plan"""
    try:
        vendor = request.user.vendor
        vendor_service = get_object_or_404(VendorService, id=service_id, vendor=vendor)
    except Vendor.DoesNotExist:
        return redirect('vendor_register')

    # Note: Verification and plan checks are handled by middleware
    if request.method == 'POST':
        form = VendorServiceForm(request.POST, instance=vendor_service)
        if form.is_valid():
            selected_sector = form.cleaned_data.get('sector')
            selected_service = form.cleaned_data.get('service')
            service_name_input = form.cleaned_data.get('service_name')
            subservice_name_input = form.cleaned_data.get('subservice_name')

            if selected_service:
                service = selected_service
            else:
                service = Service.objects.filter(
                    name__iexact=service_name_input,
                    sector=selected_sector
                ).first()

                if not service:
                    unique_id = f"{selected_sector.id.lower().replace(' ', '_')}_{service_name_input.lower().replace(' ', '_')}"
                    service = Service.objects.create(
                        id=unique_id,
                        name=service_name_input,
                        sector=selected_sector,
                        order=999,
                        slug=f"{unique_id}"
                    )

            if isinstance(subservice_name_input, SubService):
                subservice = subservice_name_input
            else:
                # Generate unique ID for subservice
                import uuid
                unique_id = f"sub_{uuid.uuid4().hex[:8]}"
                subservice = SubService.objects.create(
                    id=unique_id,
                    name=subservice_name_input,
                    service=service,
                    description=f'{subservice_name_input} service'
                )

            vendor_service.subservice = subservice
            vendor_service.description = form.cleaned_data.get('description', '')
            vendor_service.save()

            messages.success(request, 'Service updated successfully!')
            return redirect('vendor_dashboard')
    else:
        form = VendorServiceForm(instance=vendor_service)

    # Get sectors, services and subservices for filtering
    sectors = Sector.objects.all().order_by('order')
    services = Service.objects.select_related('sector').all().order_by('sector__order', 'order')
    subservices = SubService.objects.select_related('service__sector').all().order_by('service__sector__order', 'service__order', 'name')

    context = {
        'form': form,
        'action': 'Edit',
        'sectors': sectors,
        'services': services,
        'subservices': subservices,
    }
    return render(request, 'vendor_service_form.html', context)


@login_required
def vendor_service_delete(request, service_id):
    """Delete a vendor service - requires active plan"""
    try:
        vendor = request.user.vendor
        vendor_service = get_object_or_404(VendorService, id=service_id, vendor=vendor)

        # Note: Verification and plan checks are handled by middleware
        vendor_service.delete()
        messages.success(request, 'Service deleted successfully!')
    except Vendor.DoesNotExist:
        pass

    return redirect('vendor_services')


@login_required
def vendor_gallery_add(request):
    """Add image to vendor gallery - requires active plan"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return redirect('vendor_register')

    # Note: Verification and plan checks are handled by middleware
    if request.method == 'POST':
        form = VendorGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_item = form.save(commit=False)
            gallery_item.vendor = vendor
            gallery_item.save()
            messages.success(request, 'Image added to gallery!')
            return redirect('vendor_dashboard')
    else:
        form = VendorGalleryForm()
    
    return render(request, 'vendor_gallery_form.html', {'form': form})


@login_required
def vendor_gallery_delete(request, gallery_id):
    """Delete image from vendor gallery - requires active plan"""
    try:
        vendor = request.user.vendor
        gallery_item = get_object_or_404(VendorGallery, id=gallery_id, vendor=vendor)

        # Note: Verification and plan checks are handled by middleware
        gallery_item.delete()
        messages.success(request, 'Image removed from gallery!')
    except Vendor.DoesNotExist:
        pass

    return redirect('vendor_dashboard')


@login_required
def booking_update_status(request, booking_id, status):
    """Update booking status - requires active plan"""
    try:
        vendor = request.user.vendor
        booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)

        # Note: Verification and plan checks are handled by middleware
        allowed_statuses = [choice[0] for choice in Booking.STATUS_CHOICES]
        if status not in allowed_statuses:
            messages.error(request, 'Invalid booking status.')
            return redirect('vendor_bookings')

        booking.status = status
        booking.save()
        messages.success(request, f'Booking status updated to {status}.')
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not authorized to update this booking.')

    return redirect(request.META.get('HTTP_REFERER', 'vendor_bookings'))


@login_required
def add_favorite(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    FavoriteVendor.objects.get_or_create(customer=request.user, vendor=vendor)
    messages.success(request, 'Vendor added to favorites!')
    return redirect('vendor_detail', vendor_id=vendor_id)


@login_required
def remove_favorite(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    FavoriteVendor.objects.filter(customer=request.user, vendor=vendor).delete()
    messages.success(request, 'Vendor removed from favorites!')
    return redirect('vendor_detail', vendor_id=vendor_id)


@login_required
def add_review(request, vendor_id, booking_id=None):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.vendor = vendor
            if booking_id:
                review.booking = get_object_or_404(Booking, id=booking_id)
            review.save()
            vendor.update_rating()
            messages.success(request, 'Review submitted successfully!')
            return redirect('vendor_detail', vendor_id=vendor_id)
    else:
        form = ReviewForm()
    
    context = {
        'vendor': vendor,
        'form': form,
        'booking_id': booking_id,
    }
    return render(request, 'add_review.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # This is the customer registration page - force the account type.
            # Vendor/partner signups must use their dedicated pages
            # (/register/vendor/ and /register/partner/) which track referrals.
            profile = user.userprofile
            if profile.user_type != 'customer':
                profile.user_type = 'customer'
                profile.save(update_fields=['user_type'])
            login(request, user)
            messages.success(request, 'Registration successful!')

            # Send registration email
            try:
                send_registration_email(user, user_type='customer')
            except Exception as e:
                # Log error but don't prevent registration
                print(f"Failed to send registration email: {e}")

            return redirect('home')
    else:
        form = UserRegisterForm()

    # Get unique states for the dropdown
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').exclude(state__isnull=True).order_by('state')

    return render(request, 'register.html', {
        'form': form,
        'states': states
    })


def customer_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Ensure user_type is customer
            profile = user.userprofile
            profile.user_type = 'customer'
            profile.save()
            login(request, user)
            messages.success(request, 'Customer registration successful!')

            # Send registration email
            try:
                send_registration_email(user, user_type='customer')
            except Exception as e:
                # Log error but don't prevent registration
                print(f"Failed to send registration email: {e}")

            return redirect('home')
    else:
        form = UserRegisterForm()

    # Get unique states for the dropdown
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').exclude(state__isnull=True).order_by('state')
    states_list = list(states)
    print(f"DEBUG: States being passed to template: {states_list[:5]}... (total: {len(states_list)})")

    return render(request, 'customer_register.html', {
        'form': form,
        'states': states
    })


def register_choice(request):
    """Render the registration choice page with customer, vendor and partner options."""
    return render(request, 'register_choice.html')


def _record_partner_referral(request, vendor):
    """Create a permanent PartnerReferral if a referral code/coupon was used.
    Priority: coupon code entered by vendor > referral link stored in session."""
    code = (request.POST.get('referral_code') or '').strip().upper()
    if not code:
        code = (request.session.get('partner_ref_code') or '').strip().upper()

    if not code:
        return None

    coupon = PartnerCoupon.objects.filter(code=code).select_related('partner').first()
    if coupon and coupon.is_available:
        referral = PartnerReferral.objects.create(
            partner=coupon.partner,
            vendor=vendor,
            source='coupon',
            coupon=coupon,
        )
        PartnerCoupon.objects.filter(pk=coupon.pk).update(times_used=coupon.times_used + 1)
        request.session.pop('partner_ref_code', None)
        return referral

    partner = Partner.objects.filter(referral_code=code, status='active').first()
    if partner:
        referral = PartnerReferral.objects.create(
            partner=partner,
            vendor=vendor,
            source='link',
        )
        request.session.pop('partner_ref_code', None)
        return referral

    return None


def vendor_user_register(request):
    # Capture referral code from ?ref= link into session
    ref_code = request.GET.get('ref', '').strip().upper()
    if ref_code:
        request.session['partner_ref_code'] = ref_code

    if request.method == 'POST':
        form = VendorUserRegisterForm(request.POST)
        email = request.POST.get('email')

        # Check if email is verified in session
        if not email or request.session.get('otp_verified_email') != email:
            messages.error(request, 'Please verify your email address using OTP first.')
            states = City.objects.values_list('state', flat=True).distinct().exclude(state='').exclude(state__isnull=True).order_by('state')
            return render(request, 'vendor_user_register.html', {
                'form': form,
                'states': states,
                'referral_code': request.session.get('partner_ref_code', ''),
            })

        if form.is_valid():
            user = form.save()
            login(request, user)

            # Permanently record partner attribution (referral link or coupon)
            try:
                referral = _record_partner_referral(request, user.vendor)
                if referral:
                    messages.info(request, f'Referral code applied successfully. Referred by {referral.partner.company_name}.')
            except Exception as e:
                print(f"Failed to record partner referral: {e}")

            # Clear verified OTP data from session
            request.session.pop('otp_verified_email', None)
            request.session.pop('otp_code', None)
            request.session.pop('otp_email', None)
            request.session.pop('otp_timestamp', None)

            messages.success(request, 'Vendor registration successful! Your profile is pending verification.')

            # Send vendor registration email
            try:
                company_name = form.cleaned_data.get('company_name')
                send_vendor_registration_email(user, company_name)
            except Exception as e:
                # Log error but don't prevent registration
                print(f"Failed to send vendor registration email: {e}")

            # Send WhatsApp notification to vendor
            try:
                vendor = user.vendor
                send_whatsapp_vendor_registration_notification(vendor)
            except Exception as e:
                # Log error but don't prevent registration
                print(f"Failed to send WhatsApp vendor registration notification: {e}")

            return redirect('vendor_dashboard')
    else:
        form = VendorUserRegisterForm()

    # Get unique states for the dropdown
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').exclude(state__isnull=True).order_by('state')

    return render(request, 'vendor_user_register.html', {
        'form': form,
        'states': states,
        'referral_code': request.session.get('partner_ref_code', ''),
    })


def custom_login(request):
    # If user is already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        try:
            if request.user.userprofile.user_type == 'partner':
                return redirect('partner_dashboard')
            if request.user.userprofile.user_type == 'vendor':
                try:
                    vendor = request.user.vendor
                    return redirect('vendor_dashboard')
                except Vendor.DoesNotExist:
                    return redirect('vendor_register')
            elif request.user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('vendor_list')
        except UserProfile.DoesNotExist:
            return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Check for superuser first
            if user.is_superuser:
                return redirect('admin_dashboard')

            try:
                if user.userprofile.user_type == 'partner':
                    try:
                        if user.partner_profile.status == 'suspended':
                            from django.contrib.auth import logout
                            logout(request)
                            messages.error(request, 'Your partner account has been suspended. Please contact admin.')
                            return redirect('login')
                    except Partner.DoesNotExist:
                        pass
                    return redirect('partner_dashboard')
                if user.userprofile.user_type == 'vendor':
                    try:
                        vendor = user.vendor
                        return redirect('vendor_dashboard')
                    except Vendor.DoesNotExist:
                        return redirect('vendor_register')
                else:
                    return redirect('vendor_list')
            except UserProfile.DoesNotExist:
                return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def custom_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')


# ==================== Partner Views ====================

def partner_required(view_func):
    """Decorator: user must be logged in and have a partner profile"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if request.user.userprofile.user_type != 'partner':
                messages.error(request, 'Access denied. Partner account required.')
                return redirect('home')
            partner = request.user.partner_profile
        except (UserProfile.DoesNotExist, Partner.DoesNotExist):
            messages.error(request, 'Partner profile not found.')
            return redirect('home')
        return view_func(request, partner, *args, **kwargs)
    return wrapper


def partner_user_register(request):
    if request.method == 'POST':
        form = PartnerUserRegisterForm(request.POST)
        email = request.POST.get('email')

        # Check if email is verified in session
        if not email or request.session.get('otp_verified_email') != email:
            messages.error(request, 'Please verify your email address using OTP first.')
            return render(request, 'partner_user_register.html', {'form': form})

        if form.is_valid():
            user = form.save()
            login(request, user)

            # Clear verified OTP data from session
            request.session.pop('otp_verified_email', None)
            request.session.pop('otp_code', None)
            request.session.pop('otp_email', None)
            request.session.pop('otp_timestamp', None)

            messages.success(request, 'Partner registration successful! Your account is pending admin approval.')

            try:
                send_registration_email(user, user_type='partner')
            except Exception as e:
                print(f"Failed to send partner registration email: {e}")

            return redirect('partner_dashboard')
    else:
        form = PartnerUserRegisterForm()

    return render(request, 'partner_user_register.html', {'form': form})


@partner_required
def partner_dashboard(request, partner):
    referrals = partner.referrals.select_related('vendor__user', 'vendor__payment', 'coupon').all()

    total_referrals = referrals.count()
    converted_referrals = referrals.filter(vendor__payment__status='completed').count()
    pending_vendors = referrals.filter(vendor__verification_status='pending').count()
    verified_vendors = referrals.filter(vendor__verification_status='verified').count()

    coupons = partner.coupons.annotate(
        referral_count=Count('referrals')
    ).order_by('-created_at')

    total_coupon_uses = sum(c.times_used for c in coupons)

    referral_link = partner.get_referral_link(request)
    base = settings.FRONTEND_URL.rstrip('/')

    def wa_share(text):
        return f'https://wa.me/?text={quote(text)}'

    whatsapp_text = (
        f"Hello! Register your borewell business on BorewellMart - India's trusted borewell marketplace. "
        f"Use my referral link: {referral_link}"
    )

    coupon_share_data = []
    for c in coupons:
        coupon_link = f"{base}/register/vendor/?ref={c.code}"
        c.share_link = coupon_link
        c.share_whatsapp = wa_share(
            f"Register your borewell business on BorewellMart with my coupon code {c.code}.\n\n"
            f"Open link: {coupon_link}"
        )

    context = {
        'partner': partner,
        'referral_link': referral_link,
        'whatsapp_share_url': wa_share(whatsapp_text),
        'total_referrals': total_referrals,
        'converted_referrals': converted_referrals,
        'pending_vendors': pending_vendors,
        'verified_vendors': verified_vendors,
        'coupons': coupons,
        'total_coupon_uses': total_coupon_uses,
        'referrals': referrals,
        'coupon_form': PartnerCouponForm(),
        'coupon_limit_reached': coupons.count() >= partner.max_coupons,
    }
    return render(request, 'partner/dashboard.html', context)


@partner_required
def partner_coupon_add(request, partner):
    if request.method != 'POST':
        return redirect('partner_dashboard')

    if partner.coupons.count() >= partner.max_coupons:
        messages.error(request, f'You have reached your coupon limit ({partner.max_coupons}).')
        return redirect('partner_dashboard')

    form = PartnerCouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data.get('code') or None
        max_uses = form.cleaned_data.get('max_uses')
        if code and (PartnerCoupon.objects.filter(code=code).exists() or Partner.objects.filter(referral_code=code).exists()):
            form.add_error('code', 'This code is already in use. Please choose another.')
            messages.error(request, 'This code is already in use.')
            return redirect('partner_dashboard')
        coupon = PartnerCoupon.objects.create(partner=partner, code=code, max_uses=max_uses)
        messages.success(request, f'Coupon "{coupon.code}" created successfully!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
    return redirect('partner_dashboard')


@partner_required
def partner_coupon_delete(request, partner, coupon_id):
    if request.method != 'POST':
        return redirect('partner_dashboard')

    coupon = get_object_or_404(PartnerCoupon, pk=coupon_id, partner=partner)
    coupon.delete()
    messages.success(request, f'Coupon "{coupon.code}" deleted.')
    return redirect('partner_dashboard')


# ==================== Admin Partner Management ====================

def _admin_required(view_func):
    """Decorator: user must be a superuser"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@_admin_required
def admin_partners(request):
    """Admin page: manage partners and their activity"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            company_name = request.POST.get('company_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            max_coupons = int(request.POST.get('max_coupons') or 10)

            if not all([username, email, password, company_name, phone]):
                messages.error(request, 'All fields are required to create a partner.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
            else:
                with transaction.atomic():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    UserProfile.objects.create(user=user, phone=phone, user_type='partner')
                    Partner.objects.create(
                        user=user, company_name=company_name, phone=phone,
                        max_coupons=max_coupons, status='active',
                    )
                messages.success(request, f'Partner "{company_name}" created and activated.')

        elif action == 'status':
            partner = get_object_or_404(Partner, pk=request.POST.get('partner_id'))
            new_status = request.POST.get('status')
            if new_status in dict(Partner.STATUS_CHOICES):
                partner.status = new_status
                partner.save(update_fields=['status'])
                messages.success(request, f'{partner.company_name} is now {new_status}.')

        elif action == 'max_coupons':
            partner = get_object_or_404(Partner, pk=request.POST.get('partner_id'))
            try:
                partner.max_coupons = max(0, int(request.POST.get('max_coupons')))
                partner.save(update_fields=['max_coupons'])
                messages.success(request, f'Coupon limit updated for {partner.company_name}.')
            except (TypeError, ValueError):
                messages.error(request, 'Invalid coupon limit.')

        elif action == 'delete':
            partner = get_object_or_404(Partner, pk=request.POST.get('partner_id'))
            partner.user.delete()  # cascades to Partner, UserProfile
            messages.success(request, f'Partner "{partner.company_name}" deleted.')

        return redirect('admin_partners')

    partners = Partner.objects.select_related('user').prefetch_related('referrals', 'coupons').order_by('-created_at')
    partner_stats = []
    for p in partners:
        partner_stats.append({
            'partner': p,
            'total_referrals': p.referrals.count(),
            'converted': p.referrals.filter(vendor__payment__status='completed').count(),
            'coupon_count': p.coupons.count(),
        })

    recent_referrals = PartnerReferral.objects.select_related('partner', 'vendor', 'coupon').order_by('-created_at')[:20]

    context = {
        'partner_stats': partner_stats,
        'recent_referrals': recent_referrals,
        'total_partners': partners.count(),
        'active_partners': partners.filter(status='active').count(),
        'total_referrals': PartnerReferral.objects.count(),
        'total_conversions': PartnerReferral.objects.filter(vendor__payment__status='completed').count(),
    }
    return render(request, 'admin/partners.html', context)


@_admin_required
def admin_coupons(request):
    """Admin page: manage all partner coupons"""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            partner = get_object_or_404(Partner, pk=request.POST.get('partner_id'))
            code = request.POST.get('code', '').strip().upper() or None
            max_uses = request.POST.get('max_uses') or None
            if code and (PartnerCoupon.objects.filter(code=code).exists() or Partner.objects.filter(referral_code=code).exists()):
                messages.error(request, 'This code is already in use.')
            else:
                PartnerCoupon.objects.create(partner=partner, code=code, max_uses=max_uses)
                messages.success(request, 'Coupon created successfully.')

        elif action == 'toggle':
            coupon = get_object_or_404(PartnerCoupon, pk=request.POST.get('coupon_id'))
            coupon.is_active = not coupon.is_active
            coupon.save(update_fields=['is_active'])
            messages.success(request, f'Coupon "{coupon.code}" {"activated" if coupon.is_active else "deactivated"}.')

        elif action == 'delete':
            coupon = get_object_or_404(PartnerCoupon, pk=request.POST.get('coupon_id'))
            coupon.delete()
            messages.success(request, f'Coupon "{coupon.code}" deleted.')

        return redirect('admin_coupons')

    coupons = PartnerCoupon.objects.select_related('partner__user').annotate(
        referral_count=Count('referrals')
    ).order_by('-created_at')
    partners = Partner.objects.filter(status='active').order_by('company_name')

    context = {
        'coupons': coupons,
        'partners': partners,
    }
    return render(request, 'admin/coupons.html', context)


@login_required
def vendor_payment_page(request):
    """Display payment page for vendor registration fee"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, 'Please complete your vendor registration first.')
        return redirect('vendor_register')

    # Check if payment already exists
    payment = VendorPayment.objects.filter(vendor=vendor).first()

    if payment and payment.status == 'completed':
        # Show payment completion status for both verified and unverified vendors
        if vendor.verification_status != 'verified':
            messages.info(request, 'Your payment is completed. Your account is pending admin verification. You will be able to access the dashboard once approved.')
        
        # Show payment status page without creating new order
        context = {
            'payment': payment,
            'vendor': vendor,
            'amount': payment.amount,
            'payment_completed': True,
        }
        return render(request, 'vendor_payment.html', context)

    # Validate Razorpay credentials before creating order
    razorpay_key_id = settings.RAZORPAY_KEY_ID
    razorpay_key_secret = settings.RAZORPAY_KEY_SECRET
    if not razorpay_key_id or not razorpay_key_secret:
        messages.error(request, 'Razorpay payment is not configured. Please contact site administrator.')
        return render(request, 'vendor_payment.html', {'error': True})

    context = {
        'payment': payment,
        'vendor': vendor,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_currency': 'INR',
        'callback_url': request.build_absolute_uri('/vendor/payment/callback/'),
        'payment_completed': False,
    }
    return render(request, 'vendor_payment.html', context)


@csrf_exempt
@login_required
def create_razorpay_order(request):
    """Create Razorpay order dynamically based on selected amount."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)

    payload = get_request_payload(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    amount_in_paise = parse_order_amount_paise(payload)
    if amount_in_paise is None:
        return JsonResponse({'error': 'Amount is required'}, status=400)

    if amount_in_paise < 100:
        return JsonResponse({'error': 'Minimum amount is 100 paise'}, status=400)

    allowed_amounts_paise = [100, 99900, 499900, 899900]
    if amount_in_paise not in allowed_amounts_paise:
        return JsonResponse({'error': 'Invalid amount selected'}, status=400)

    razorpay_key_id = settings.RAZORPAY_KEY_ID
    razorpay_key_secret = settings.RAZORPAY_KEY_SECRET
    if not razorpay_key_id or not razorpay_key_secret:
        return JsonResponse({'error': 'Razorpay not configured'}, status=401)

    razorpay_client = razorpay.Client(
        auth=(razorpay_key_id, razorpay_key_secret)
    )

    currency = payload.get('currency') or settings.RAZORPAY_CURRENCY
    receipt = payload.get('receipt') or f'vendor_{vendor.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}'

    # Debug logging
    import sys
    print(f"Creating Razorpay order: amount={amount_in_paise}, currency={currency}, receipt={receipt}", file=sys.stderr)

    try:
        razorpay_order = razorpay_client.order.create({
            'amount': amount_in_paise,
            'currency': currency,
            'receipt': receipt,
            'payment_capture': 1,  # Integer, not string
            'notes': {
                'vendor_id': vendor.id,
                'company_name': vendor.company_name,
                'selected_amount': amount_in_paise // 100,
            }
        })
        print(f"[PAYMENT INFO] Razorpay order created: {razorpay_order['id']} for vendor: {vendor.company_name}", file=sys.stderr)
    except Exception as exc:
        print(f"[PAYMENT ERROR] Failed to create Razorpay order: {exc}", file=sys.stderr)
        return razorpay_api_error_response(exc)

    amount = amount_in_paise / 100

    # Check if there's an existing pending payment for this vendor
    existing_pending_payment = VendorPayment.objects.filter(
        vendor=vendor,
        status='pending'
    ).first()

    if existing_pending_payment:
        # Update the existing pending payment with new order details
        payment = existing_pending_payment
        payment.amount = amount
        payment.razorpay_order_id = razorpay_order['id']
        payment.payment_method = 'razorpay'
        payment.save()
        print(f"[PAYMENT INFO] Updated existing pending payment for vendor: {vendor.company_name}, order_id: {razorpay_order['id']}", file=sys.stderr)
    else:
        # Create new payment record
        payment = VendorPayment.objects.create(
            vendor=vendor,
            amount=amount,
            status='pending',
            razorpay_order_id=razorpay_order['id'],
            payment_method='razorpay'
        )
        print(f"[PAYMENT INFO] Created new payment record for vendor: {vendor.company_name}, order_id: {razorpay_order['id']}", file=sys.stderr)

    return JsonResponse({
        'order_id': razorpay_order['id'],
        'amount': amount_in_paise,
        'currency': currency,
    })


@csrf_exempt
@login_required
def verify_razorpay_payment(request):
    """Verify Razorpay payment signature and mark the vendor payment completed."""
    import sys
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    payload = get_request_payload(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    razorpay_payment_id = payload.get('razorpay_payment_id')
    razorpay_order_id = payload.get('razorpay_order_id')
    razorpay_signature = payload.get('razorpay_signature')

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        print(f"[PAYMENT ERROR] Missing payment verification fields. payment_id: {razorpay_payment_id}, order_id: {razorpay_order_id}, signature: {bool(razorpay_signature)}", file=sys.stderr)
        return JsonResponse({'error': 'Missing payment verification fields'}, status=400)

    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        print(f"[PAYMENT ERROR] Vendor not found for user: {request.user.username}", file=sys.stderr)
        return JsonResponse({'error': 'Vendor not found'}, status=404)

    # Get payment by razorpay_order_id instead of vendor to avoid mismatch
    try:
        payment = VendorPayment.objects.get(razorpay_order_id=razorpay_order_id)
    except VendorPayment.DoesNotExist:
        print(f"[PAYMENT ERROR] Payment not found for order_id: {razorpay_order_id}", file=sys.stderr)
        # Try to find payment by vendor as fallback
        try:
            payment = VendorPayment.objects.get(vendor=vendor)
            print(f"[PAYMENT WARNING] Found payment by vendor instead of order_id. Payment order_id: {payment.razorpay_order_id}, Request order_id: {razorpay_order_id}", file=sys.stderr)
        except VendorPayment.DoesNotExist:
            print(f"[PAYMENT ERROR] No payment found for vendor: {vendor.company_name}", file=sys.stderr)
            return JsonResponse({'error': 'Payment record not found'}, status=404)

    # Verify the payment belongs to this vendor
    if payment.vendor != vendor:
        print(f"[PAYMENT ERROR] Payment vendor mismatch. Payment vendor: {payment.vendor.company_name}, Current vendor: {vendor.company_name}", file=sys.stderr)
        return JsonResponse({'error': 'Payment vendor mismatch'}, status=403)

    if not settings.RAZORPAY_KEY_SECRET:
        print(f"[PAYMENT ERROR] Razorpay not configured", file=sys.stderr)
        return JsonResponse({'error': 'Razorpay not configured'}, status=401)

    # Verify signature
    if not verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        print(f"[PAYMENT ERROR] Signature verification failed for order_id: {razorpay_order_id}, payment_id: {razorpay_payment_id}", file=sys.stderr)
        payment.status = 'failed'
        payment.gateway_response = {
            'status': 'signature_mismatch',
            'order_id': razorpay_order_id,
            'payment_id': razorpay_payment_id,
        }
        payment.save()
        return JsonResponse({'error': 'Payment verification failed - signature mismatch'}, status=400)

    # Mark payment as completed
    try:
        payment.mark_completed(
            transaction_id=razorpay_payment_id,
            paid_amount=payment.amount,
            gateway_response={
                'status': 'success',
                'order_id': razorpay_order_id,
                'payment_id': razorpay_payment_id,
            }
        )
        print(f"[PAYMENT SUCCESS] Payment completed for vendor: {vendor.company_name}, amount: {payment.amount}, transaction_id: {razorpay_payment_id}", file=sys.stderr)
    except Exception as e:
        print(f"[PAYMENT ERROR] Failed to mark payment as completed: {e}", file=sys.stderr)
        return JsonResponse({'error': f'Failed to complete payment: {str(e)}'}, status=500)

    # Auto-approve vendor and create trial plan after successful payment
    vendor.verification_status = 'verified'
    vendor.save()
    print(f"[PAYMENT INFO] Vendor {vendor.company_name} marked as verified", file=sys.stderr)

    # Create trial plan for vendor after successful payment if no plan exists
    from datetime import timedelta
    existing_plan = VendorPlan.objects.filter(vendor=vendor).first()
    if not existing_plan:
        trial_start = date.today()
        trial_end = trial_start + timedelta(days=7)
        trial_plan = VendorPlan.objects.create(
            vendor=vendor,
            plan_type='basic',
            plan_name='Trial Plan (7 Days)',
            price=0,
            start_date=trial_start,
            end_date=trial_end,
            status='active',
            description='Free trial plan for 7 days. Upgrade to continue services.'
        )
        print(f"[PAYMENT INFO] Trial plan created for vendor: {vendor.company_name}, valid until: {trial_end}", file=sys.stderr)
    else:
        print(f"[PAYMENT INFO] Vendor {vendor.company_name} already has a plan, skipping trial creation", file=sys.stderr)

    messages.success(
        request,
        f'Payment of Rs. {payment.amount} completed successfully! '
        f'Your account is now active and approved. '
        f'Transaction ID: {razorpay_payment_id}'
    )

    return JsonResponse({
        'success': True,
        'redirect_url': str(reverse_lazy('vendor_dashboard')),
    })


@csrf_exempt
def vendor_payment_callback(request):
    """Handle Razorpay payment callback"""
    import sys
    if request.method != 'POST':
        print(f"[PAYMENT CALLBACK] Invalid method: {request.method}", file=sys.stderr)
        return redirect('vendor_payment_page')

    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        print(f"[PAYMENT CALLBACK] Vendor not found for user: {request.user.username if request.user.is_authenticated else 'anonymous'}", file=sys.stderr)
        messages.error(request, 'Please complete your vendor registration first.')
        return redirect('vendor_register')

    # Get payment by razorpay_order_id from POST data
    razorpay_order_id = request.POST.get('razorpay_order_id')
    if razorpay_order_id:
        try:
            payment = VendorPayment.objects.get(razorpay_order_id=razorpay_order_id)
            # Verify the payment belongs to this vendor
            if payment.vendor != vendor:
                print(f"[PAYMENT CALLBACK] Payment vendor mismatch. Payment vendor: {payment.vendor.company_name}, Current vendor: {vendor.company_name}", file=sys.stderr)
                messages.error(request, 'Payment vendor mismatch.')
                return redirect('vendor_payment_page')
        except VendorPayment.DoesNotExist:
            print(f"[PAYMENT CALLBACK] Payment not found for order_id: {razorpay_order_id}", file=sys.stderr)
            # Fallback to getting payment by vendor
            payment = get_object_or_404(VendorPayment, vendor=vendor)
    else:
        payment = get_object_or_404(VendorPayment, vendor=vendor)

    if payment.status == 'completed':
        print(f"[PAYMENT CALLBACK] Payment already completed for vendor: {vendor.company_name}", file=sys.stderr)
        messages.warning(request, 'Payment has already been completed.')
        return redirect('vendor_dashboard')

    # Get payment details from Razorpay callback
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    print(f"[PAYMENT CALLBACK] Processing payment for vendor: {vendor.company_name}, payment_id: {razorpay_payment_id}, order_id: {razorpay_order_id}", file=sys.stderr)

    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
        print(f"[PAYMENT CALLBACK] Missing payment details. payment_id: {razorpay_payment_id}, order_id: {razorpay_order_id}, signature: {bool(razorpay_signature)}", file=sys.stderr)
        messages.error(request, 'Invalid payment details. Please try again.')
        return redirect('vendor_payment_page')

    # Verify payment signature
    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        # Verify signature
        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        razorpay_client.utility.verify_payment_signature(params)
        print(f"[PAYMENT CALLBACK] Signature verified successfully for order: {razorpay_order_id}", file=sys.stderr)

        # Update payment record
        payment.mark_completed(
            transaction_id=razorpay_payment_id,
            paid_amount=payment.amount,
            gateway_response={
                'status': 'success',
                'order_id': razorpay_order_id,
                'payment_id': razorpay_payment_id
            }
        )
        print(f"[PAYMENT CALLBACK] Payment marked as completed for vendor: {vendor.company_name}, amount: {payment.amount}", file=sys.stderr)

        # Auto-approve vendor after successful payment (no admin approval needed)
        vendor.verification_status = 'verified'
        vendor.save()
        print(f"[PAYMENT CALLBACK] Vendor {vendor.company_name} marked as verified", file=sys.stderr)

        # Create trial plan for vendor after successful payment if no plan exists
        from datetime import timedelta
        existing_plan = VendorPlan.objects.filter(vendor=vendor).first()
        if not existing_plan:
            trial_start = date.today()
            trial_end = trial_start + timedelta(days=7)
            trial_plan = VendorPlan.objects.create(
                vendor=vendor,
                plan_type='basic',
                plan_name='Trial Plan (7 Days)',
                price=0,
                start_date=trial_start,
                end_date=trial_end,
                status='active',
                description='Free trial plan for 7 days. Upgrade to continue services.'
            )
            print(f"[PAYMENT CALLBACK] Trial plan created for vendor: {vendor.company_name}, valid until: {trial_end}", file=sys.stderr)
        else:
            print(f"[PAYMENT CALLBACK] Vendor {vendor.company_name} already has a plan, skipping trial creation", file=sys.stderr)

        # Send WhatsApp notification for payment completion with approval
        try:
            send_whatsapp_payment_completion_notification(vendor, payment.amount)
        except Exception as e:
            print(f"[PAYMENT CALLBACK] Failed to send WhatsApp payment completion notification: {e}", file=sys.stderr)

        messages.success(
            request,
            f'Payment of ₹{payment.amount} completed successfully! '
            f'Your account is now active and approved. '
            f'Transaction ID: {razorpay_payment_id}'
        )
        return redirect('vendor_dashboard')

    except razorpay.errors.SignatureVerificationError as e:
        print(f"[PAYMENT CALLBACK] Signature verification error: {e}", file=sys.stderr)
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('vendor_payment_page')
    except Exception as e:
        print(f"[PAYMENT CALLBACK] Payment processing error: {e}", file=sys.stderr)
        messages.error(request, f'Payment processing error: {str(e)}')
        return redirect('vendor_payment_page')


@login_required
def vendor_register(request):
    # Capture referral code from ?ref= link into session (step-2 completion flow)
    ref_code = request.GET.get('ref', '').strip().upper()
    if ref_code:
        request.session['partner_ref_code'] = ref_code

    try:
        vendor = request.user.vendor
        return redirect('vendor_dashboard')
    except (Vendor.DoesNotExist, AttributeError):
        pass

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()

            # Record partner attribution (referral link session or coupon code field)
            try:
                referral = _record_partner_referral(request, vendor)
                if referral:
                    messages.info(request, f'Referral code applied successfully. Referred by {referral.partner.company_name}.')
            except Exception as e:
                print(f"Failed to record partner referral: {e}")

            messages.success(request, 'Vendor registration submitted! Please complete the payment to activate your account.')
            return redirect('vendor_payment_page')
    else:
        form = VendorProfileForm()

    return render(request, 'vendor_register.html', {
        'form': form,
        'referral_code': request.session.get('partner_ref_code', ''),
    })


def search(request):
    query = request.GET.get('q', '')
    state = request.GET.get('state')
    city_id = request.GET.get('city')
    sector_id = request.GET.get('sector')
    service_id = request.GET.get('service')
    subservice_id = request.GET.get('subservice')

    vendors = Vendor.objects.filter(verification_status='verified')

    if query:
        vendors = vendors.filter(
            Q(company_name__icontains=query) |
            Q(address__icontains=query) |
            Q(vendor_services__subservice__name__icontains=query) |
            Q(vendor_services__subservice__description__icontains=query) |
            Q(vendor_services__subservice__service__name__icontains=query) |
            Q(vendor_services__subservice__service__id__icontains=query) |
            Q(vendor_services__subservice__service__sector__name__icontains=query) |
            Q(vendor_services__subservice__service__sector__id__icontains=query)
        ).distinct()

    if state:
        vendors = vendors.filter(city__state=state)

    if city_id:
        vendors = vendors.filter(city_id=city_id)

    if sector_id:
        vendors = vendors.filter(vendor_services__subservice__service__sector_id=sector_id).distinct()

    if service_id:
        vendors = vendors.filter(vendor_services__subservice__service_id=service_id).distinct()

    if subservice_id:
        vendors = vendors.filter(vendor_services__subservice_id=subservice_id).distinct()

    cities = City.objects.all()
    subservices = SubService.objects.all()

    context = {
        'vendors': vendors,
        'cities': cities,
        'subservices': subservices,
        'query': query,
        'selected_state': state,
        'selected_city': city_id,
        'selected_sector': sector_id,
        'selected_service': service_id,
        'selected_subservice': subservice_id,
    }
    return render(request, 'search_results.html', context)


def blog_list(request):
    blogs = Blog.objects.filter(slug__isnull=False).exclude(slug='').order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': blogs})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, 'blog_detail.html', {'blog': blog})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def borewell_faqs(request):
    """Borewell FAQs page"""
    return render(request, 'borewell_faqs.html')


@login_required
def send_enquiry(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        form = EnquiryForm(request.POST, vendor=vendor)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.customer = request.user
            enquiry.vendor = vendor
            enquiry.save()

            # Send WhatsApp notification to the vendor
            success, result = send_whatsapp_enquiry_notification(enquiry)
            if not success:
                print(f'WhatsApp notification failed: {result}')
                print(f'Vendor phone: {vendor.phone}')
                print(f'WhatsApp settings configured: {bool(settings.WHATSAPP_CLOUD_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID)}')
            else:
                print(f'WhatsApp notification sent successfully to {vendor.phone}')

            messages.success(request, 'Enquiry sent successfully! The vendor will respond with detailed pricing.')
            return redirect('vendor_detail', vendor_id=vendor_id)
    else:
        form = EnquiryForm(vendor=vendor)
        subservice_id = request.GET.get('subservice')
        if subservice_id:
            form.initial['subservice'] = subservice_id

    context = {
        'vendor': vendor,
        'form': form,
    }
    return render(request, 'send_enquiry.html', context)


@login_required
def vendor_enquiries(request):
    """Vendor enquiries page - requires active plan"""
    try:
        vendor = request.user.vendor
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not registered as a vendor.')
        return redirect('home')

    # Note: Verification and plan checks are handled by middleware
    enquiries = Enquiry.objects.filter(vendor=vendor).order_by('-created_at')
    pending_enquiries = enquiries.filter(status='pending').count()
    unread_notifications_count = pending_enquiries

    context = {
        'vendor': vendor,
        'enquiries': enquiries,
        'pending_enquiries': pending_enquiries,
        'pending_enquiries_count': pending_enquiries,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'vendor_enquiries.html', context)


@login_required
def respond_enquiry(request, enquiry_id):
    """Respond to an enquiry - requires active plan"""
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)

    # Check if the logged-in user is the vendor for this enquiry
    try:
        vendor = request.user.vendor
        if vendor != enquiry.vendor:
            messages.error(request, 'You are not authorized to respond to this enquiry.')
            return redirect('vendor_enquiries')
    except Vendor.DoesNotExist:
        messages.error(request, 'You are not registered as a vendor.')
        return redirect('home')

    # Note: Verification and plan checks are handled by middleware
    if request.method == 'POST':
        form = EnquiryResponseForm(request.POST, instance=enquiry)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.status = 'responded'
            enquiry.save()

            # Send WhatsApp notification to the customer
            try:
                from .utils import send_whatsapp_customer_response_notification
                success, result = send_whatsapp_customer_response_notification(enquiry)
                if not success:
                    print('Customer WhatsApp notification failed:', result)
            except Exception as e:
                print('Customer WhatsApp notification error:', e)

            messages.success(request, 'Response sent successfully!')
            return redirect('vendor_enquiries')
    else:
        form = EnquiryResponseForm(instance=enquiry)
    
    context = {
        'enquiry': enquiry,
        'form': form,
    }
    return render(request, 'respond_enquiry.html', context)


@login_required
def customer_enquiries(request):
    enquiries = Enquiry.objects.filter(customer=request.user).order_by('-created_at')

    context = {
        'enquiries': enquiries,
    }
    return render(request, 'customer_enquiries.html', context)


@login_required
def notifications(request):
    """Unified notifications page for both customers and vendors"""
    user_profile = request.user.userprofile

    if user_profile.user_type == 'vendor':
        # Ensure user is registered as vendor before showing notifications
        try:
            vendor = request.user.vendor
        except Vendor.DoesNotExist:
            messages.error(request, 'Please complete your vendor registration first.')
            return redirect('vendor_register')

        # Note: Verification and plan checks are handled by middleware

        # Vendors see pending enquiries
        notifications_list = Enquiry.objects.filter(
            vendor=request.user.vendor,
            status='pending'
        ).order_by('-created_at')
        title = 'Pending Enquiries'
        empty_message = 'No pending enquiries.'

    elif user_profile.user_type == 'customer':
        # Customers see responded enquiries
        notifications_list = Enquiry.objects.filter(
            customer=request.user,
            status='responded'
        ).order_by('-created_at')
        title = 'Vendor Responses'
        empty_message = 'No new responses from vendors yet.'

    else:
        notifications_list = []
        title = 'Notifications'
        empty_message = 'No notifications.'

    context = {
        'notifications': notifications_list,
        'title': title,
        'empty_message': empty_message,
        'user_type': user_profile.user_type,
    }
    return render(request, 'notifications.html', context)


@login_required
def dismiss_notification(request, enquiry_id):
    """Dismiss a notification by marking the enquiry as closed"""
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    user_profile = request.user.userprofile

    # Only allow customers to dismiss their own notifications
    if user_profile.user_type == 'customer' and enquiry.customer == request.user:
        enquiry.status = 'closed'
        enquiry.save()
        messages.success(request, 'Notification dismissed.')

    return redirect('notifications')


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    # Get all data for admin to manage
    total_vendors = Vendor.objects.count()
    total_customers = UserProfile.objects.filter(user_type='customer').count()
    total_subservices = SubService.objects.count()
    total_cities = City.objects.count()
    total_bookings = Booking.objects.count()
    total_enquiries = Enquiry.objects.count()
    pending_vendors = Vendor.objects.filter(verification_status='pending').count()

    # Service hierarchy statistics
    total_sectors = Sector.objects.count()
    total_services = Service.objects.count()

    # Vendor service associations
    total_vendor_services = VendorService.objects.count()

    # Reviews and blogs
    total_reviews = Review.objects.count()
    total_blogs = Blog.objects.count()

    # Verification status breakdown
    verified_vendors = Vendor.objects.filter(verification_status='verified').count()
    suspended_vendors = Vendor.objects.filter(verification_status='suspended').count()

    # Payment statistics
    total_payments = VendorPayment.objects.count()
    completed_payments = VendorPayment.objects.filter(status='completed').count()
    pending_payments = VendorPayment.objects.filter(status='pending').count()
    total_revenue = VendorPayment.objects.filter(status='completed').aggregate(
        total=Sum('paid_amount')
    )['total'] or 0

    # Booking status breakdown
    pending_bookings = Booking.objects.filter(status='pending').count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    active_bookings = Booking.objects.filter(status__in=['accepted', 'in_progress']).count()

    # Enquiry status breakdown
    pending_enquiries = Enquiry.objects.filter(status='pending').count()
    responded_enquiries = Enquiry.objects.filter(status='responded').count()

    recent_vendors = Vendor.objects.order_by('-created_at')[:5]
    recent_bookings = Booking.objects.order_by('-created_at')[:5]
    recent_enquiries = Enquiry.objects.order_by('-created_at')[:5]
    recent_reviews = Review.objects.order_by('-created_at')[:5]

    # Get all pending vendors for verification
    all_pending_vendors = Vendor.objects.filter(verification_status='pending').order_by('-created_at')

    # Visitor tracking statistics
    total_visitors = VisitorTracking.objects.count()
    today_visitors = VisitorTracking.objects.filter(
        first_visit__date=date.today()
    ).count()
    unique_visitors = VisitorTracking.objects.count()  # All records are unique
    repeat_visitors = VisitorTracking.objects.filter(visit_count__gt=1).count()

    # Get sectors with their service and subservice counts
    sectors_with_stats = []
    for sector in Sector.objects.prefetch_related('services__subservices').all():
        service_count = sector.services.count()
        subservice_count = SubService.objects.filter(service__sector=sector).count()
        sectors_with_stats.append({
            'sector': sector,
            'service_count': service_count,
            'subservice_count': subservice_count
        })

    context = {
        'total_vendors': total_vendors,
        'total_customers': total_customers,
        'total_subservices': total_subservices,
        'total_cities': total_cities,
        'total_bookings': total_bookings,
        'total_enquiries': total_enquiries,
        'pending_vendors': pending_vendors,
        'total_sectors': total_sectors,
        'total_services': total_services,
        'total_vendor_services': total_vendor_services,
        'total_reviews': total_reviews,
        'total_blogs': total_blogs,
        'verified_vendors': verified_vendors,
        'suspended_vendors': suspended_vendors,
        'pending_bookings': pending_bookings,
        'completed_bookings': completed_bookings,
        'active_bookings': active_bookings,
        'pending_enquiries': pending_enquiries,
        'responded_enquiries': responded_enquiries,
        'recent_vendors': recent_vendors,
        'recent_bookings': recent_bookings,
        'recent_enquiries': recent_enquiries,
        'recent_reviews': recent_reviews,
        'all_pending_vendors': all_pending_vendors,
        'sectors_with_stats': sectors_with_stats,
        'total_payments': total_payments,
        'completed_payments': completed_payments,
        'pending_payments': pending_payments,
        'total_revenue': total_revenue,
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'unique_visitors': unique_visitors,
        'repeat_visitors': repeat_visitors,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def approve_vendor(request, vendor_id):
    """Approve a vendor account and create trial plan"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.verification_status = 'verified'
    vendor.save()

    # Create 7-day trial plan for the vendor
    from datetime import timedelta
    trial_start = date.today()
    trial_end = trial_start + timedelta(days=7)

    # Check if vendor already has ANY plan (active, expired, or cancelled)
    existing_plan = VendorPlan.objects.filter(
        vendor=vendor
    ).first()

    # Only create trial plan if vendor has no existing plans
    if not existing_plan:
        trial_plan = VendorPlan.objects.create(
            vendor=vendor,
            plan_type='basic',
            plan_name='Trial Plan (7 Days)',
            price=0,
            start_date=trial_start,
            end_date=trial_end,
            status='active',
            description='Free trial plan for 7 days. Upgrade to continue services.'
        )
        plan_created = True
    else:
        trial_plan = existing_plan
        plan_created = False

    # Send WhatsApp notification to approved vendor
    try:
        print(f"[DEBUG] Sending WhatsApp approval notification to: {vendor.company_name}, Phone: {vendor.phone}")
        success, response = send_whatsapp_vendor_approval_notification(vendor)
        print(f"[DEBUG] WhatsApp notification result - Success: {success}, Response: {response}")
        if not success:
            print(f"[ERROR] Failed to send WhatsApp to {vendor.company_name}: {response}")
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp approval notification: {e}")

    # Approval email disabled for vendor accounts

    if plan_created:
        messages.success(request, f'Vendor {vendor.company_name} has been approved! Trial plan created until {trial_end}.')
    else:
        messages.success(request, f'Vendor {vendor.company_name} has been approved! They already have an existing plan.')

    return redirect('admin_dashboard')


@login_required
def reject_vendor(request, vendor_id):
    """Reject a vendor account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.verification_status = 'suspended'
    vendor.save()

    # Send rejection email to vendor
    try:
        from .utils import send_vendor_rejection_email
        send_vendor_rejection_email(vendor)
    except Exception as e:
        print(f"Failed to send vendor rejection email: {e}")

    messages.success(request, f'Vendor {vendor.company_name} has been rejected!')
    return redirect('admin_dashboard')


@login_required
def suspend_vendor(request, vendor_id):
    """Suspend a vendor account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.verification_status = 'suspended'
    vendor.save()

    messages.success(request, f'Vendor {vendor.company_name} has been suspended!')
    return redirect('admin_dashboard')


@login_required
def activate_vendor(request, vendor_id):
    """Activate a suspended vendor account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.verification_status = 'verified'
    vendor.save()

    messages.success(request, f'Vendor {vendor.company_name} has been activated!')
    return redirect('admin_dashboard')


@login_required
def delete_vendor(request, vendor_id):
    """Delete a vendor account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    company_name = vendor.company_name
    vendor.delete()

    messages.success(request, f'Vendor {company_name} has been deleted!')
    return redirect('admin_dashboard')


@login_required
def admin_vendor_edit(request, vendor_id):
    """Edit a vendor's profile (admin view)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    vendor = get_object_or_404(Vendor, id=vendor_id)
    cities = City.objects.all()

    if request.method == 'POST':
        # Update basic fields
        vendor.company_name = request.POST.get('company_name')
        vendor.email = request.POST.get('email')
        vendor.phone = request.POST.get('phone')
        vendor.city_id = request.POST.get('city')
        vendor.experience = request.POST.get('experience')
        vendor.address = request.POST.get('address')
        vendor.license_number = request.POST.get('license_number', '')
        vendor.certifications = request.POST.get('certifications', '')
        vendor.verification_status = request.POST.get('verification_status')
        vendor.is_emergency_available = 'is_emergency_available' in request.POST
        vendor.rating = request.POST.get('rating', 0) or 0

        # Handle file uploads
        if 'logo' in request.FILES:
            vendor.logo = request.FILES['logo']
        if 'cover_image' in request.FILES:
            vendor.cover_image = request.FILES['cover_image']

        vendor.save()
        messages.success(request, f'Vendor {vendor.company_name} has been updated!')
        return redirect('admin_all_vendors')

    # Get recent bookings for this vendor
    recent_bookings = vendor.bookings.select_related('subservice__service__sector').order_by('-date')[:5]

    context = {
        'vendor': vendor,
        'cities': cities,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/vendor_edit.html', context)


@login_required
def vendor_payments_list(request):
    """View all vendor payments for admin"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    status_filter = request.GET.get('status', 'all')
    method_filter = request.GET.get('method')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    page = request.GET.get('page', 1)

    payments = VendorPayment.objects.select_related('vendor__city').all()

    if status_filter != 'all':
        payments = payments.filter(status=status_filter)

    if method_filter:
        method_filter = (method_filter or '').strip().lower()
        if method_filter in {'razorpay', 'stripe', 'bank_transfer', 'upi', 'other', 'cash', 'card', 'net_banking'}:
            payments = payments.filter(gateway_response__icontains=method_filter)

    if date_from:
        payments = payments.filter(created_at__gte=date_from)

    if date_to:
        payments = payments.filter(created_at__lte=date_to)

    payments = payments.order_by('-created_at')

    # Pagination - 10 payments per page
    paginator = Paginator(payments, 10)
    payments_page = paginator.get_page(page)

    # Statistics (calculated on all payments, not filtered)
    all_payments = VendorPayment.objects.all()
    stats = {
        'total': all_payments.count(),
        'pending': all_payments.filter(status='pending').count(),
        'completed': all_payments.filter(status='completed').count(),
        'failed': all_payments.filter(status='failed').count(),
        'revenue': all_payments.filter(status='completed').aggregate(
            total=Sum('paid_amount')
        )['total'] or 0,
        'pending_amount': all_payments.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'failed_amount': all_payments.filter(status='failed').aggregate(
            total=Sum('amount')
        )['total'] or 0,
    }

    context = {
        'payments': payments_page,
        'status_filter': status_filter,
        'stats': stats,
    }
    return render(request, 'admin/payments.html', context)


@login_required
def vendor_payment_detail(request, payment_id):
    """View and manage a specific vendor payment"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    payment = get_object_or_404(VendorPayment, id=payment_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'mark_completed':
            transaction_id = request.POST.get('transaction_id', f'ADMIN_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}')
            payment.mark_completed(transaction_id=transaction_id)
            messages.success(request, f'Payment marked as completed. Vendor account verified.')

        elif action == 'mark_failed':
            payment.status = 'failed'
            payment.notes = request.POST.get('notes', '')
            payment.save()
            messages.warning(request, f'Payment marked as failed.')

        elif action == 'refund':
            payment.status = 'refunded'
            payment.notes = request.POST.get('notes', '')
            payment.save()
            messages.info(request, f'Payment refunded.')

        elif action == 'delete':
            vendor = payment.vendor
            payment.delete()
            messages.success(request, f'Payment record deleted.')
            return redirect('vendor_payments_list')

        return redirect('vendor_payment_detail', payment_id=payment.id)

    context = {
        'payment': payment,
        'vendor': payment.vendor,
    }
    return render(request, 'admin/payment_detail.html', context)


@login_required
def all_vendors(request):
    """View all vendors with filtering options"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    status_filter = request.GET.get('status', 'all')
    city_filter = request.GET.get('city')
    state_filter = request.GET.get('state')
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', 1)

    if state_filter in ['', 'None', 'null', 'undefined']:
        state_filter = None

    if city_filter in ['', 'None', 'null', 'undefined']:
        city_filter = None

    # Include plan information and vendor services in the query
    vendors = Vendor.objects.select_related('city').prefetch_related(
        'plans',
        'vendor_services__subservice__service__sector'
    ).all()

    if status_filter != 'all':
        vendors = vendors.filter(verification_status=status_filter)

    if state_filter:
        vendors = vendors.filter(Q(state=state_filter) | Q(city__state=state_filter))

    if city_filter:
        vendors = vendors.filter(city_id=city_filter)

    if search_query:
        vendors = vendors.filter(
            Q(company_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    vendors = vendors.order_by('-created_at')

    # Pagination - 10 vendors per page
    paginator = Paginator(vendors, 10)
    vendors_page = paginator.get_page(page)

    # Annotate each vendor with plan information and auto-create trial plans
    from datetime import timedelta

    for vendor in vendors_page:
        # Get the most recent plan for this vendor
        vendor.current_plan = vendor.plans.first()

        # Get service sectors for this vendor
        vendor.service_sectors = []
        if vendor.vendor_services.exists():
            sectors = set()
            for vendor_service in vendor.vendor_services.all():
                if vendor_service.subservice and vendor_service.subservice.service:
                    sector = vendor_service.subservice.service.sector
                    if sector:
                        sectors.add(sector)
            vendor.service_sectors = sorted(list(sectors), key=lambda s: s.name)

        # Auto-create trial plan for verified vendors without any plan
        # Check if vendor has ANY existing plans (not just active ones)
        has_any_plan = VendorPlan.objects.filter(vendor=vendor).exists()

        if vendor.verification_status == 'verified' and not vendor.current_plan and not has_any_plan:
            trial_start = date.today()
            trial_end = trial_start + timedelta(days=7)

            # Create trial plan
            trial_plan = VendorPlan.objects.create(
                vendor=vendor,
                plan_type='basic',
                plan_name='Trial Plan (7 Days)',
                price=0,
                start_date=trial_start,
                end_date=trial_end,
                status='active',
                description='Free trial plan for 7 days. Upgrade to continue services.'
            )

            vendor.current_plan = trial_plan
            vendor.days_remaining = 7

            # Log automatic creation (optional)
            print(f'Auto-created trial plan for vendor: {vendor.company_name}')

        elif vendor.current_plan:
            vendor.current_plan.update_status()
            vendor.days_remaining = vendor.current_plan.days_until_expiry()
        else:
            vendor.days_remaining = None

    # Calculate statistics
    total_count = Vendor.objects.count()
    verified_count = Vendor.objects.filter(verification_status='verified').count()
    pending_count = Vendor.objects.filter(verification_status='pending').count()
    suspended_count = Vendor.objects.filter(verification_status='suspended').count()

    # Get cities and states for filters
    cities = City.objects.all()
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').order_by('state')

    context = {
        'vendors': vendors_page,
        'status_filter': status_filter,
        'state_filter': state_filter,
        'city_filter': city_filter,
        'search_query': search_query,
        'total_count': total_count,
        'verified_count': verified_count,
        'pending_count': pending_count,
        'suspended_count': suspended_count,
        'cities': cities,
        'states': states,
    }
    return render(request, 'admin/vendors.html', context)


@login_required
def all_customers(request):
    """View all customers with filtering options"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    city_filter = request.GET.get('city')
    state_filter = request.GET.get('state')
    search_query = request.GET.get('search')
    page = request.GET.get('page', 1)

    # Get all users who are not vendors (exclude superusers)
    customers = UserProfile.objects.exclude(user__is_superuser=True).select_related('user', 'city').prefetch_related('user__bookings', 'user__enquiries').all()
    # Exclude users who have a Vendor profile
    customers = customers.exclude(user__vendor__isnull=False)

    if state_filter:
        customers = customers.filter(state=state_filter)

    if city_filter:
        customers = customers.filter(city_id=city_filter)

    if search_query:
        customers = customers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    customers = customers.order_by('-created_at')

    # Pagination - 10 customers per page
    paginator = Paginator(customers, 10)
    customers_page = paginator.get_page(page)

    # Calculate statistics
    total_count = UserProfile.objects.exclude(user__is_superuser=True).exclude(user__vendor__isnull=False).count()
    active_count = User.objects.exclude(is_superuser=True).filter(userprofile__isnull=False).exclude(vendor__isnull=False).filter(is_active=True).count()
    inactive_count = User.objects.exclude(is_superuser=True).filter(userprofile__isnull=False).exclude(vendor__isnull=False).filter(is_active=False).count()

    # Get cities and states for filters
    cities = City.objects.all()
    states = City.objects.values_list('state', flat=True).distinct().exclude(state='').order_by('state')

    context = {
        'customers': customers_page,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'cities': cities,
        'states': states,
        'state_filter': state_filter,
    }
    return render(request, 'admin/customers.html', context)


@login_required
def admin_customer_edit(request, customer_id):
    """Edit customer profile information"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    customer = get_object_or_404(User, id=customer_id)
    profile = get_object_or_404(UserProfile, user=customer)

    if request.method == 'POST':
        # Update profile information
        profile.phone = request.POST.get('phone')
        profile.city_id = request.POST.get('city')
        profile.address = request.POST.get('address')
        profile.save()

        # Update user information
        customer.email = request.POST.get('email')
        if request.POST.get('password'):
            customer.set_password(request.POST.get('password'))
        customer.save()

        messages.success(request, f'Customer {customer.username} updated successfully.')
        return redirect('admin_all_customers')

    cities = City.objects.all()

    context = {
        'customer': customer,
        'profile': profile,
        'cities': cities,
    }
    return render(request, 'admin/customer_edit.html', context)


@login_required
def admin_customer_activate(request, customer_id):
    """Activate a customer account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    customer = get_object_or_404(User, id=customer_id)
    customer.is_active = True
    customer.save()

    messages.success(request, f'Customer {customer.username} has been activated.')
    return redirect('admin_all_customers')


@login_required
def admin_customer_deactivate(request, customer_id):
    """Deactivate a customer account"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    customer = get_object_or_404(User, id=customer_id)
    customer.is_active = False
    customer.save()

    messages.success(request, f'Customer {customer.username} has been deactivated.')
    return redirect('admin_all_customers')


@login_required
def admin_customer_delete(request, customer_id):
    """Delete a customer account permanently"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    customer = get_object_or_404(User, id=customer_id)

    if request.method == 'POST':
        username = customer.username
        customer.delete()
        messages.success(request, f'Customer {username} has been deleted permanently.')
        return redirect('admin_all_customers')

    context = {
        'customer': customer,
    }
    return render(request, 'admin/customer_delete.html', context)


@login_required
def bulk_vendor_registration(request):
    """Bulk vendor registration via Excel upload"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    if not PANDAS_AVAILABLE:
        messages.error(request, 'pandas library is not installed. Please install it: pip install pandas openpyxl')
        return redirect('admin_dashboard')

    # Check daily limit
    today = timezone.now().date()
    cache_key = f'vendor_reg_count_{today}'
    today_count = cache.get(cache_key, 0)

    if request.method == 'POST':
        form = BulkVendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = request.FILES['excel_file']

                # Read Excel file
                df = pd.read_excel(excel_file, engine='openpyxl' if excel_file.name.endswith('.xlsx') else 'xlrd')

                # Check if required columns exist
                required_columns = ['company_name', 'email', 'phone', 'city', 'address', 'experience', 'license_number']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f'Missing required columns: {", ".join(missing_columns)}')
                    return render(request, 'admin/bulk_registration.html', {'form': form, 'today_count': today_count, 'remaining': 500 - today_count})

                # Check daily limit
                num_vendors = len(df)
                if today_count + num_vendors > 500:
                    messages.error(request, f'Daily limit exceeded. You can register only {500 - today_count} more vendors today.')
                    return render(request, 'admin/bulk_registration.html', {'form': form, 'today_count': today_count, 'remaining': 500 - today_count})

                # Process vendors
                registered_vendors = []
                duplicate_vendors = []
                error_vendors = []
                created_cities = set()

                for index, row in df.iterrows():
                    try:
                        company_name = str(row['company_name']).strip()
                        email = str(row['email']).strip().lower()
                        phone = str(row['phone']).strip()
                        if pd.isna(row['city']) or not str(row['city']).strip():
                            error_vendors.append({'company_name': company_name, 'email': email, 'reason': 'City is required'})
                            continue
                        city_name = str(row['city']).strip()
                        address = str(row['address']).strip()
                        experience = int(row['experience'])
                        license_number = str(row['license_number']).strip()

                        # Check for duplicates (by email)
                        if User.objects.filter(email=email).exists():
                            duplicate_vendors.append({'company_name': company_name, 'email': email, 'reason': 'Email already exists'})
                            continue

                        if Vendor.objects.filter(email=email).exists():
                            duplicate_vendors.append({'company_name': company_name, 'email': email, 'reason': 'Email already registered as vendor'})
                            continue

                        # Reuse existing cities and create new ones from the upload when needed.
                        city = City.objects.filter(name__iexact=city_name).first()
                        if not city:
                            city = City.objects.create(name=city_name)
                            created_cities.add(city.name)

                        # Create user account with email as username and phone as password
                        with transaction.atomic():
                            # Generate unique username from email
                            username = email.split('@')[0]
                            base_username = username
                            counter = 1
                            while User.objects.filter(username=username).exists():
                                username = f"{base_username}{counter}"
                                counter += 1

                            # Create user
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=phone  # Phone number as password
                            )

                            # Create user profile
                            UserProfile.objects.create(
                                user=user,
                                phone=phone,
                                user_type='vendor',
                                city=city
                            )

                            # Create vendor profile
                            vendor = Vendor.objects.create(
                                user=user,
                                company_name=company_name,
                                city=city,
                                experience=experience,
                                phone=phone,
                                email=email,
                                address=address,
                                license_number=license_number,
                                verification_status='pending',
                                is_bulk_registered=True
                            )

                            registered_vendors.append(vendor)

                    except Exception as e:
                        error_vendors.append({
                            'company_name': row.get('company_name', 'Unknown'),
                            'email': row.get('email', 'Unknown'),
                            'reason': str(e)
                        })

                # Update daily count
                cache.set(cache_key, today_count + len(registered_vendors), 86400)  # Cache for 24 hours

                # Show results
                if registered_vendors:
                    messages.success(request, f'Successfully registered {len(registered_vendors)} vendors! (No emails sent - bulk registration)')

                if created_cities:
                    messages.info(request, f'Created new cities: {", ".join(sorted(created_cities))}')

                if duplicate_vendors:
                    messages.warning(request, f'{len(duplicate_vendors)} duplicate vendors skipped (check console for details)')

                if error_vendors:
                    messages.error(request, f'{len(error_vendors)} vendors had errors (check console for details)')

                # Log details for admin
                if duplicate_vendors:
                    print(f"\n=== DUPLICATE VENDORS ===")
                    for dup in duplicate_vendors:
                        print(f"- {dup['company_name']} ({dup['email']}): {dup['reason']}")

                if error_vendors:
                    print(f"\n=== ERROR VENDORS ===")
                    for err in error_vendors:
                        print(f"- {err['company_name']} ({err['email']}): {err['reason']}")

                return redirect('admin_dashboard')

            except Exception as e:
                messages.error(request, f'Error processing Excel file: {str(e)}')
                return render(request, 'admin/bulk_registration.html', {'form': form, 'today_count': today_count, 'remaining': 500 - today_count})
    else:
        form = BulkVendorRegistrationForm()

    context = {
        'form': form,
        'today_count': today_count,
        'remaining': 500 - today_count,
    }
    return render(request, 'admin/bulk_registration.html', context)


# ==================== CUSTOM ADMIN PAGES ====================

@login_required
def admin_cities(request, city_id=None):
    """Custom admin page for cities management"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '').strip()
    state_filter = request.GET.get('state', '').strip()

    # Filter cities based on search query and state
    cities_qs = City.objects.all()

    if search_query:
        from django.db.models import Q
        cities_qs = cities_qs.filter(
            Q(name__icontains=search_query) |
            Q(state__icontains=search_query) |
            Q(description__icontains=search_query)
        ).distinct()

    if state_filter:
        cities_qs = cities_qs.filter(state=state_filter)

    cities_qs = cities_qs.order_by('state', 'name')
    paginator = Paginator(cities_qs, 10)
    cities = paginator.get_page(page)

    # Get unique states for filter dropdown
    states = City.objects.filter(state__isnull=False).exclude(state='').values_list('state', flat=True).distinct().order_by('state')

    total_vendors = Vendor.objects.filter(verification_status='verified').count()
    total_subservices = SubService.objects.count()
    total_cities = City.objects.count()

    if request.method == 'POST':
        action = request.POST.get('action')
        city_id = request.POST.get('city_id')

        if action == 'add':
            name = request.POST.get('name')
            state = request.POST.get('state', '').strip()
            description = request.POST.get('description', '')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            if City.objects.filter(name__iexact=name).exists():
                messages.error(request, 'City with this name already exists.')
            else:
                city = City.objects.create(
                    name=name,
                    state=state,
                    description=description,
                    latitude=latitude if latitude else None,
                    longitude=longitude if longitude else None
                )
                if 'image' in request.FILES:
                    city.image = request.FILES['image']
                    city.save()
                messages.success(request, f'City "{name}" added successfully.')

        elif action == 'edit':
            city = get_object_or_404(City, id=city_id)
            city.name = request.POST.get('name')
            city.state = request.POST.get('state', '').strip()
            city.description = request.POST.get('description', '')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            city.latitude = latitude if latitude else None
            city.longitude = longitude if longitude else None

            if 'image' in request.FILES:
                city.image = request.FILES['image']
            city.save()
            messages.success(request, f'City "{city.name}" updated successfully.')

        elif action == 'delete':
            city = get_object_or_404(City, id=city_id)
            city_name = city.name
            city.delete()
            messages.success(request, f'City "{city_name}" deleted successfully.')

        return redirect('admin_cities')

    return render(request, 'admin/cities.html', {
        'cities': cities,
        'total_cities': total_cities,
        'total_vendors': total_vendors,
        'total_subservices': total_subservices,
        'search_query': search_query,
        'states': states
    })


@login_required
def admin_sectors(request):
    """Custom admin page for sectors management only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    sectors_qs = Sector.objects.prefetch_related('services').all().order_by('-id', 'order', 'name')

    # Pagination - 10 items per page
    paginator = Paginator(sectors_qs, 10)
    sectors = paginator.get_page(page)

    total_services = Service.objects.count()
    total_subservices = SubService.objects.count()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_sector':
            sector_id = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', '')
            order = request.POST.get('order', 0)

            if Sector.objects.filter(id=sector_id).exists():
                messages.error(request, 'Sector ID already exists.')
            elif Sector.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Sector with name "{name}" already exists.')
            else:
                sector = Sector.objects.create(
                    id=sector_id,
                    name=name,
                    description=description,
                    icon=icon,
                    order=order
                )
                if 'image' in request.FILES:
                    sector.image = request.FILES['image']
                    sector.save()
                messages.success(request, f'Sector "{name}" added successfully.')

        elif action == 'edit_sector':
            sector = get_object_or_404(Sector, id=request.POST.get('sector_id'))
            new_id = request.POST.get('id')
            old_id = sector.id
            new_name = request.POST.get('name')

            # Check if name already exists (excluding current sector)
            if Sector.objects.filter(name__iexact=new_name).exclude(id=old_id).exists():
                messages.error(request, f'Sector with name "{new_name}" already exists.')
            else:
                sector.name = new_name
                sector.description = request.POST.get('description', '')
                sector.icon = request.POST.get('icon', '')
                sector.order = request.POST.get('order', 0)

                if 'image' in request.FILES:
                    sector.image = request.FILES['image']
                sector.save()

                if old_id != new_id:
                    # Update the ID field
                    Sector.objects.filter(id=old_id).update(id=new_id)

                messages.success(request, f'Sector "{sector.name}" updated successfully.')

        elif action == 'delete_sector':
            sector = get_object_or_404(Sector, id=request.POST.get('sector_id'))
            sector_name = sector.name
            sector.delete()
            messages.success(request, f'Sector "{sector_name}" deleted successfully.')

        return redirect('admin_sectors')

    # Add total_subservices to each sector
    for sec in sectors:
        sec.total_subservices = SubService.objects.filter(service__sector=sec).count()

    total_sectors = Sector.objects.count()

    return render(request, 'admin/sectors.html', {
        'sectors': sectors,
        'total_sectors': total_sectors,
        'total_services': total_services,
        'total_subservices': total_subservices
    })


@login_required
def admin_services_list(request):
    """Custom admin page for services management only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    services_qs = Service.objects.select_related('sector').all()

    # Apply filters
    sector_filter = request.GET.get('sector')
    search_query = request.GET.get('search')

    if sector_filter:
        services_qs = services_qs.filter(sector__id=sector_filter)

    if search_query:
        services_qs = services_qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    services_qs = services_qs.order_by('-id', 'sector__order', 'sector__name', 'order', 'name')

    # Pagination - 10 items per page
    paginator = Paginator(services_qs, 10)
    services = paginator.get_page(page)

    total_sectors = Sector.objects.count()
    total_subservices = SubService.objects.count()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_service':
            sector_id = request.POST.get('sector')
            service_id_input = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', '')
            order = request.POST.get('order', 0)

            if Service.objects.filter(id=service_id_input).exists():
                messages.error(request, 'Service ID already exists.')
            elif Service.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Service with name "{name}" already exists.')
            else:
                sector = get_object_or_404(Sector, id=sector_id)
                Service.objects.create(
                    sector=sector,
                    id=service_id_input,
                    name=name,
                    description=description,
                    icon=icon,
                    order=order
                )
                messages.success(request, f'Service "{name}" added successfully.')

        elif action == 'edit_service':
            service = get_object_or_404(Service, id=request.POST.get('service_id'))
            new_id = request.POST.get('id')
            old_id = service.id
            new_name = request.POST.get('name')

            # Check if name already exists (excluding current service)
            if Service.objects.filter(name__iexact=new_name).exclude(id=old_id).exists():
                messages.error(request, f'Service with name "{new_name}" already exists.')
            else:
                service.sector = get_object_or_404(Sector, id=request.POST.get('sector'))
                service.name = new_name
                service.description = request.POST.get('description', '')
                service.icon = request.POST.get('icon', '')
                service.order = request.POST.get('order', 0)

                if 'image' in request.FILES:
                    service.image = request.FILES['image']
                service.save()
                messages.success(request, f'Service "{service.name}" updated successfully.')

        elif action == 'delete_service':
            service = get_object_or_404(Service, id=request.POST.get('service_id'))
            service_name = service.name
            service.delete()
            messages.success(request, f'Service "{service_name}" deleted successfully.')

        return redirect('admin_services_list')

    # Get all sectors for modal dropdowns
    all_sectors = Sector.objects.all().order_by('order', 'name')

    return render(request, 'admin/services_list.html', {
        'services': services,
        'all_sectors': all_sectors,
        'total_sectors': total_sectors,
        'total_services': Service.objects.count(),
        'total_subservices': total_subservices,
        'sector_filter': sector_filter or '',
        'search_query': search_query or ''
    })


@login_required
def admin_subservices(request, subservice_id=None):
    """Custom admin page for subservices management only"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    sectors = Sector.objects.prefetch_related('services__subservices').all()
    services = Service.objects.all()
    subservices_qs = SubService.objects.select_related('service__sector').all()

    # Apply filters
    sector_filter = request.GET.get('sector')
    service_filter = request.GET.get('service')
    search_query = request.GET.get('search')

    if sector_filter:
        subservices_qs = subservices_qs.filter(service__sector__id=sector_filter)

    if service_filter:
        subservices_qs = subservices_qs.filter(service__id=service_filter)

    if search_query:
        subservices_qs = subservices_qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    subservices_qs = subservices_qs.order_by('-id', 'service__sector__order', 'service__order', 'order')

    # Pagination - 10 subservices per page
    paginator = Paginator(subservices_qs, 10)
    subservices = paginator.get_page(page)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            service = get_object_or_404(Service, id=request.POST.get('service'))
            subservice_id = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            per_feet_amount = request.POST.get('per_feet_amount')
            order = request.POST.get('order', 0)
            features = request.POST.get('features', '')
            popular = request.POST.get('popular') == 'on'

            if SubService.objects.filter(id=subservice_id).exists():
                messages.error(request, 'SubService ID already exists.')
            elif SubService.objects.filter(service=service, name__iexact=name).exists():
                messages.error(request, f'SubService with name "{name}" already exists in this service.')
            else:
                subservice = SubService.objects.create(
                    service=service,
                    id=subservice_id,
                    name=name,
                    description=description,
                    per_feet_amount=per_feet_amount if per_feet_amount else None,
                    order=order,
                    features=features.split(',') if features else [],
                    popular=popular
                )
                if 'image' in request.FILES:
                    subservice.image = request.FILES['image']
                    subservice.save()
                messages.success(request, f'SubService "{name}" added successfully.')

        elif action == 'edit':
            subservice = get_object_or_404(SubService, id=request.POST.get('subservice_id'))
            service = get_object_or_404(Service, id=request.POST.get('service'))
            new_name = request.POST.get('name')

            # Check if name already exists in the same service (excluding current subservice)
            if SubService.objects.filter(service=service, name__iexact=new_name).exclude(id=subservice.id).exists():
                messages.error(request, f'SubService with name "{new_name}" already exists in this service.')
            else:
                subservice.service = service
                subservice.name = new_name
                subservice.description = request.POST.get('description', '')
                per_feet_amount = request.POST.get('per_feet_amount')
                subservice.per_feet_amount = per_feet_amount if per_feet_amount else None
                subservice.order = request.POST.get('order', 0)
                features = request.POST.get('features', '')
                subservice.features = features.split(',') if features else []
                subservice.popular = request.POST.get('popular') == 'on'

                if 'image' in request.FILES:
                    subservice.image = request.FILES['image']
                subservice.save()
                messages.success(request, f'SubService "{subservice.name}" updated successfully.')

        elif action == 'delete':
            subservice = get_object_or_404(SubService, id=request.POST.get('subservice_id'))
            subservice_name = subservice.name
            subservice.delete()
            messages.success(request, f'SubService "{subservice_name}" deleted successfully.')

        return redirect('admin_subservices')

    total_subservices = SubService.objects.count()

    return render(request, 'admin/subservices.html', {
        'sectors': sectors,
        'services': services,
        'subservices': subservices,
        'total_subservices': total_subservices,
        'sector_filter': sector_filter or '',
        'service_filter': service_filter or '',
        'search_query': search_query or ''
    })


@login_required
def admin_categories(request, sector_id=None, service_id=None):
    """Custom admin page for sectors and services management (legacy - kept for backward compatibility)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)
    subpage = request.GET.get('subpage', 1)

    sectors_qs = Sector.objects.prefetch_related('services').all()
    services_qs = Service.objects.select_related('sector').all()

    # Pagination - 10 items per page for both
    paginator = Paginator(sectors_qs, 10)
    sectors = paginator.get_page(page)

    subpaginator = Paginator(services_qs, 10)
    services = subpaginator.get_page(subpage)

    total_services = Service.objects.count()
    total_subservices = SubService.objects.count()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_sector':
            sector_id = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', '')
            order = request.POST.get('order', 0)

            if Sector.objects.filter(id=sector_id).exists():
                messages.error(request, 'Sector ID already exists.')
            elif Sector.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Sector with name "{name}" already exists.')
            else:
                sector = Sector.objects.create(
                    id=sector_id,
                    name=name,
                    description=description,
                    icon=icon,
                    order=order
                )
                if 'image' in request.FILES:
                    sector.image = request.FILES['image']
                    sector.save()
                messages.success(request, f'Sector "{name}" added successfully.')

        elif action == 'add_service':
            sector_id = request.POST.get('sector')
            service_id_input = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            icon = request.POST.get('icon', '')
            order = request.POST.get('order', 0)

            if Service.objects.filter(id=service_id_input).exists():
                messages.error(request, 'Service ID already exists.')
            elif Service.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Service with name "{name}" already exists.')
            else:
                sector = get_object_or_404(Sector, id=sector_id)
                Service.objects.create(
                    sector=sector,
                    id=service_id_input,
                    name=name,
                    description=description,
                    icon=icon,
                    order=order
                )
                messages.success(request, f'Service "{name}" added successfully.')

        elif action == 'edit_sector':
            sector = get_object_or_404(Sector, id=request.POST.get('sector_id'))
            new_id = request.POST.get('id')
            old_id = sector.id
            new_name = request.POST.get('name')

            if Sector.objects.filter(name__iexact=new_name).exclude(id=old_id).exists():
                messages.error(request, f'Sector with name "{new_name}" already exists.')
            else:
                sector.name = new_name
                sector.description = request.POST.get('description', '')
                sector.icon = request.POST.get('icon', '')
                sector.order = request.POST.get('order', 0)

                if 'image' in request.FILES:
                    sector.image = request.FILES['image']
                sector.save()

                if old_id != new_id:
                    # Update the ID field
                    Sector.objects.filter(id=old_id).update(id=new_id)

                messages.success(request, f'Sector "{sector.name}" updated successfully.')

        elif action == 'edit_service':
            service = get_object_or_404(Service, id=request.POST.get('service_id'))
            new_name = request.POST.get('name')

            if Service.objects.filter(name__iexact=new_name).exclude(id=service.id).exists():
                messages.error(request, f'Service with name "{new_name}" already exists.')
            else:
                service.sector = get_object_or_404(Sector, id=request.POST.get('sector'))
                service.name = new_name
                service.description = request.POST.get('description', '')
                service.icon = request.POST.get('icon', '')
                service.order = request.POST.get('order', 0)

                if 'image' in request.FILES:
                    service.image = request.FILES['image']
                service.save()
                messages.success(request, f'Service "{service.name}" updated successfully.')

        elif action == 'delete_sector':
            sector = get_object_or_404(Sector, id=request.POST.get('sector_id'))
            sector_name = sector.name
            sector.delete()
            messages.success(request, f'Sector "{sector_name}" deleted successfully.')

        elif action == 'delete_service':
            service = get_object_or_404(Service, id=request.POST.get('service_id'))
            service_name = service.name
            service.delete()
            messages.success(request, f'Service "{service_name}" deleted successfully.')

        return redirect('admin_categories')

    # Add total_subservices to each sector
    for sec in sectors:
        sec.total_subservices = SubService.objects.filter(service__sector=sec).count()

    total_sectors = Sector.objects.count()
    # Get all sectors for modal dropdowns
    all_sectors = Sector.objects.all().order_by('order', 'name')

    return render(request, 'admin/categories.html', {
        'sectors': sectors,
        'services': services,
        'all_sectors': all_sectors,
        'total_sectors': total_sectors,
        'total_services': total_services,
        'total_subservices': total_subservices
    })


@login_required
def admin_services(request, subservice_id=None):
    """Custom admin page for subservices management"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    sectors = Sector.objects.prefetch_related('services__subservices').all()
    services = Service.objects.all()
    subservices_qs = SubService.objects.select_related('service__sector').all()

    # Apply filters
    sector_filter = request.GET.get('sector')
    service_filter = request.GET.get('service')
    search_query = request.GET.get('search')

    if sector_filter:
        subservices_qs = subservices_qs.filter(service__sector__id=sector_filter)

    if service_filter:
        subservices_qs = subservices_qs.filter(service__id=service_filter)

    if search_query:
        subservices_qs = subservices_qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    subservices_qs = subservices_qs.order_by('service__sector__order', 'service__order', 'order')

    # Pagination - 10 subservices per page
    paginator = Paginator(subservices_qs, 10)
    subservices = paginator.get_page(page)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            service = get_object_or_404(Service, id=request.POST.get('service'))
            subservice_id = request.POST.get('id')
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            per_feet_amount = request.POST.get('per_feet_amount')
            order = request.POST.get('order', 0)
            features = request.POST.get('features', '')
            popular = request.POST.get('popular') == 'on'

            if SubService.objects.filter(id=subservice_id).exists():
                messages.error(request, 'SubService ID already exists.')
            else:
                subservice = SubService.objects.create(
                    service=service,
                    id=subservice_id,
                    name=name,
                    description=description,
                    per_feet_amount=per_feet_amount if per_feet_amount else None,
                    order=order,
                    features=features.split(',') if features else [],
                    popular=popular
                )
                if 'image' in request.FILES:
                    subservice.image = request.FILES['image']
                    subservice.save()
                messages.success(request, f'SubService "{name}" added successfully.')

        elif action == 'edit':
            subservice = get_object_or_404(SubService, id=request.POST.get('subservice_id'))
            subservice.service = get_object_or_404(Service, id=request.POST.get('service'))
            subservice.name = request.POST.get('name')
            subservice.description = request.POST.get('description', '')
            subservice.per_feet_amount = request.POST.get('per_feet_amount')
            subservice.order = request.POST.get('order', 0)
            features = request.POST.get('features', '')
            subservice.features = features.split(',') if features else []
            subservice.popular = request.POST.get('popular') == 'on'

            if 'image' in request.FILES:
                subservice.image = request.FILES['image']
            subservice.save()
            messages.success(request, f'SubService "{subservice.name}" updated successfully.')

        elif action == 'delete':
            subservice = get_object_or_404(SubService, id=request.POST.get('subservice_id'))
            subservice_name = subservice.name
            subservice.delete()
            messages.success(request, f'SubService "{subservice_name}" deleted successfully.')

        return redirect('admin_services')

    total_subservices = SubService.objects.count()

    return render(request, 'admin/services.html', {
        'sectors': sectors,
        'services': services,
        'subservices': subservices,
        'total_subservices': total_subservices,
        'sector_filter': sector_filter or '',
        'service_filter': service_filter or '',
        'search_query': search_query or ''
    })


@login_required
def admin_blogs(request, blog_id=None):
    """Custom admin page for blogs management"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    blogs_qs = Blog.objects.all().order_by('-created_at')

    # Apply filters
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')

    if category_filter:
        blogs_qs = blogs_qs.filter(category=category_filter)

    if search_query:
        blogs_qs = blogs_qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination - 10 blogs per page
    paginator = Paginator(blogs_qs, 10)
    blogs = paginator.get_page(page)

    categories_count = Blog.objects.values('category').distinct().count()
    authors_count = Blog.objects.values('author').distinct().count()
    total_blogs = Blog.objects.count()

    # Calculate this month's blogs
    from django.utils import timezone
    from datetime import timedelta
    month_ago = timezone.now() - timedelta(days=30)
    this_month = Blog.objects.filter(created_at__gte=month_ago).count()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            title = request.POST.get('title')
            slug = request.POST.get('slug')
            content = request.POST.get('content')
            category = request.POST.get('category')

            if Blog.objects.filter(slug=slug).exists():
                messages.error(request, 'Blog with this slug already exists.')
            else:
                blog = Blog.objects.create(
                    title=title,
                    slug=slug,
                    content=content,
                    category=category,
                    author=request.user
                )
                if 'image' in request.FILES:
                    blog.image = request.FILES['image']
                    blog.save()
                messages.success(request, f'Blog "{title}" published successfully.')

        elif action == 'edit':
            blog = get_object_or_404(Blog, id=request.POST.get('blog_id'))
            blog.title = request.POST.get('title')
            blog.slug = request.POST.get('slug')
            blog.content = request.POST.get('content')
            blog.category = request.POST.get('category')

            if 'image' in request.FILES:
                blog.image = request.FILES['image']
            blog.save()
            messages.success(request, f'Blog "{blog.title}" updated successfully.')

        elif action == 'delete':
            blog = get_object_or_404(Blog, id=request.POST.get('blog_id'))
            blog_title = blog.title
            blog.delete()
            messages.success(request, f'Blog "{blog_title}" deleted successfully.')

        return redirect('admin_blogs')

    return render(request, 'admin/blogs.html', {
        'blogs': blogs,
        'total_blogs': total_blogs,
        'categories_count': categories_count,
        'authors_count': authors_count,
        'this_month': this_month,
        'category_filter': category_filter or '',
        'search_query': search_query or ''
    })


@login_required
def admin_subservice_data(request, subservice_id):
    """Return subservice data as JSON for AJAX calls"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    subservice = get_object_or_404(SubService, id=subservice_id)
    data = {
        'id': subservice.id,
        'name': subservice.name,
        'description': subservice.description,
        'service': subservice.service.id,
        'per_feet_amount': str(subservice.per_feet_amount) if subservice.per_feet_amount else None,
        'order': subservice.order,
        'features': subservice.features,
        'popular': subservice.popular,
    }
    return JsonResponse(data)


@login_required
def admin_blog_data(request, blog_id):
    """Return blog data as JSON for AJAX calls"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    blog = get_object_or_404(Blog, id=blog_id)
    data = {
        'id': blog.id,
        'title': blog.title,
        'slug': blog.slug,
        'content': blog.content,
        'category': blog.category,
        'image': blog.image.url if blog.image else None,
    }
    return JsonResponse(data)


@csrf_exempt
def send_otp(request):
    import random
    import time
    from django.core.mail import send_mail

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('username')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'message': 'Invalid request data'}, status=400)
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Email address is required'}, status=400)
    
    # Check if username already exists
    if username and User.objects.filter(username=username).exists():
        return JsonResponse({
            'success': False,
            'message': 'Username already exists. Please use a different username.'
        }, status=400)
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store in session
    request.session['otp_code'] = otp
    request.session['otp_email'] = email
    request.session['otp_timestamp'] = time.time()
    
    # Send email
    subject = "Verify Your Email - BorewellMart"
    message = f"Your OTP for BorewellMart registration is {otp}.\n\nThis OTP is valid for 5 minutes. Please do not share it with anyone."
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'OTP sent successfully'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }, status=500)


@csrf_exempt
def verify_otp(request):
    import time

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        otp = data.get('otp')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'message': 'Invalid request data'}, status=400)

    if not otp:
        return JsonResponse({'success': False, 'message': 'OTP is required'}, status=400)

    session_otp = request.session.get('otp_code')
    session_email = request.session.get('otp_email')
    session_timestamp = request.session.get('otp_timestamp')

    if not session_otp or not session_email or not session_timestamp:
        return JsonResponse({'success': False, 'message': 'No OTP has been requested/sent yet'}, status=400)

    # Check expiry (5 minutes = 300 seconds)
    if time.time() - session_timestamp > 300:
        request.session.pop('otp_code', None)
        request.session.pop('otp_email', None)
        request.session.pop('otp_timestamp', None)
        return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'}, status=400)

    if otp == session_otp:
        request.session['otp_verified_email'] = session_email
        return JsonResponse({'success': True, 'message': 'OTP verified successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid OTP. Please try again.'}, status=400)


@csrf_exempt
def cities_by_state(request):
    """API endpoint to fetch cities filtered by state"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    state = request.GET.get('state')

    cities = City.objects.all()

    if state:
        cities = cities.filter(state=state)

    # Order cities by name
    cities = cities.order_by('name').values('id', 'name')

    return JsonResponse({
        'success': True,
        'cities': list(cities)
    })


# ===== VENDOR PLAN VIEWS =====

@login_required
def vendor_plans(request):
    """Display all plans for the logged-in vendor"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found')
        return redirect('home')
    
    # Check if vendor is verified
    is_verified, redirect_url = check_vendor_verification(vendor)
    if not is_verified:
        if vendor.verification_status == 'pending':
            messages.warning(request, 'Your account is pending admin verification. Please wait for approval to access plans.')
        elif vendor.verification_status == 'suspended':
            messages.error(request, 'Your account has been suspended. Please contact admin.')
        return redirect('vendor_payment_page')
    
    plans = VendorPlan.objects.filter(vendor=vendor).order_by('-created_at')
    
    # Update plan statuses
    for plan in plans:
        try:
            plan.update_status()
        except Exception as e:
            # Log error but continue to avoid blocking the view
            pass
    
    # Get pagination
    paginator = Paginator(plans, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'vendor': vendor,
        'plans': page_obj,
        'total_plans': plans.count(),
        'active_plans': plans.filter(status='active').count(),
        'expired_plans': plans.filter(status='expired').count(),
    }
    
    return render(request, 'vendor_plans.html', context)


@login_required
def plan_detail(request, plan_id):
    """Display detailed information about a specific plan"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found')
        return redirect('home')
    
    # Check if vendor is verified
    is_verified, redirect_url = check_vendor_verification(vendor)
    if not is_verified:
        if vendor.verification_status == 'pending':
            messages.warning(request, 'Your account is pending admin verification. Please wait for approval to access plans.')
        elif vendor.verification_status == 'suspended':
            messages.error(request, 'Your account has been suspended. Please contact admin.')
        return redirect('vendor_payment_page')
    
    plan = get_object_or_404(VendorPlan, id=plan_id, vendor=vendor)
    plan.update_status()
    
    # Get all notifications for this plan
    notifications = PlanNotification.objects.filter(plan=plan).order_by('-sent_at')
    
    context = {
        'plan': plan,
        'notifications': notifications,
        'vendor': vendor,
    }
    
    return render(request, 'plan_detail.html', context)


@login_required
def create_plan(request):
    """Create a new vendor plan"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found')
        return redirect('home')
    
    # Check if vendor is verified
    is_verified, redirect_url = check_vendor_verification(vendor)
    if not is_verified:
        if vendor.verification_status == 'pending':
            messages.warning(request, 'Your account is pending admin verification. Please wait for approval to create plans.')
        elif vendor.verification_status == 'suspended':
            messages.error(request, 'Your account has been suspended. Please contact admin.')
        return redirect('vendor_payment_page')
    
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        plan_name = request.POST.get('plan_name')
        price = request.POST.get('price')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        description = request.POST.get('description')
        
        # Validate data
        if not all([plan_type, plan_name, price, start_date, end_date]):
            messages.error(request, 'All fields are required')
            return redirect('create_plan')
        
        try:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end_date_obj <= start_date_obj:
                messages.error(request, 'End date must be after start date')
                return redirect('create_plan')
            
            plan = VendorPlan.objects.create(
                vendor=vendor,
                plan_type=plan_type,
                plan_name=plan_name,
                price=float(price),
                start_date=start_date_obj,
                end_date=end_date_obj,
                description=description
            )
            
            messages.success(request, f'Plan "{plan_name}" created successfully!')
            return redirect('plan_detail', plan_id=plan.id)
        
        except ValueError:
            messages.error(request, 'Invalid date format. Use YYYY-MM-DD')
            return redirect('create_plan')
    
    context = {
        'plan_types': VendorPlan.PLAN_TYPE_CHOICES,
    }
    
    return render(request, 'create_plan.html', context)


@login_required
def edit_plan(request, plan_id):
    """Edit an existing vendor plan"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found')
        return redirect('home')
    
    # Check if vendor is verified
    is_verified, redirect_url = check_vendor_verification(vendor)
    if not is_verified:
        if vendor.verification_status == 'pending':
            messages.warning(request, 'Your account is pending admin verification. Please wait for approval to edit plans.')
        elif vendor.verification_status == 'suspended':
            messages.error(request, 'Your account has been suspended. Please contact admin.')
        return redirect('vendor_payment_page')
    
    plan = get_object_or_404(VendorPlan, id=plan_id, vendor=vendor)
    
    if request.method == 'POST':
        plan_name = request.POST.get('plan_name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        
        plan.plan_name = plan_name
        plan.price = float(price)
        plan.description = description
        plan.save()
        
        messages.success(request, 'Plan updated successfully!')
        return redirect('plan_detail', plan_id=plan.id)
    
    context = {
        'plan': plan,
        'plan_types': VendorPlan.PLAN_TYPE_CHOICES,
    }
    
    return render(request, 'edit_plan.html', context)


@login_required
def renew_plan(request, plan_id):
    """Renew an expired or expiring plan"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found')
        return redirect('home')
    
    # Check if vendor is verified
    is_verified, redirect_url = check_vendor_verification(vendor)
    if not is_verified:
        if vendor.verification_status == 'pending':
            messages.warning(request, 'Your account is pending admin verification. Please wait for approval to renew plans.')
        elif vendor.verification_status == 'suspended':
            messages.error(request, 'Your account has been suspended. Please contact admin.')
        return redirect('vendor_payment_page')
    
    old_plan = get_object_or_404(VendorPlan, id=plan_id, vendor=vendor)
    
    if request.method == 'POST':
        new_start_date = request.POST.get('start_date')
        new_end_date = request.POST.get('end_date')
        
        if not all([new_start_date, new_end_date]):
            messages.error(request, 'All fields are required')
            return redirect('renew_plan', plan_id=plan_id)
        
        try:
            from datetime import datetime
            start_date_obj = datetime.strptime(new_start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(new_end_date, '%Y-%m-%d').date()
            
            if end_date_obj <= start_date_obj:
                messages.error(request, 'End date must be after start date')
                return redirect('renew_plan', plan_id=plan_id)
            
            # Create new plan based on old one
            new_plan = VendorPlan.objects.create(
                vendor=vendor,
                plan_type=old_plan.plan_type,
                plan_name=old_plan.plan_name,
                price=old_plan.price,
                start_date=start_date_obj,
                end_date=end_date_obj,
                description=old_plan.description
            )

            # Mark old plan as cancelled if it's expired
            if old_plan.is_expired():
                old_plan.status = 'cancelled'
                old_plan.save()

            # Send WhatsApp notification for plan renewal/upgrade
            try:
                send_whatsapp_plan_renewal_notification(
                    vendor=vendor,
                    plan_name=new_plan.plan_name,
                    amount=new_plan.price,
                    start_date=start_date_obj,
                    end_date=end_date_obj
                )
            except Exception as e:
                print(f"Failed to send WhatsApp plan renewal notification: {e}")

            messages.success(request, f'Plan renewed successfully! New validity: {new_start_date} to {new_end_date}')
            return redirect('plan_detail', plan_id=new_plan.id)
        
        except ValueError:
            messages.error(request, 'Invalid date format. Use YYYY-MM-DD')
            return redirect('renew_plan', plan_id=plan_id)
    
    context = {
        'plan': old_plan,
    }
    
    return render(request, 'renew_plan.html', context)


@login_required
def plan_notifications(request, plan_id):
    """Display all notifications for a specific plan"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor profile not found')
        return redirect('home')
    
    # Check if vendor is verified
    is_verified, redirect_url = check_vendor_verification(vendor)
    if not is_verified:
        if vendor.verification_status == 'pending':
            messages.warning(request, 'Your account is pending admin verification. Please wait for approval to view notifications.')
        elif vendor.verification_status == 'suspended':
            messages.error(request, 'Your account has been suspended. Please contact admin.')
        return redirect('vendor_payment_page')
    
    plan = get_object_or_404(VendorPlan, id=plan_id, vendor=vendor)
    notifications = PlanNotification.objects.filter(plan=plan).order_by('-sent_at')
    
    # Get pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'plan': plan,
        'notifications': page_obj,
        'total_notifications': notifications.count(),
    }
    
    return render(request, 'plan_notifications.html', context)


# ==================== FORUM VIEWS ====================

def forum_home(request):
    """Forum home page with categories and recent threads"""
    # Block admin access
    if request.user.is_authenticated and request.user.is_superuser:
        messages.error(request, 'Admins cannot access the forum page.')
        return redirect('admin_dashboard')

    from django.db.models import Count, Q

    # Annotate categories with calculated thread and post counts
    # Use different names to avoid conflicts with model fields
    categories = ForumCategory.objects.annotate(
        calc_thread_count=Count('threads', distinct=True),
        calc_post_count=Count('threads__posts', distinct=True)
    ).prefetch_related('threads__author').all().order_by('order')

    # Update the category objects with the calculated counts
    for category in categories:
        category.thread_count = category.calc_thread_count
        category.post_count = category.calc_post_count

    recent_threads = ForumThread.objects.select_related('author', 'category').prefetch_related('posts').order_by('-updated_at')[:10]

    # Get communities
    communities = Community.objects.filter(is_active=True).prefetch_related('members').order_by('-created_at')

    # Check if user is member of each community
    user_memberships = {}
    if request.user.is_authenticated:
        user_memberships = set(
            CommunityMember.objects.filter(
                user=request.user
            ).values_list('community_id', flat=True)
        )

    for community in communities:
        community.is_member = community.id in user_memberships

    # Get statistics
    total_threads = ForumThread.objects.count()
    total_posts = ForumPost.objects.count()
    total_members = User.objects.count()

    # Get top contributors
    from django.db.models import Count
    top_contributors = User.objects.annotate(
        thread_count=Count('forum_threads'),
        post_count=Count('forum_posts')
    ).order_by('-thread_count')[:10]

    context = {
        'categories': categories,
        'recent_threads': recent_threads,
        'communities': communities,
        'total_threads': total_threads,
        'total_posts': total_posts,
        'total_members': total_members,
        'top_contributors': top_contributors,
    }
    return render(request, 'forum/home.html', context)


def forum_category(request, category_slug):
    """View threads in a specific category"""
    from django.db.models import Count, Q
    from django.core.paginator import Paginator

    # Handle 'all' slug for showing all threads
    if category_slug == 'all':
        category = None
        threads_qs = ForumThread.objects.select_related('author', 'category').prefetch_related('posts').all()
        # Annotate other categories with counts (use different names to avoid conflicts)
        other_categories = ForumCategory.objects.annotate(
            calc_thread_count=Count('threads', distinct=True),
            calc_post_count=Count('threads__posts', distinct=True)
        ).all().order_by('order')
        # Update the category objects with the calculated counts
        for cat in other_categories:
            cat.thread_count = cat.calc_thread_count
            cat.post_count = cat.calc_post_count
    else:
        category = get_object_or_404(ForumCategory, slug=category_slug)
        threads_qs = category.threads.select_related('author').prefetch_related('posts').all()
        # Annotate other categories with counts (use different names to avoid conflicts)
        other_categories = ForumCategory.objects.annotate(
            calc_thread_count=Count('threads', distinct=True),
            calc_post_count=Count('threads__posts', distinct=True)
        ).all().order_by('order')
        # Update the category objects with the calculated counts
        for cat in other_categories:
            cat.thread_count = cat.calc_thread_count
            cat.post_count = cat.calc_post_count

    # Get filter parameter
    filter = request.GET.get('filter', 'newest')

    # Apply filters
    if filter == 'solved':
        threads_qs = threads_qs.filter(status='solved')
    elif filter == 'unsolved':
        threads_qs = threads_qs.filter(status='open')
    elif filter == 'popular':
        threads_qs = threads_qs.order_by('-like_count', '-updated_at')
    elif filter == 'nearby':
        # Filter by user's city if logged in
        if request.user.is_authenticated:
            try:
                user_city = request.user.userprofile.city
                threads_qs = threads_qs.filter(author__userprofile__city=user_city)
            except UserProfile.DoesNotExist:
                threads_qs = threads_qs.none()
        else:
            threads_qs = threads_qs.none()
    else:  # newest
        threads_qs = threads_qs.order_by('-updated_at')

    # Search
    search_query = request.GET.get('q')
    if search_query:
        threads_qs = threads_qs.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Get counts for sidebar
    solved_count = threads_qs.filter(status='solved').count()
    unanswered_count = threads_qs.filter(reply_count=0).count()

    # Pagination
    paginator = Paginator(threads_qs, 20)
    page = request.GET.get('page', 1)
    threads_page = paginator.get_page(page)

    context = {
        'category': category,
        'threads': threads_page,
        'filter': filter,
        'solved_count': solved_count,
        'unanswered_count': unanswered_count,
        'other_categories': other_categories,
    }
    return render(request, 'forum/category.html', context)


def forum_thread(request, thread_slug):
    """View a single thread and its posts"""
    thread = get_object_or_404(ForumThread, slug=thread_slug)
    # Exclude the first post (it's the question content, shown at top)
    posts = thread.posts.select_related('author').all().order_by('created_at')[1:]

    # Increment view count
    thread.views += 1
    thread.save()

    # Check if user has voted
    user_has_voted = False
    if request.user.is_authenticated:
        user_has_voted = ForumVote.objects.filter(
            user=request.user,
            thread=thread
        ).exists()

    # Get related threads (same category, excluding current)
    related_threads = ForumThread.objects.filter(
        category=thread.category
    ).exclude(id=thread.id).order_by('-updated_at')[:5]

    context = {
        'thread': thread,
        'posts': posts,
        'user_has_voted': user_has_voted,
        'related_threads': related_threads,
    }
    return render(request, 'forum/thread.html', context)


@login_required
def forum_create_thread(request):
    """Create a new forum thread - vendors require active plan"""
    # Note: For vendors, plan verification is handled by middleware
    # Vendors without an active plan will be redirected before reaching this view
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()

            # Handle tags
            tags = form.cleaned_data.get('tags')
            if tags:
                from .models import ForumThreadTag
                for tag in tags:
                    ForumThreadTag.objects.create(thread=thread, tag=tag)
                    # Increment tag thread count
                    tag.thread_count += 1
                    tag.save()

            # Handle services
            services = form.cleaned_data.get('services')
            if services:
                from .models import ForumThreadService
                for service in services:
                    ForumThreadService.objects.create(thread=thread, service=service)

            # Create initial post (the thread content)
            ForumPost.objects.create(
                thread=thread,
                author=request.user,
                content=thread.content
            )

            # Update category counts
            thread.category.thread_count += 1
            thread.category.save()

            messages.success(request, 'Your question has been posted successfully!')
            return redirect('forum_thread', thread_slug=thread.slug)
    else:
        form = ForumThreadForm()

    categories = ForumCategory.objects.all().order_by('order')
    all_tags = ForumTag.objects.all().order_by('name')
    subservices = SubService.objects.select_related('service__sector').all()
    selected_tags = []

    context = {
        'form': form,
        'categories': categories,
        'all_tags': all_tags,
        'subservices': subservices,
        'selected_tags': selected_tags,
    }
    return render(request, 'forum/create_thread.html', context)


@login_required
def forum_reply(request, thread_slug):
    """Reply to a thread - vendors require active plan"""
    # Note: For vendors, plan verification is handled by middleware
    thread = get_object_or_404(ForumThread, slug=thread_slug)

    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()

            # Update thread reply count
            thread.reply_count += 1
            thread.updated_at = timezone.now()
            thread.save()

            # Update category post count
            thread.category.post_count += 1
            thread.category.save()

            messages.success(request, 'Your reply has been posted!')
            return redirect('forum_thread', thread_slug=thread.slug)

    return redirect('forum_thread', thread_slug=thread_slug)


@login_required
def forum_vote(request):
    """Vote on a thread or post"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

    vote_type = request.POST.get('vote_type', 'up')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'success': False, 'message': 'Invalid vote type'}, status=400)

    thread_id = request.POST.get('thread_id')
    post_id = request.POST.get('post_id')

    # Get the target object
    if thread_id:
        target = get_object_or_404(ForumThread, id=thread_id)
        target_type = 'thread'
    elif post_id:
        target = get_object_or_404(ForumPost, id=post_id)
        target_type = 'post'
    else:
        return JsonResponse({'success': False, 'message': 'No target specified'}, status=400)

    # Check if user already voted
    existing_vote = ForumVote.objects.filter(
        user=request.user,
        **{f'{target_type}_id': target.id}
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote (toggle)
            existing_vote.delete()
            return JsonResponse({'success': True, 'action': 'removed', 'count': target.like_count})
        else:
            # Change vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
            return JsonResponse({'success': True, 'action': 'changed', 'count': target.like_count})
    else:
        # Create new vote
        ForumVote.objects.create(
            user=request.user,
            vote_type=vote_type,
            **{f'{target_type}': target}
        )
        return JsonResponse({'success': True, 'action': 'added', 'count': target.like_count})


@login_required
def forum_mark_best_answer(request, thread_slug, post_id):
    """Mark a post as the best answer"""
    thread = get_object_or_404(ForumThread, slug=thread_slug)

    # Only thread author can mark best answer
    if thread.author != request.user:
        messages.error(request, 'Only the question author can mark the best answer.')
        return redirect('forum_thread', thread_slug=thread.slug)

    post = get_object_or_404(ForumPost, id=post_id, thread=thread)

    # Remove existing best answer
    thread.posts.filter(is_best_answer=True).update(is_best_answer=False)

    # Mark new best answer
    post.is_best_answer = True
    post.save()

    # Mark thread as solved
    thread.status = 'solved'
    thread.save()

    messages.success(request, 'Best answer marked successfully!')
    return redirect('forum_thread', thread_slug=thread.slug)


@login_required
def forum_mark_solved(request, thread_slug):
    """Mark a thread as solved without selecting best answer"""
    thread = get_object_or_404(ForumThread, slug=thread_slug)

    # Only thread author can mark as solved
    if thread.author != request.user:
        messages.error(request, 'Only the question author can mark the question as solved.')
        return redirect('forum_thread', thread_slug=thread.slug)

    thread.status = 'solved'
    thread.save()

    messages.success(request, 'Question marked as solved!')
    return redirect('forum_thread', thread_slug=thread.slug)


@login_required
def forum_edit_post(request, post_id):
    """Edit a forum post"""
    post = get_object_or_404(ForumPost, id=post_id)

    # Only post author or admin can edit
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('forum_thread', thread_slug=post.thread.slug)

    if request.method == 'POST':
        form = ForumPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('forum_thread', thread_slug=post.thread.slug)
    else:
        form = ForumPostForm(instance=post)

    return render(request, 'forum/edit_post.html', {'form': form, 'post': post})


@login_required
def forum_edit_thread(request, thread_slug):
    """Edit a forum thread title and content"""
    thread = get_object_or_404(ForumThread, slug=thread_slug)

    # Only thread author or admin can edit
    if thread.author != request.user and not request.user.is_staff:
        messages.error(request, 'You can only edit your own threads.')
        return redirect('forum_thread', thread_slug=thread.slug)

    if request.method == 'POST':
        form = ForumThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            # Also update the first post content
            first_post = thread.posts.first()
            if first_post:
                first_post.content = thread.content
                first_post.save()

            messages.success(request, 'Thread updated successfully!')
            return redirect('forum_thread', thread_slug=thread.slug)
        else:
            # Form is not valid, show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForumThreadForm(instance=thread)

    context = {
        'form': form,
        'thread': thread,
        'categories': ForumCategory.objects.all().order_by('order'),
        'all_tags': ForumTag.objects.all().order_by('name'),
        'subservices': SubService.objects.select_related('service__sector').all(),
        'selected_tags': list(thread.thread_tags.all().values_list('tag_id', flat=True)),
    }
    return render(request, 'forum/edit_thread.html', context)


@login_required
def forum_close_thread(request, thread_slug):
    """Close a thread (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Only admins can close threads.')
        return redirect('forum_thread', thread_slug=thread_slug)

    thread = get_object_or_404(ForumThread, slug=thread_slug)
    thread.status = 'closed'
    thread.save()

    messages.success(request, 'Thread has been closed.')
    return redirect('forum_thread', thread_slug=thread.slug)


@login_required
def forum_reopen_thread(request, thread_slug):
    """Reopen a closed thread (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Only admins can reopen threads.')
        return redirect('forum_thread', thread_slug=thread_slug)

    thread = get_object_or_404(ForumThread, slug=thread_slug)
    thread.status = 'open'
    thread.save()

    messages.success(request, 'Thread has been reopened.')
    return redirect('forum_thread', thread_slug=thread.slug)


@login_required
def forum_delete_thread(request, thread_slug):
    """Delete a forum thread (author or admin only)"""
    thread = get_object_or_404(ForumThread, slug=thread_slug)

    # Only thread author or admin can delete
    if thread.author != request.user and not request.user.is_staff:
        messages.error(request, 'You can only delete your own threads.')
        return redirect('forum_thread', thread_slug=thread.slug)

    category_slug = thread.category.slug

    if request.method == 'POST':
        thread.delete()
        messages.success(request, 'Thread has been deleted.')
        return redirect('forum_category', category_slug=category_slug)

    # For GET requests, show confirmation page
    return render(request, 'forum/delete_thread.html', {'thread': thread})


@login_required
def forum_delete_post(request, post_id):
    """Delete a forum post/reply (author or admin only)"""
    post = get_object_or_404(ForumPost, id=post_id)

    # Only post author or admin can delete
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('forum_thread', thread_slug=post.thread.slug)

    thread_slug = post.thread.slug

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Reply has been deleted.')
        return redirect('forum_thread', thread_slug=thread_slug)

    # For GET requests, show confirmation page
    return render(request, 'forum/delete_post.html', {'post': post})


# ==================== COMMUNITY VIEWS ====================

def community_list(request):
    """List all communities"""
    communities = Community.objects.filter(is_active=True).annotate(
        total_posts=Count('posts')
    ).order_by('-created_at')

    # Check if user is member of each community
    user_memberships = {}
    if request.user.is_authenticated:
        user_memberships = set(
            CommunityMember.objects.filter(
                user=request.user
            ).values_list('community_id', flat=True)
        )

    for community in communities:
        community.is_member = community.id in user_memberships

    context = {
        'communities': communities,
    }
    return render(request, 'communities/community_list.html', context)


def community_detail(request, community_slug):
    """View community and its posts"""
    community = get_object_or_404(Community, slug=community_slug, is_active=True)
    posts = community.posts.select_related('author').prefetch_related('likes', 'comments__author').order_by('-created_at')

    # Check if user is member
    is_member = False
    if request.user.is_authenticated:
        is_member = CommunityMember.objects.filter(
            user=request.user,
            community=community
        ).exists()

    # Add like status for each post
    for post in posts:
        post.is_liked = post.is_liked_by_user(request.user) if request.user.is_authenticated else False

    context = {
        'community': community,
        'posts': posts,
        'is_member': is_member,
    }
    return render(request, 'communities/community_detail.html', context)


@login_required
def join_community(request, community_slug):
    """Join a community"""
    community = get_object_or_404(Community, slug=community_slug, is_active=True)

    # Check if already a member
    if CommunityMember.objects.filter(user=request.user, community=community).exists():
        messages.warning(request, 'You are already a member of this community.')
        return redirect('community_detail', community_slug=community.slug)

    # Add as member
    CommunityMember.objects.create(
        user=request.user,
        community=community,
        role='member'
    )

    messages.success(request, f'You have joined {community.name}!')
    return redirect('community_detail', community_slug=community.slug)


@login_required
def leave_community(request, community_slug):
    """Leave a community"""
    community = get_object_or_404(Community, slug=community_slug, is_active=True)

    try:
        membership = CommunityMember.objects.get(user=request.user, community=community)
        membership.delete()
        messages.success(request, f'You have left {community.name}.')
    except CommunityMember.DoesNotExist:
        messages.error(request, 'You are not a member of this community.')

    return redirect('community_detail', community_slug=community.slug)


@login_required
def create_community_post(request, community_slug):
    """Create a post in a community"""
    community = get_object_or_404(Community, slug=community_slug, is_active=True)

    # Check if user is a member
    if not CommunityMember.objects.filter(user=request.user, community=community).exists():
        messages.error(request, 'You must be a member to post in this community.')
        return redirect('community_detail', community_slug=community.slug)

    if request.method == 'POST':
        form = CommunityPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.community = community
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been published!')
            return redirect('community_detail', community_slug=community.slug)
    else:
        form = CommunityPostForm()

    context = {
        'form': form,
        'community': community,
    }
    return render(request, 'communities/create_post.html', context)


@login_required
def like_community_post(request, post_id):
    """Like/unlike a community post"""
    post = get_object_or_404(CommunityPost, id=post_id)
    community = post.community

    # Check if user is a member
    if not CommunityMember.objects.filter(user=request.user, community=community).exists():
        messages.error(request, 'You must be a member to interact with posts.')
        return redirect('community_detail', community_slug=community.slug)

    like, created = CommunityLike.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        # Unlike if already liked
        like.delete()

    return redirect('community_detail', community_slug=community.slug)


@login_required
def comment_on_post(request, post_id):
    """Add a comment to a community post"""
    post = get_object_or_404(CommunityPost, id=post_id)
    community = post.community

    # Check if user is a member
    if not CommunityMember.objects.filter(user=request.user, community=community).exists():
        messages.error(request, 'You must be a member to comment on posts.')
        return redirect('community_detail', community_slug=community.slug)

    if request.method == 'POST':
        form = CommunityCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('community_detail', community_slug=community.slug)

    return redirect('community_detail', community_slug=community.slug)


@login_required
def admin_create_community(request):
    """Admin create a new community"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('community_list')

    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.created_by = request.user
            community.save()
            # Add creator as admin member
            CommunityMember.objects.create(
                user=request.user,
                community=community,
                role='admin'
            )
            messages.success(request, f'Community "{community.name}" has been created!')
            return redirect('community_list')
    else:
        form = CommunityForm()

    context = {
        'form': form,
    }
    return render(request, 'communities/admin_create_community.html', context)


@login_required
def admin_edit_community(request, community_slug):
    """Admin edit a community"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('community_list')

    community = get_object_or_404(Community, slug=community_slug)

    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES, instance=community)
        if form.is_valid():
            form.save()
            messages.success(request, f'Community "{community.name}" has been updated!')
            return redirect('community_list')
    else:
        form = CommunityForm(instance=community)

    context = {
        'form': form,
        'community': community,
    }
    return render(request, 'communities/admin_edit_community.html', context)


@login_required
def admin_delete_community(request, community_slug):
    """Admin delete a community"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('community_list')

    community = get_object_or_404(Community, slug=community_slug)

    if request.method == 'POST':
        community_name = community.name
        community.delete()
        messages.success(request, f'Community "{community_name}" has been deleted.')
        return redirect('community_list')

    context = {
        'community': community,
    }
    return render(request, 'communities/admin_delete_community.html', context)


@login_required
def admin_communities(request):
    """Admin manage all communities"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('community_list')

    communities = Community.objects.all().order_by('-created_at')

    context = {
        'communities': communities,
    }
    return render(request, 'communities/admin_communities.html', context)


@login_required
def delete_post(request, post_id):
    """Delete own post (author only) or admin can delete any"""
    post = get_object_or_404(CommunityPost, id=post_id)

    # Check if user is author or admin
    if post.author != request.user and not request.user.is_superuser:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('community_detail', community_slug=post.community.slug)

    community_slug = post.community.slug
    post.delete()
    messages.success(request, 'Your post has been deleted.')
    return redirect('community_detail', community_slug=community_slug)


def custom_404_view(request, exception=None):
    """Custom 404 Page Not Found view"""
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """Custom 500 Server Error view"""
    return render(request, '500.html', status=500)


def terms_and_conditions(request):
    """Terms and Conditions page"""
    return render(request, 'terms_and_conditions.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'privacy_policy.html')


def cancellation_refund_policy(request):
    """Cancellation and Refund Policy page"""
    return render(request, 'cancellation_refund_policy.html')


@login_required
def admin_equipment(request):
    """Admin page for managing all equipment listings"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    equipment_qs = VendorEquipment.objects.select_related('vendor').all().order_by('-created_at')

    # Apply filters
    category_filter = request.GET.get('category')
    vendor_filter = request.GET.get('vendor')
    availability_filter = request.GET.get('availability')
    search_query = request.GET.get('search')

    if category_filter:
        equipment_qs = equipment_qs.filter(category=category_filter)

    if vendor_filter:
        equipment_qs = equipment_qs.filter(vendor_id=vendor_filter)

    if availability_filter:
        if availability_filter == 'available':
            equipment_qs = equipment_qs.filter(is_available=True)
        elif availability_filter == 'sold':
            equipment_qs = equipment_qs.filter(is_available=False)

    if search_query:
        equipment_qs = equipment_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Pagination - 12 equipment per page
    paginator = Paginator(equipment_qs, 12)
    equipment_list = paginator.get_page(page)

    # Get filter options
    categories = VendorEquipment.CATEGORY_CHOICES
    vendors = Vendor.objects.filter(verification_status='verified')

    total_equipment = VendorEquipment.objects.count()
    available_count = VendorEquipment.objects.filter(is_available=True).count()
    sold_count = VendorEquipment.objects.filter(is_available=False).count()

    return render(request, 'admin/admin_equipment.html', {
        'equipment_list': equipment_list,
        'categories': categories,
        'vendors': vendors,
        'total_equipment': total_equipment,
        'available_count': available_count,
        'sold_count': sold_count,
        'category_filter': category_filter or '',
        'vendor_filter': vendor_filter or '',
        'availability_filter': availability_filter or '',
        'search_query': search_query or ''
    })


@login_required
def admin_equipment_add(request):
    """Admin view to add new equipment"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, id=request.POST.get('vendor'))
        title = request.POST.get('title')
        category = request.POST.get('category')
        condition = request.POST.get('condition')
        description = request.POST.get('description')
        price = request.POST.get('price')
        brand = request.POST.get('brand', '')
        year_manufactured = request.POST.get('year_manufactured')
        location = request.POST.get('location')
        is_negotiable = request.POST.get('is_negotiable') == 'on'
        is_available = request.POST.get('is_available') == 'on'

        equipment = VendorEquipment.objects.create(
            vendor=vendor,
            title=title,
            category=category,
            condition=condition,
            description=description,
            price=price,
            brand=brand,
            year_manufactured=year_manufactured,
            location=location,
            is_negotiable=is_negotiable,
            is_available=is_available
        )

        if 'image' in request.FILES:
            equipment.image = request.FILES['image']
            equipment.save()

        messages.success(request, f'Equipment "{title}" added successfully.')
        return redirect('admin_equipment')

    from django.utils import timezone
    vendors = Vendor.objects.filter(verification_status='verified')
    return render(request, 'admin/admin_equipment_form.html', {
        'vendors': vendors,
        'action': 'add',
        'current_year': timezone.now().year
    })


@login_required
def admin_equipment_edit(request, equipment_id):
    """Admin view to edit equipment"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    equipment = get_object_or_404(VendorEquipment, id=equipment_id)

    if request.method == 'POST':
        equipment.vendor = get_object_or_404(Vendor, id=request.POST.get('vendor'))
        equipment.title = request.POST.get('title')
        equipment.category = request.POST.get('category')
        equipment.condition = request.POST.get('condition')
        equipment.description = request.POST.get('description')
        equipment.price = request.POST.get('price')
        equipment.brand = request.POST.get('brand', '')
        equipment.year_manufactured = request.POST.get('year_manufactured')
        equipment.location = request.POST.get('location')
        equipment.is_negotiable = request.POST.get('is_negotiable') == 'on'
        equipment.is_available = request.POST.get('is_available') == 'on'

        if 'image' in request.FILES:
            equipment.image = request.FILES['image']

        equipment.save()
        messages.success(request, f'Equipment "{equipment.title}" updated successfully.')
        return redirect('admin_equipment')

    from django.utils import timezone
    vendors = Vendor.objects.filter(verification_status='verified')
    return render(request, 'admin/admin_equipment_form.html', {
        'equipment': equipment,
        'vendors': vendors,
        'action': 'edit',
        'current_year': timezone.now().year
    })


@login_required
def admin_equipment_delete(request, equipment_id):
    """Admin view to delete equipment"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    equipment = get_object_or_404(VendorEquipment, id=equipment_id)

    if request.method == 'POST':
        title = equipment.title
        equipment.delete()
        messages.success(request, f'Equipment "{title}" deleted successfully.')
        return redirect('admin_equipment')

    return render(request, 'admin/admin_equipment_delete.html', {
        'equipment': equipment
    })


@login_required
def admin_equipment_data(request, equipment_id):
    """AJAX endpoint to get equipment data for editing"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Access denied'}, status=403)

    equipment = get_object_or_404(VendorEquipment, id=equipment_id)
    data = {
        'id': equipment.id,
        'title': equipment.title,
        'category': equipment.category,
        'condition': equipment.condition,
        'description': equipment.description,
        'price': str(equipment.price),
        'brand': equipment.brand or '',
        'year_manufactured': equipment.year_manufactured or '',
        'location': equipment.location,
        'is_negotiable': equipment.is_negotiable,
        'is_available': equipment.is_available,
        'vendor_id': equipment.vendor.id,
        'vendor_name': equipment.vendor.company_name,
        'image_url': equipment.image.url if equipment.image else ''
    }
    return JsonResponse(data)


def cities_by_state(request):
    """API endpoint to get cities filtered by state"""
    state = request.GET.get('state', '')
    
    if state:
        cities = City.objects.filter(state=state).order_by('name')
    else:
        cities = City.objects.all().order_by('name')
    
    cities_data = [{'id': city.id, 'name': city.name} for city in cities]
    return JsonResponse({'success': True, 'cities': cities_data})


@login_required
def admin_visitors(request):
    """Custom admin page for visitor tracking"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')

    page = request.GET.get('page', 1)

    visitors_qs = VisitorTracking.objects.all().order_by('-first_visit')

    # Apply filters
    search_query = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if search_query:
        visitors_qs = visitors_qs.filter(
            Q(ip_address__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(session_key__icontains=search_query)
        )

    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            visitors_qs = visitors_qs.filter(first_visit__date__gte=date_from_obj)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            from datetime import datetime, timedelta
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            # Include the entire end date by adding one day
            end_date = date_to_obj + timedelta(days=1)
            visitors_qs = visitors_qs.filter(first_visit__date__lt=end_date)
        except (ValueError, TypeError):
            pass

    # Pagination - 20 visitors per page
    paginator = Paginator(visitors_qs, 20)
    visitors = paginator.get_page(page)

    # Statistics
    total_visitors = VisitorTracking.objects.count()
    today_visitors = VisitorTracking.objects.filter(
        first_visit__date=date.today()
    ).count()
    unique_visitors = total_visitors
    repeat_visitors = VisitorTracking.objects.filter(visit_count__gt=1).count()

    # Calculate this week's visitors
    from django.utils import timezone
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    this_week = VisitorTracking.objects.filter(first_visit__gte=week_ago).count()

    return render(request, 'admin/visitors.html', {
        'visitors': visitors,
        'total_visitors': total_visitors,
        'today_visitors': today_visitors,
        'this_week': this_week,
        'repeat_visitors': repeat_visitors,
        'search_query': search_query or '',
        'date_from': date_from or '',
        'date_to': date_to or ''
    })


