"""
Management command to send plan expiry notifications to vendors.
Run this command periodically (e.g., daily via cron or celery) to send notifications.

Usage: python manage.py send_plan_notifications
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import date, timedelta
from core.models import VendorPlan, PlanNotification


class Command(BaseCommand):
    help = 'Send plan expiry notifications to vendors'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting plan notification process...'))
        
        # Get all active plans
        active_plans = VendorPlan.objects.filter(status='active')
        
        notification_count = 0
        email_count = 0
        
        for plan in active_plans:
            # Update plan status if expired
            plan.update_status()
            
            if plan.status == 'expired':
                continue
            
            # Check how many days until expiry
            days_until_expiry = plan.days_until_expiry()
            notification_days = plan.get_notification_days()
            
            # Check if we need to send notification
            if days_until_expiry in notification_days:
                # Determine notification type
                if days_until_expiry == 7:
                    notification_type = '7_day_before'
                    message_days = '7 days'
                elif days_until_expiry == 3:
                    notification_type = '3_day_before'
                    message_days = '3 days'
                elif days_until_expiry == 2:
                    notification_type = '2_day_before'
                    message_days = '2 days'
                else:  # 1 day
                    notification_type = '1_day_before'
                    message_days = '1 day'
                
                # Check if notification already exists for this date
                notification_exists = PlanNotification.objects.filter(
                    plan=plan,
                    notification_type=notification_type,
                    notification_date=date.today()
                ).exists()
                
                if not notification_exists:
                    # Create notification
                    notification_text = (
                        f"Your {plan.plan_name} plan will expire in {message_days}. "
                        f"Expiry date: {plan.end_date}. "
                        f"Please renew your plan to continue uninterrupted service."
                    )
                    
                    notification = PlanNotification.objects.create(
                        plan=plan,
                        notification_type=notification_type,
                        notification_date=date.today(),
                        notification_text=notification_text
                    )
                    notification_count += 1
                    
                    # Send email notification
                    try:
                        self.send_notification_email(plan, notification, message_days)
                        notification.email_sent = True
                        notification.save()
                        email_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to send email for {plan.vendor.company_name}: {str(e)}"
                            )
                        )
        
        # Also send expiry notification for plans that just expired
        expired_plans = VendorPlan.objects.filter(status='expired')
        for plan in expired_plans:
            # Check if we already sent expiry notification
            expiry_notif_exists = PlanNotification.objects.filter(
                plan=plan,
                notification_type='expired',
                notification_date__gte=plan.end_date
            ).exists()
            
            if not expiry_notif_exists:
                notification_text = (
                    f"Your {plan.plan_name} plan has expired on {plan.end_date}. "
                    f"Please renew your plan immediately to restore your services."
                )
                
                notification = PlanNotification.objects.create(
                    plan=plan,
                    notification_type='expired',
                    notification_date=date.today(),
                    notification_text=notification_text
                )
                notification_count += 1
                
                try:
                    self.send_expiry_notification_email(plan, notification)
                    notification.email_sent = True
                    notification.save()
                    email_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to send expiry email for {plan.vendor.company_name}: {str(e)}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed notifications:\n'
                f'- Notifications created: {notification_count}\n'
                f'- Emails sent: {email_count}'
            )
        )

    def send_notification_email(self, plan, notification, message_days):
        """Send plan expiry reminder email"""
        vendor = plan.vendor
        user_email = vendor.user.email
        
        context = {
            'vendor_name': vendor.company_name,
            'plan_name': plan.plan_name,
            'plan_type': plan.get_plan_type_display(),
            'message_days': message_days,
            'expiry_date': plan.end_date,
            'plan_price': plan.price,
            'renewal_link': f'/vendor/plans/renew/{plan.id}/',
        }
        
        subject = f'Your {plan.plan_name} Plan Expires in {message_days}'
        
        # Try to render HTML email template if it exists
        try:
            html_message = render_to_string('emails/plan_expiry_notification.html', context)
        except:
            html_message = None
        
        # Fallback plain text
        message = (
            f"Hi {vendor.company_name},\n\n"
            f"Your {plan.plan_name} plan will expire in {message_days}.\n"
            f"Expiry Date: {plan.end_date}\n"
            f"Plan Price: ₹{plan.price}\n\n"
            f"Please renew your plan to avoid service interruption.\n\n"
            f"Best regards,\n"
            f"BorewellMart Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@borewellmart.com',
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )

    def send_expiry_notification_email(self, plan, notification):
        """Send plan expired notification email"""
        vendor = plan.vendor
        user_email = vendor.user.email
        
        context = {
            'vendor_name': vendor.company_name,
            'plan_name': plan.plan_name,
            'plan_type': plan.get_plan_type_display(),
            'expiry_date': plan.end_date,
            'renewal_link': f'/vendor/plans/renew/{plan.id}/',
        }
        
        subject = f'Your {plan.plan_name} Plan Has Expired'
        
        try:
            html_message = render_to_string('emails/plan_expired_notification.html', context)
        except:
            html_message = None
        
        message = (
            f"Hi {vendor.company_name},\n\n"
            f"Your {plan.plan_name} plan has expired on {plan.end_date}.\n\n"
            f"Please renew your plan immediately to restore your services on BorewellMart.\n\n"
            f"Best regards,\n"
            f"BorewellMart Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email='noreply@borewellmart.com',
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
