# Tests for registration, the profile and the dashboard.
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from catalog.forms import postcode_validator
from django.core.exceptions import ValidationError

from .models import Profile


class RegistrationTests(TestCase):
    def test_signing_up_creates_an_account_and_signs_it_in(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newcomer', 'email': 'newcomer@example.com',
            'first_name': 'New', 'last_name': 'Comer',
            'password1': 'a-long-enough-password', 'password2': 'a-long-enough-password',
        })
        self.assertRedirects(response, reverse('catalog:index'))
        self.assertTrue(User.objects.filter(username='newcomer').exists())
        # Signed in already, so there is no second trip through the login page.
        self.assertEqual(int(self.client.session['_auth_user_id']),
                         User.objects.get(username='newcomer').pk)

    def test_a_new_account_is_only_a_customer(self):
        self.client.post(reverse('accounts:register'), {
            'username': 'newcomer', 'email': 'newcomer@example.com',
            'password1': 'a-long-enough-password', 'password2': 'a-long-enough-password',
        })
        newcomer = User.objects.get(username='newcomer')
        self.assertFalse(newcomer.has_perm('accounts.access_backoffice'))
        self.assertFalse(newcomer.is_superuser)

    def test_the_two_passwords_have_to_match(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newcomer', 'email': 'newcomer@example.com',
            'password1': 'a-long-enough-password', 'password2': 'something-else',
        })
        self.assertFalse(User.objects.filter(username='newcomer').exists())
        self.assertTrue(response.context['form'].errors)

    def test_the_username_has_to_be_free(self):
        User.objects.create_user(username='taken', password='pw-for-tests')
        response = self.client.post(reverse('accounts:register'), {
            'username': 'taken', 'email': 'x@example.com',
            'password1': 'a-long-enough-password', 'password2': 'a-long-enough-password',
        })
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(User.objects.filter(username='taken').count(), 1)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shopper', password='pw-for-tests')
        self.client.force_login(self.user)

    def test_a_profile_is_made_on_demand_for_an_account_without_one(self):
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_the_profile_page_names_the_role(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertContains(response, 'Customer')

    def test_editing_the_profile_saves_the_address(self):
        self.client.post(reverse('accounts:profile_edit'), {
            'first_name': 'Test', 'last_name': 'Shopper', 'email': 'shopper@example.com',
            'phone': '2101234567', 'shipping_address': 'Street 1',
            'shipping_city': 'Athens', 'shipping_postcode': '14234',
            'shipping_country': 'Greece',
        })
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.shipping_city, 'Athens')
        self.assertEqual(User.objects.get(pk=self.user.pk).email, 'shopper@example.com')

    def test_the_dashboard_needs_an_account(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class PostcodeTests(TestCase):
    def test_it_takes_the_formats_the_country_list_implies(self):
        # The dropdown offers the whole world, so a digits only rule would turn
        # away real addresses.
        for code in ('14234', 'SW1A 1AA', 'K1A 0B1', '1011 AB', '75008'):
            postcode_validator(code)

    def test_it_still_turns_away_nonsense(self):
        for code in ('', '!!', '#$%', 'x' * 20):
            with self.assertRaises(ValidationError):
                postcode_validator(code)
