from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Reset all vendor passwords to a default password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='Vendor@123',
            help='Default password to set (default: Vendor@123)',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Reset password for specific vendor username only',
        )

    def handle(self, *args, **options):
        password = options['password']
        username = options.get('username')

        if username:
            try:
                user = User.objects.get(username=username)
                # Check if user is a vendor
                if not hasattr(user, 'userprofile') or user.userprofile.user_type != 'vendor':
                    self.stdout.write(
                        self.style.WARNING(f"User '{username}' is not a vendor")
                    )
                    return
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Password reset for vendor: {username}")
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{username}' not found")
                )
        else:
            vendors = UserProfile.objects.filter(user_type='vendor')
            count = vendors.count()

            for i, vp in enumerate(vendors, 1):
                vp.user.set_password(password)
                vp.user.save()
                self.stdout.write(f"[{i}/{count}] Reset password for: {vp.user.username}")

            self.stdout.write(
                self.style.SUCCESS(f"\nSuccessfully reset {count} vendor passwords to: {password}")
            )
