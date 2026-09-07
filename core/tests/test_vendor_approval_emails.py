from django.core import mail
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from core.models import Vendor
from core.utils import send_vendor_approval_email


class VendorApprovalEmailTests(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_bulk_registered_vendor_does_not_receive_approval_email(self):
        user = get_user_model().objects.create_user(
            username='bulkvendor',
            email='bulkvendor@example.com',
            password='testpass123',
        )
        vendor = Vendor.objects.create(
            user=user,
            company_name='Bulk Vendor Ltd',
            phone='1234567890',
            email='bulkvendor@example.com',
            address='Test address',
            is_bulk_registered=True,
        )

        result = send_vendor_approval_email(vendor)

        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_regular_vendor_still_receives_approval_email(self):
        user = get_user_model().objects.create_user(
            username='regularvendor',
            email='regularvendor@example.com',
            password='testpass123',
        )
        vendor = Vendor.objects.create(
            user=user,
            company_name='Regular Vendor Ltd',
            phone='0987654321',
            email='regularvendor@example.com',
            address='Test address',
            is_bulk_registered=False,
        )

        result = send_vendor_approval_email(vendor)

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
