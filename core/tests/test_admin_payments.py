from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Vendor, VendorPayment


class AdminPaymentsTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='testpass123',
        )
        self.vendor = Vendor.objects.create(
            user=get_user_model().objects.create_user(
                username='vendorpay',
                email='vendorpay@example.com',
                password='testpass123',
            ),
            company_name='Pay Vendor',
            phone='1234567890',
            email='vendorpay@example.com',
            address='Test address',
        )
        VendorPayment.objects.create(
            vendor=self.vendor,
            plan_type='basic',
            amount=1000,
            status='completed',
            paid_amount=1000,
        )

    def test_admin_payments_page_handles_method_filter_without_error(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse('vendor_payments_list'),
            {'status': 'all', 'method': 'razorpay', 'date_from': '', 'date_to': ''},
        )

        self.assertEqual(response.status_code, 200)
