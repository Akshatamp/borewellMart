from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Enquiry, Sector, Service, SubService, Vendor, VendorService
from core.utils import send_whatsapp_enquiry_notification


class SendEnquiryTests(TestCase):
    def setUp(self):
        self.customer_user = get_user_model().objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
        )
        self.vendor_user = get_user_model().objects.create_user(
            username='vendor1',
            email='vendor@example.com',
            password='testpass123',
        )

        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            company_name='Test Vendor',
            phone='1234567890',
            email='vendor@example.com',
            address='Test address',
        )

        self.sector = Sector.objects.create(id='sector-1', name='Agriculture')
        self.service = Service.objects.create(id='service-1', sector=self.sector, name='Irrigation')
        self.vendor_subservice = SubService.objects.create(
            id='subservice-1',
            service=self.service,
            name='Drip Irrigation',
        )
        self.other_subservice = SubService.objects.create(
            id='subservice-2',
            service=self.service,
            name='Sprinkler Installation',
        )
        VendorService.objects.create(vendor=self.vendor, subservice=self.vendor_subservice, price=100)

    def test_send_enquiry_page_shows_only_vendor_services(self):
        self.client.force_login(self.customer_user)

        response = self.client.get(
            reverse('send_enquiry', args=[self.vendor.id]),
            {'subservice': self.vendor_subservice.id},
        )

        self.assertContains(response, f'value="{self.vendor_subservice.id}"')
        self.assertNotContains(response, f'value="{self.other_subservice.id}"')

    @patch('core.views.send_whatsapp_enquiry_notification', return_value=(True, 'ok'))
    def test_send_enquiry_submission_creates_enquiry(self, mocked_notification):
        self.client.force_login(self.customer_user)

        response = self.client.post(
            reverse('send_enquiry', args=[self.vendor.id]),
            {
                'subservice': self.vendor_subservice.id,
                'message': 'Need drip irrigation for my farm.',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Enquiry.objects.filter(
                customer=self.customer_user,
                vendor=self.vendor,
                subservice=self.vendor_subservice,
            ).exists()
        )
        mocked_notification.assert_called_once()

    @patch('core.utils.send_whatsapp_text_message', return_value=(True, {'id': 'whatsapp-msg'}))
    def test_send_whatsapp_enquiry_notification_falls_back_to_text_when_template_missing(self, mocked_text_message):
        self.vendor.phone = '9876543210'
        self.vendor.save()

        enquiry = Enquiry.objects.create(
            customer=self.customer_user,
            vendor=self.vendor,
            subservice=self.vendor_subservice,
            message='Need drip irrigation for my farm.',
        )

        with patch.object(settings, 'WHATSAPP_TEMPLATE_NAME', ''):
            success, result = send_whatsapp_enquiry_notification(enquiry)

        self.assertTrue(success)
        self.assertEqual(result['id'], 'whatsapp-msg')
        mocked_text_message.assert_called_once()
