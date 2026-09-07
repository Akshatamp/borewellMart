import re
import requests
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from PIL import Image
import io
import os


def format_whatsapp_number(phone):
    """Normalize phone numbers for WhatsApp Cloud API."""
    if not phone:
        return None

    digits = re.sub(r'\D', '', str(phone))
    if not digits:
        return None

    if digits.startswith('0') and len(digits) > 10:
        digits = digits.lstrip('0')

    if len(digits) == 10:
        digits = '91' + digits

    return f'whatsapp:+{digits}'


def send_registration_email(user, user_type='customer'):
    """
    Send registration confirmation email to user after successful registration.

    Args:
        user: User model instance
        user_type: Type of user ('customer', 'vendor', 'admin')
    """
    subject = 'Welcome to BorewellMart - Registration Successful'

    # Get user's email
    to_email = user.email

    # Prepare context for email template
    context = {
        'user': user,
        'user_type': user_type,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:8000'),
    }

    # Check if user has a profile with phone
    if hasattr(user, 'userprofile'):
        context['phone'] = user.userprofile.phone

    # Render email templates (HTML and plain text)
    html_message = render_to_string(f'emails/registration_{user_type}_email.html', context)
    plain_message = render_to_string(f'emails/registration_{user_type}_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_vendor_registration_email(user, company_name=None):
    """
    Send vendor registration email with pending verification notice.

    Args:
        user: User model instance
        company_name: Optional company name for the vendor
    """
    subject = 'Welcome to BorewellMart - Vendor Registration Submitted'

    to_email = user.email

    context = {
        'user': user,
        'company_name': company_name or user.username,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:8000'),
    }

    # Render email templates
    html_message = render_to_string('emails/registration_vendor_email.html', context)
    plain_message = render_to_string('emails/registration_vendor_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email to customer.

    Args:
        booking: Booking model instance
    """
    subject = f'Booking Confirmed - {booking.subservice.name}'

    to_email = booking.customer.email

    context = {
        'booking': booking,
        'customer': booking.customer,
        'vendor': booking.vendor,
        'service': booking.subservice,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:8000'),
    }

    html_message = render_to_string('emails/booking_confirmation_email.html', context)
    plain_message = render_to_string('emails/booking_confirmation_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_enquiry_notification_email(enquiry):
    """
    Send enquiry notification email to vendor.

    Args:
        enquiry: Enquiry model instance
    """
    subject = f'New Enquiry Received - {enquiry.subservice.name}'

    to_email = enquiry.vendor.email

    context = {
        'enquiry': enquiry,
        'vendor': enquiry.vendor,
        'customer': enquiry.customer,
        'service': enquiry.subservice,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:8000'),
    }

    html_message = render_to_string('emails/enquiry_notification_email.html', context)
    plain_message = render_to_string('emails/enquiry_notification_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_whatsapp_enquiry_notification(enquiry):
    vendor = enquiry.vendor
    phone = vendor.phone

    to_number = format_whatsapp_number(phone)

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_CLOUD_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "service_enquiry",
            "language": {
                "code": "en"
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.ok, response.json()

def build_enquiry_whatsapp_body(enquiry):
    """Build a plain-text WhatsApp message for vendor enquiry notifications."""
    customer_name = enquiry.customer.username or 'Customer'
    service_name = enquiry.subservice.name if enquiry.subservice else 'service'
    vendor_name = enquiry.vendor.company_name or 'Vendor'
    message = enquiry.message or ''
    return (
        f"New enquiry received!\n\n"
        f"Customer: {customer_name}\n"
        f"Service: {service_name}\n"
        f"Message: {message[:1024]}"
    )


def get_missing_whatsapp_credentials():
    missing = []
    if not settings.WHATSAPP_CLOUD_API_URL:
        missing.append('WHATSAPP_CLOUD_API_URL')
    if not settings.WHATSAPP_PHONE_NUMBER_ID:
        missing.append('WHATSAPP_PHONE_NUMBER_ID')
    if not settings.WHATSAPP_CLOUD_TOKEN:
        missing.append('WHATSAPP_CLOUD_TOKEN')
    return missing


def get_missing_twilio_credentials():
    missing = []
    if not settings.TWILIO_ACCOUNT_SID:
        missing.append('TWILIO_ACCOUNT_SID')
    if not settings.TWILIO_AUTH_TOKEN:
        missing.append('TWILIO_AUTH_TOKEN')
    if not settings.TWILIO_FROM_NUMBER:
        missing.append('TWILIO_FROM_NUMBER')
    return missing


def send_whatsapp_text_message(phone, body_text):
    """Send a plain text WhatsApp message via WhatsApp Cloud API."""
    if not phone or not body_text:
        return False, {'error': 'Missing phone number or message body'}

    missing = get_missing_whatsapp_credentials()
    if missing:
        return False, {'error': 'WhatsApp credentials not configured', 'missing': missing}

    to_number = format_whatsapp_number(phone)
    if not to_number:
        return False, {'error': 'Invalid WhatsApp phone number'}

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_CLOUD_TOKEN}',
        'Content-Type': 'application/json',
    }
    payload = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'type': 'text',
        'text': {
            'body': body_text[:4096],
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.ok:
            return True, response.json()

        try:
            body = response.json()
        except ValueError:
            body = response.text
        return False, {
            'status_code': response.status_code,
            'body': body,
        }
    except Exception as e:
        return False, {'error': str(e)}


def send_twilio_sms(phone, body_text):
    """Send SMS via Twilio API."""
    if not phone or not body_text:
        return False, {'error': 'Missing phone number or message body'}

    missing = get_missing_twilio_credentials()
    if missing:
        return False, {'error': 'Twilio credentials not configured', 'missing': missing}

    # Format phone number for Twilio (remove non-digits, add + if needed)
    phone = phone.strip()
    phone = ''.join(filter(str.isdigit, phone))
    if not phone.startswith('+'):
        phone = '+' + phone

    try:
        from twilio.rest import Client
        from twilio.base.exceptions import TwilioRestException

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body_text[:1600],  # Twilio limit is 1600 characters
            from_=settings.TWILIO_FROM_NUMBER,
            to=phone
        )
        print(f'Twilio SMS sent successfully. Message SID: {message.sid}')
        return True, {'sid': message.sid}
    except TwilioRestException as e:
        print(f'Twilio SMS failed: {e.msg} (code {e.code})')
        return False, {
            'error': str(e),
            'twilio_code': e.code,
            'twilio_msg': e.msg,
        }
    except Exception as e:
        print(f'Twilio SMS failed: {e}')
        return False, {'error': str(e)}


def send_whatsapp_customer_response_notification(enquiry):
    """Send the vendor response to the customer via WhatsApp."""
    customer = enquiry.customer
    profile = getattr(customer, 'userprofile', None)
    phone = getattr(profile, 'phone', '') if profile else ''
    if not phone:
        return False, {'error': 'Customer phone number is missing'}

    vendor = enquiry.vendor
    response_text = enquiry.vendor_response or 'The vendor has responded to your enquiry.'
    quote_text = f"Quoted amount: ₹{enquiry.quoted_amount:.2f}\n" if enquiry.quoted_amount else ''
    body_text = (
        f"Hello {customer.username},\n\n"
        f"{vendor.company_name} has responded to your enquiry for {enquiry.subservice.name}.\n\n"
        f"{response_text}\n\n"
        f"{quote_text}"
        f"You can view the response in your BorewellMart account."
    )

    return send_whatsapp_text_message(phone, body_text)


def send_vendor_approval_email(vendor):
    """
    Send vendor account approval email.

    Args:
        vendor: Vendor model instance
    """
    if getattr(vendor, 'is_bulk_registered', False):
        return False

    subject = f'Congratulations! Your Vendor Account has been Approved - {vendor.company_name}'

    to_email = vendor.email

    # Generate password reset link
    user = vendor.user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    password_reset_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/reset/{uid}/{token}/"

    context = {
        'vendor': vendor,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:8000'),
        'password_reset_url': password_reset_url,
        'username': user.username,
    }

    html_message = render_to_string('emails/vendor_approval_email.html', context)
    plain_message = render_to_string('emails/vendor_approval_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_vendor_rejection_email(vendor):
    """
    Send vendor account rejection email.

    Args:
        vendor: Vendor model instance
    """
    subject = f'Update on Your Vendor Application - {vendor.company_name}'

    to_email = vendor.email

    context = {
        'vendor': vendor,
        'frontend_url': getattr(settings, 'FRONTEND_URL', 'http://localhost:8000'),
    }

    html_message = render_to_string('emails/vendor_rejection_email.html', context)
    plain_message = render_to_string('emails/vendor_rejection_email.txt', context)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_whatsapp_booking_confirmation(booking):
    """
    Send WhatsApp notification to vendor when a new booking is confirmed.

    Args:
        booking: Booking model instance

    Returns:
        tuple: (success: bool, response: dict)
    """
    vendor = booking.vendor
    phone = vendor.phone

    if not phone:
        return False, {'error': 'Vendor phone number is missing'}

    to_number = format_whatsapp_number(phone)

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_CLOUD_TOKEN}",
        "Content-Type": "application/json",
    }

    # Get customer name (combine first_name and last_name, or use username)
    customer = booking.customer
    customer_name = f"{customer.first_name} {customer.last_name}".strip() or customer.username

    # Get customer phone from profile
    customer_profile = getattr(customer, 'userprofile', None)
    customer_phone = getattr(customer_profile, 'phone', 'N/A') if customer_profile else 'N/A'

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "booking_notification",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": vendor.company_name
                        },
                        {
                            "type": "text",
                            "text": customer_name
                        },
                        {
                            "type": "text",
                            "text": booking.subservice.name
                        },
                        {
                            "type": "text",
                            "text": booking.address
                        },
                        {
                            "type": "text",
                            "text": customer_phone
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.ok, response.json()


def send_whatsapp_vendor_registration_notification(vendor):
    """
    Send WhatsApp notification to vendor after successful registration.

    Args:
        vendor: Vendor model instance

    Returns:
        tuple: (success: bool, response: dict)
    """
    phone = vendor.phone

    if not phone:
        return False, {'error': 'Vendor phone number is missing'}

    to_number = format_whatsapp_number(phone)

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_CLOUD_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "vendor_registration_submitted",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": vendor.company_name
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.ok, response.json()


def send_whatsapp_vendor_approval_notification(vendor):
    """
    Send WhatsApp notification to vendor when admin approves their trial plan account.
    This is used for vendors who registered without payment.

    Args:
        vendor: Vendor model instance

    Returns:
        tuple: (success: bool, response: dict)
    """
    phone = vendor.phone

    if not phone:
        return False, {'error': 'Vendor phone number is missing'}

    to_number = format_whatsapp_number(phone)

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_CLOUD_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "vendor_account_approved",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": vendor.company_name
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.ok, response.json()


def send_whatsapp_payment_completion_notification(vendor, amount):
    """
    Send WhatsApp notification to vendor after payment completion.
    Vendor is automatically approved after successful payment (no admin approval needed).

    Args:
        vendor: Vendor model instance
        amount: Payment amount (Decimal or str)

    Returns:
        tuple: (success: bool, response: dict)
    """
    phone = vendor.phone

    if not phone:
        return False, {'error': 'Vendor phone number is missing'}

    to_number = format_whatsapp_number(phone)

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_CLOUD_TOKEN}",
        "Content-Type": "application/json",
    }

    # Format amount to Indian currency format
    amount_str = f"₹{amount}" if amount else 'N/A'

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "payment_completion_and_approval",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": vendor.company_name
                        },
                        {
                            "type": "text",
                            "text": amount_str
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.ok, response.json()


def send_whatsapp_plan_renewal_notification(vendor, plan_name, amount, start_date, end_date):
    """
    Send WhatsApp notification to vendor when their plan is renewed or upgraded.
    This is used when a trial vendor upgrades to a paid plan or renews an existing plan.

    Args:
        vendor: Vendor model instance
        plan_name: Name of the new plan
        amount: Plan amount (Decimal or str)
        start_date: Plan start date (date object or str)
        end_date: Plan end date (date object or str)

    Returns:
        tuple: (success: bool, response: dict)
    """
    phone = vendor.phone

    if not phone:
        return False, {'error': 'Vendor phone number is missing'}

    to_number = format_whatsapp_number(phone)

    url = f"{settings.WHATSAPP_CLOUD_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_CLOUD_TOKEN}",
        "Content-Type": "application/json",
    }

    # Format amount and dates
    amount_str = f"₹{amount}" if amount else 'N/A'
    if hasattr(start_date, 'strftime'):
        start_date_str = start_date.strftime('%d-%m-%Y')
    else:
        start_date_str = str(start_date)
    if hasattr(end_date, 'strftime'):
        end_date_str = end_date.strftime('%d-%m-%Y')
    else:
        end_date_str = str(end_date)

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "plan_renewal_success",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": vendor.company_name
                        },
                        {
                            "type": "text",
                            "text": plan_name
                        },
                        {
                            "type": "text",
                            "text": amount_str
                        },
                        {
                            "type": "text",
                            "text": start_date_str
                        },
                        {
                            "type": "text",
                            "text": end_date_str
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print(response.status_code)
    print(response.text)

    return response.ok, response.json()


def compress_image(image_file, max_size=(800, 800), quality=85, format='JPEG'):
    """
    Compress and optimize an image file.

    Args:
        image_file: Uploaded image file
        max_size: Maximum dimensions (width, height)
        quality: JPEG quality (1-100)
        format: Output format (JPEG, PNG, WEBP)

    Returns:
        Compressed image file
    """
    img = Image.open(image_file)

    # Convert RGBA to RGB if saving as JPEG
    if format == 'JPEG' and img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Resize image while maintaining aspect ratio
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Save to memory buffer
    output = io.BytesIO()
    img.save(output, format=format, quality=quality, optimize=True)

    # Create new file-like object
    output.seek(0)
    return output


def validate_image_size(image_file, max_size_mb=2):
    """
    Validate image file size.

    Args:
        image_file: Uploaded image file
        max_size_mb: Maximum allowed size in MB

    Returns:
        tuple: (is_valid, error_message)
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = image_file.size

    if file_size > max_size_bytes:
        return False, f'Image size must be less than {max_size_mb}MB. Current size: {file_size / (1024 * 1024):.2f}MB'

    return True, None


def create_thumbnail(image_file, size=(200, 200), quality=85):
    """
    Create a thumbnail from an image.

    Args:
        image_file: Uploaded image file
        size: Thumbnail dimensions (width, height)
        quality: JPEG quality (1-100)

    Returns:
        Thumbnail image file
    """
    img = Image.open(image_file)

    # Convert RGBA to RGB if needed
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Create thumbnail
    img.thumbnail(size, Image.Resampling.LANCZOS)

    # Save to memory buffer
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)

    # Create new file-like object
    output.seek(0)
    return output


def generate_upi_qr_code(upi_id, amount, name=None, note=None):
    """
    Generate UPI QR code for payment

    Args:
        upi_id: UPI ID (e.g., vendor@upi)
        amount: Amount to pay
        name: Payee name (optional)
        note: Transaction note (optional)

    Returns:
        InMemoryUploadedFile containing the QR code image
    """
    try:
        import qrcode
    except ImportError:
        raise ImportError("qrcode library is not installed. Run: pip install qrcode[pil]")

    from django.core.files.uploadedfile import InMemoryUploadedFile

    # Construct UPI payment URL
    upi_url = f"upi://pay?pa={upi_id}&am={amount}"

    if name:
        upi_url += f"&pn={name}"
    if note:
        upi_url += f"&tn={note}"
    upi_url += "&cu=INR"  # Currency

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Create InMemoryUploadedFile
    return InMemoryUploadedFile(
        buffer,
        None,
        'upi_qr.png',
        'image/png',
        buffer.getbuffer().nbytes,
        None
    )


def generate_booking_qr_code(booking):
    """
    Generate UPI QR code for a specific booking

    Args:
        booking: Booking instance

    Returns:
        InMemoryUploadedFile containing the QR code image
    """
    vendor = booking.vendor

    # Get vendor service price if available
    from core.models import VendorService
    vendor_service = VendorService.objects.filter(
        vendor=vendor,
        subservice=booking.subservice
    ).first()

    amount = vendor_service.price if vendor_service else 0

    return generate_upi_qr_code(
        upi_id=vendor.upi_id or 'vendor@upi',
        amount=amount,
        name=vendor.company_name,
        note=f"Booking #{booking.id} - {booking.subservice.name}"
    )
