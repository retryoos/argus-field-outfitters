# Tests for the role based security. The point of these is that every check is
# made against the server, not against whether a link happens to be on the page,
# so each one asks for the url directly the way somebody typing it in would
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.roles import EMPLOYEE, OWNER, role_of, set_role
from catalog.models import Category, Product, Subcategory


class RoleTestCase(TestCase):
    def setUp(self):
        # The groups and their permissions are created by the accounts migration,
        # so they already exist in the test database
        self.customer = User.objects.create_user(username='customer', password='pw-for-tests')
        self.employee = User.objects.create_user(username='employee', password='pw-for-tests')
        self.owner = User.objects.create_user(username='owner', password='pw-for-tests')
        self.root = User.objects.create_superuser(username='root', password='pw-for-tests')
        set_role(self.employee, EMPLOYEE)
        set_role(self.owner, OWNER)

        category = Category.objects.create(name='Apparel', slug='apparel')
        subcategory = Subcategory.objects.create(category=category, name='Jackets', slug='jackets')
        self.product = Product.objects.create(
            name='Rain Shell', brand='Condor', subcategory=subcategory,
            price=Decimal('89.99'), stock=5,
        )


class GroupsCarryThePermissions(RoleTestCase):
    def test_the_groups_grant_what_they_should(self):
        self.assertTrue(self.employee.has_perm('accounts.access_backoffice'))
        self.assertFalse(self.employee.has_perm('accounts.manage_users'))

        self.assertTrue(self.owner.has_perm('accounts.access_backoffice'))
        self.assertTrue(self.owner.has_perm('accounts.manage_users'))

        self.assertFalse(self.customer.has_perm('accounts.access_backoffice'))

    def test_the_superuser_passes_without_being_in_any_group(self):
        self.assertTrue(self.root.has_perm('accounts.access_backoffice'))
        self.assertTrue(self.root.has_perm('accounts.manage_users'))
        self.assertEqual(self.root.groups.count(), 0)

    def test_a_role_is_read_back_from_the_groups(self):
        self.assertEqual(role_of(self.customer), 'Customer')
        self.assertEqual(role_of(self.employee), EMPLOYEE)
        self.assertEqual(role_of(self.owner), OWNER)
        self.assertEqual(role_of(self.root), 'Administrator')

    def test_changing_a_role_moves_the_user_between_groups(self):
        set_role(self.customer, EMPLOYEE)
        self.assertEqual(role_of(self.customer), EMPLOYEE)

        # Going back to Customer means belonging to neither group
        set_role(self.customer, 'Customer')
        self.assertEqual(self.customer.groups.count(), 0)
        self.assertFalse(User.objects.get(pk=self.customer.pk).has_perm('accounts.access_backoffice'))


class TheBackofficeIsClosedToCustomers(RoleTestCase):
    def test_a_guest_is_sent_to_the_sign_in_page(self):
        response = self.client.get(reverse('backoffice:panel_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_a_customer_is_refused_every_backoffice_url(self):
        self.client.force_login(self.customer)
        for name, args in [
            ('backoffice:panel_home', []),
            ('backoffice:product_list', []),
            ('backoffice:product_create', []),
            ('backoffice:product_edit', [self.product.pk]),
            ('backoffice:product_delete', [self.product.pk]),
            ('backoffice:category_list', []),
            ('backoffice:subcategory_list', []),
            ('backoffice:order_list', []),
            ('backoffice:user_list', []),
        ]:
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 403, f'{name} let a customer in')

    def test_a_customer_cannot_post_either(self):
        # Refusing the GET is not enough on its own, the write has to be refused
        self.client.force_login(self.customer)
        response = self.client.post(reverse('backoffice:product_delete', args=[self.product.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


class EmployeesStopShortOfUserManagement(RoleTestCase):
    def test_an_employee_can_work_the_catalogue(self):
        self.client.force_login(self.employee)
        for name in ('backoffice:panel_home', 'backoffice:product_list', 'backoffice:order_list'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_an_employee_cannot_reach_user_management_by_url(self):
        self.client.force_login(self.employee)
        self.assertEqual(self.client.get(reverse('backoffice:user_list')).status_code, 403)
        self.assertEqual(
            self.client.get(reverse('backoffice:user_role_edit', args=[self.customer.pk])).status_code,
            403,
        )

    def test_an_employee_is_not_offered_the_link_either(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('backoffice:panel_home'))
        self.assertNotContains(response, reverse('backoffice:user_list'))


class OwnersManageRoles(RoleTestCase):
    def test_an_owner_sees_the_user_screen_and_the_link(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('backoffice:user_list')).status_code, 200)
        response = self.client.get(reverse('backoffice:panel_home'))
        self.assertContains(response, reverse('backoffice:user_list'))

    def test_an_owner_can_promote_a_customer(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse('backoffice:user_role_edit', args=[self.customer.pk]), {'role': EMPLOYEE}
        )
        self.assertEqual(role_of(User.objects.get(pk=self.customer.pk)), EMPLOYEE)

    def test_the_root_account_is_left_out_of_the_role_screen(self):
        # The superuser's access does not come from a group, so there is nothing
        # to set and the screen refuses rather than pretending otherwise
        self.client.force_login(self.owner)
        self.assertEqual(
            self.client.get(reverse('backoffice:user_role_edit', args=[self.root.pk])).status_code,
            403,
        )

    def test_a_made_up_role_is_refused(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse('backoffice:user_role_edit', args=[self.customer.pk]), {'role': 'Superuser'}
        )
        self.assertEqual(role_of(User.objects.get(pk=self.customer.pk)), 'Customer')
