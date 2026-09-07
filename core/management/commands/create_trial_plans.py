"""
Management command to create trial plans for all verified vendors who don't have plans.
Run this command to backfill trial plans for existing vendors.

Usage: python manage.py create_trial_plans
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, timedelta
from core.models import Vendor, VendorPlan


class Command(BaseCommand):
    help = 'Create 7-day trial plans for all verified vendors without existing plans'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting trial plan creation process...'))

        # Get all verified vendors
        verified_vendors = Vendor.objects.filter(verification_status='verified')
        total_verified = verified_vendors.count()

        if total_verified == 0:
            self.stdout.write(self.style.WARNING('No verified vendors found.'))
            return

        self.stdout.write(f'Found {total_verified} verified vendors.')

        plans_created = 0
        plans_skipped = 0
        errors = []

        for vendor in verified_vendors:
            try:
                # Check if vendor already has a plan
                existing_plan = VendorPlan.objects.filter(vendor=vendor).first()

                if existing_plan:
                    # Check if the existing plan is expired
                    existing_plan.update_status()

                    if existing_plan.status == 'expired':
                        # Create new trial plan starting from today
                        trial_start = date.today()
                        trial_end = trial_start + timedelta(days=7)

                        new_plan = VendorPlan.objects.create(
                            vendor=vendor,
                            plan_type='basic',
                            plan_name='Trial Plan (7 Days)',
                            price=0,
                            start_date=trial_start,
                            end_date=trial_end,
                            status='active',
                            description='Free trial plan for 7 days. Upgrade to continue services.'
                        )
                        plans_created += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created trial plan for {vendor.company_name} (expired previous plan)'
                            )
                        )
                    else:
                        plans_skipped += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'- Skipped {vendor.company_name} (already has active plan: {existing_plan.plan_name})'
                            )
                        )
                else:
                    # No plan exists - create trial plan
                    # Calculate trial period based on vendor creation date or today
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
                    plans_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created trial plan for {vendor.company_name}'
                        )
                    )

            except Exception as e:
                errors.append(f'Error processing {vendor.company_name}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error processing {vendor.company_name}: {str(e)}'
                    )
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('TRIAL PLAN CREATION SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f'Total verified vendors: {total_verified}')
        self.stdout.write(self.style.SUCCESS(f'Plans created: {plans_created}'))
        self.stdout.write(self.style.WARNING(f'Plans skipped (already have active plans): {plans_skipped}'))

        if errors:
            self.stdout.write(self.style.ERROR(f'Errors: {len(errors)}'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))

        self.stdout.write('='*50)

        if plans_created > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created trial plans for {plans_created} vendors!'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    '\nNo new trial plans created. All verified vendors already have active plans.'
                )
            )
