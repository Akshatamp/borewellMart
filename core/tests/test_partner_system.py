from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import City, Partner, PartnerCoupon, PartnerReferral, UserProfile, Vendor

User = get_user_model()

PASSWORD = 'S3cureTestPass!9'


class PartnerReferralFlowTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='Test City', state='Karnataka')

        self.partner_user = User.objects.create_user(
            username='partner1', email='partner@example.com', password=PASSWORD,
        )
        UserProfile.objects.create(user=self.partner_user, user_type='partner', phone='9999999999')
        self.partner = Partner.objects.create(
            user=self.partner_user, company_name='Test Partner', phone='9999999999', status='active',
        )

        self.coupon = PartnerCoupon.objects.create(partner=self.partner, code='TESTCOUP1', max_uses=5)

    def register_vendor(self, referral_code=''):
        session = self.client.session
        session['otp_verified_email'] = 'newvendor@example.com'
        session.save()

        return self.client.post(reverse('vendor_user_register'), {
            'username': 'newvendor1',
            'email': 'newvendor@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
            'phone': '8888888888',
            'city': self.city.id,
            'state': 'Karnataka',
            'company_name': 'New Vendor Co',
            'experience': 5,
            'address': 'Test Address',
            'license_number': '',
            'referral_code': referral_code,
        })

    def test_vendor_registration_with_coupon_creates_referral(self):
        response = self.register_vendor(referral_code='TESTCOUP1')
        self.assertRedirects(
            response, reverse('vendor_dashboard'), fetch_redirect_response=False,
        )

        vendor = Vendor.objects.get(company_name='New Vendor Co')
        referral = PartnerReferral.objects.get(vendor=vendor)
        self.assertEqual(referral.partner, self.partner)
        self.assertEqual(referral.source, 'coupon')
        self.assertEqual(referral.coupon, self.coupon)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 1)

    def test_vendor_registration_with_partner_ref_link_code(self):
        response = self.register_vendor(referral_code=self.partner.referral_code)
        self.assertRedirects(
            response, reverse('vendor_dashboard'), fetch_redirect_response=False,
        )

        vendor = Vendor.objects.get(company_name='New Vendor Co')
        referral = PartnerReferral.objects.get(vendor=vendor)
        self.assertEqual(referral.partner, self.partner)
        self.assertEqual(referral.source, 'link')
        self.assertIsNone(referral.coupon)

    def test_ref_link_get_stores_code_in_session(self):
        self.client.get(reverse('vendor_user_register'), {'ref': self.partner.referral_code})
        self.assertEqual(self.client.session.get('partner_ref_code'), self.partner.referral_code)

    def test_session_ref_code_attributes_on_registration(self):
        session = self.client.session
        session['partner_ref_code'] = self.partner.referral_code
        session.save()
        self.register_vendor(referral_code='')

        self.assertEqual(PartnerReferral.objects.count(), 1)
        self.assertEqual(PartnerReferral.objects.first().source, 'link')

    def test_invalid_referral_code_ignored(self):
        self.register_vendor(referral_code='BOGUS123')
        self.assertEqual(PartnerReferral.objects.count(), 0)

    def test_referral_is_permanent_and_unique_per_vendor(self):
        self.register_vendor(referral_code='TESTCOUP1')
        self.assertEqual(PartnerReferral.objects.count(), 1)

    def test_inactive_partner_code_not_accepted(self):
        self.partner.status = 'suspended'
        self.partner.save()
        self.register_vendor(referral_code=self.partner.referral_code)
        self.assertEqual(PartnerReferral.objects.count(), 0)

    def test_exhausted_coupon_not_accepted(self):
        self.coupon.times_used = 5
        self.coupon.save()
        self.register_vendor(referral_code='TESTCOUP1')
        self.assertEqual(PartnerReferral.objects.count(), 0)


class PartnerAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='partner1', email='partner@example.com', password=PASSWORD,
        )
        UserProfile.objects.create(user=self.user, user_type='partner', phone='9999999999')
        self.partner = Partner.objects.create(
            user=self.user, company_name='Test Partner', phone='9999999999', status='active',
        )

    def test_partner_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'partner1', 'password': PASSWORD,
        })
        self.assertRedirects(response, reverse('partner_dashboard'))

    def test_suspended_partner_login_blocked(self):
        self.partner.status = 'suspended'
        self.partner.save()
        response = self.client.post(reverse('login'), {
            'username': 'partner1', 'password': PASSWORD,
        })
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_partner_dashboard_requires_partner_user(self):
        other = User.objects.create_user(username='cust1', email='c@example.com', password=PASSWORD)
        UserProfile.objects.create(user=other, user_type='customer', phone='1')
        self.client.force_login(other)
        response = self.client.get(reverse('partner_dashboard'))
        self.assertRedirects(response, reverse('home'))

    def test_partner_dashboard_shows_stats(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('partner_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.partner.referral_code)

    def test_coupon_limit_enforced(self):
        self.partner.max_coupons = 1
        self.partner.save()
        PartnerCoupon.objects.create(partner=self.partner, code='FIRSTCOP')
        self.client.force_login(self.user)
        response = self.client.post(reverse('partner_coupon_add'), {'code': 'SECONDCOP'})
        self.assertRedirects(response, reverse('partner_dashboard'))
        self.assertEqual(self.partner.coupons.count(), 1)

    def test_duplicate_coupon_code_rejected(self):
        existing = PartnerCoupon.objects.create(partner=self.partner, code='UNIQUE01')
        self.client.force_login(self.user)
        self.client.post(reverse('partner_coupon_add'), {'code': 'UNIQUE01'})
        self.assertEqual(self.partner.coupons.filter(code='UNIQUE01').count(), 1)


class AdminPartnerTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin1', email='admin@example.com', password=PASSWORD)
        self.user = User.objects.create_user(username='partner1', email='partner@example.com', password=PASSWORD)
        UserProfile.objects.create(user=self.user, user_type='partner', phone='9999999999')
        self.partner = Partner.objects.create(
            user=self.user, company_name='Test Partner', phone='9999999999', status='pending',
        )

    def test_admin_partners_requires_superuser(self):
        response = self.client.get(reverse('admin_partners'))
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    def test_admin_can_approve_partner(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('admin_partners'), {
            'action': 'status', 'partner_id': self.partner.id, 'status': 'active',
        })
        self.assertRedirects(response, reverse('admin_partners'))
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.status, 'active')

    def test_admin_can_create_partner(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('admin_partners'), {
            'action': 'create',
            'username': 'newpartner',
            'email': 'newpartner@example.com',
            'password': PASSWORD,
            'company_name': 'New Partner',
            'phone': '7777777777',
            'max_coupons': 5,
        })
        self.assertRedirects(response, reverse('admin_partners'))
        self.assertTrue(Partner.objects.filter(company_name='New Partner', status='active').exists())

    def test_admin_can_delete_partner(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('admin_partners'), {
            'action': 'delete', 'partner_id': self.partner.id,
        })
        self.assertFalse(Partner.objects.filter(pk=self.partner.id).exists())
        self.assertFalse(User.objects.filter(username='partner1').exists())


class StepTwoVendorReferralTests(TestCase):
    """Referral tracking for vendors completing the two-step flow (/vendor/register/)"""

    def setUp(self):
        self.city = City.objects.create(name='Test City', state='Karnataka')
        self.vendor_user = User.objects.create_user(
            username='halfvendor', email='half@example.com', password=PASSWORD,
        )
        UserProfile.objects.create(user=self.vendor_user, user_type='vendor', phone='7777777777')
        self.partner = Partner.objects.create(
            user=User.objects.create_user(username='p2', email='p2@example.com', password=PASSWORD),
            company_name='Step Two Partner', phone='9999999999', status='active',
        )
        self.coupon = PartnerCoupon.objects.create(partner=self.partner, code='STEPTW0', max_uses=5)

    def complete_vendor_profile(self, referral_code=''):
        self.client.force_login(self.vendor_user)
        return self.client.post(reverse('vendor_register'), {
            'company_name': 'Step Two Vendor',
            'city': self.city.id,
            'state': 'Karnataka',
            'experience': 3,
            'phone': '7777777777',
            'email': 'half@example.com',
            'address': 'Step Two Address',
            'license_number': '',
            'referral_code': referral_code,
        })

    def test_step_two_with_coupon_creates_referral(self):
        response = self.complete_vendor_profile(referral_code='STEPTW0')
        self.assertRedirects(response, reverse('vendor_payment_page'), fetch_redirect_response=False)
        vendor = Vendor.objects.get(company_name='Step Two Vendor')
        referral = PartnerReferral.objects.get(vendor=vendor)
        self.assertEqual(referral.partner, self.partner)
        self.assertEqual(referral.source, 'coupon')
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.times_used, 1)

    def test_step_two_ref_link_session_attributes(self):
        self.client.force_login(self.vendor_user)
        self.client.get(reverse('vendor_register'), {'ref': self.partner.referral_code})
        self.assertEqual(self.client.session.get('partner_ref_code'), self.partner.referral_code)
        self.complete_vendor_profile()
        self.assertEqual(PartnerReferral.objects.count(), 1)
        self.assertEqual(PartnerReferral.objects.first().source, 'link')

    def test_step_two_without_code_no_referral(self):
        self.complete_vendor_profile()
        self.assertEqual(PartnerReferral.objects.count(), 0)


class CustomerRegisterForcesCustomerTypeTests(TestCase):
    """/register/customer/ must never create vendor/partner accounts"""

    def setUp(self):
        self.city = City.objects.create(name='Force City', state='Karnataka')

    def _post_register(self, user_type):
        return self.client.post(reverse('register'), {
            'username': 'tamper1',
            'email': 'tamper@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
            'phone': '8888888888',
            'user_type': user_type,
            'city': self.city.id,
            'state': 'Karnataka',
        })

    def test_vendor_type_tampering_forced_to_customer(self):
        self._post_register('vendor')
        profile = UserProfile.objects.get(user__username='tamper1')
        self.assertEqual(profile.user_type, 'customer')
        self.assertFalse(Vendor.objects.filter(user__username='tamper1').exists())

    def test_partner_type_tampering_forced_to_customer(self):
        self._post_register('partner')
        profile = UserProfile.objects.get(user__username='tamper1')
        self.assertEqual(profile.user_type, 'customer')
        self.assertFalse(Partner.objects.filter(user__username='tamper1').exists())
