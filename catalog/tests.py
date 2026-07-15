# Tests for the shop side, the cart, the stock rules, the checkout and the
# recommender. These run against a throwaway database, so nothing here touches
# the real products or orders.
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Order, Product, Rating, RecentlyViewed, Subcategory
from .recommendations import recommendations_for_user


class ShopTestCase(TestCase):
    # Builds the same shape of data every test below starts from.
    def setUp(self):
        self.category = Category.objects.create(name='Apparel', slug='apparel')
        self.subcategory = Subcategory.objects.create(
            category=self.category, name='Jackets', slug='jackets'
        )
        self.product = Product.objects.create(
            name='Rain Shell', brand='Condor', subcategory=self.subcategory,
            price=Decimal('89.99'), stock=5,
        )
        self.user = User.objects.create_user(username='shopper', password='pw-for-tests')

    def make_product(self, name, stock=5, price='10.00'):
        return Product.objects.create(
            name=name, brand='Argus', subcategory=self.subcategory,
            price=Decimal(price), stock=stock,
        )


class CartTests(ShopTestCase):
    def test_guest_can_fill_a_cart(self):
        # The whole point of keeping the cart in the session is that no account
        # is needed to start shopping.
        response = self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['cart_count'], 1)

    def test_cart_refuses_to_go_past_the_stock(self):
        self.product.stock = 2
        self.product.save()
        response = self.client.post(
            reverse('catalog:cart_update', args=[self.product.pk]), {'quantity': 10}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Only 2 left', response.json()['error'])

    def test_quantity_zero_removes_the_line(self):
        self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        response = self.client.post(
            reverse('catalog:cart_update', args=[self.product.pk]), {'quantity': 0}
        )
        self.assertTrue(response.json()['removed'])

    def test_a_deleted_product_leaves_nothing_behind_in_the_cart(self):
        # A product can be taken out of the catalogue while it is still sitting
        # in someone's session. The count and the total have to agree that the
        # cart is empty, otherwise an order goes through for nothing.
        self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        self.product.delete()
        response = self.client.get(reverse('catalog:cart'))
        self.assertEqual(len(response.context['cart']), 0)
        self.assertEqual(response.context['cart'].total_price(), 0)

    def test_browsing_does_not_start_a_session(self):
        # The navbar badge builds a Cart on every page, which should not hand a
        # session to somebody who is only looking around.
        self.client.get(reverse('catalog:index'))
        self.assertNotIn('cart', self.client.session)


# Blanking the Stripe key puts the checkout on the path it takes when no keys
# are configured, where the order completes on the spot instead of handing off
# to Stripe's page. That keeps these tests off the network and stops them
# behaving differently depending on what is in someone's .env.
@override_settings(STRIPE_SECRET_KEY='')
class CheckoutTests(ShopTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        self.address = {
            'ship_full_name': 'Test Shopper', 'ship_address': 'Street 1',
            'ship_city': 'Athens', 'ship_postcode': '14234', 'ship_country': 'Greece',
        }

    def test_an_empty_cart_cannot_check_out(self):
        response = self.client.get(reverse('catalog:checkout'))
        self.assertRedirects(response, reverse('catalog:cart'))

    def test_checkout_creates_a_paid_order_and_takes_the_stock(self):
        self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        self.client.post(reverse('catalog:cart_update', args=[self.product.pk]), {'quantity': 2})
        self.client.post(reverse('catalog:checkout'), self.address)

        order = Order.objects.get()
        self.product.refresh_from_db()
        self.assertEqual(order.status, Order.PAID)
        self.assertEqual(order.total, Decimal('179.98'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(self.product.stock, 3)
        self.assertTrue(order.reference_number.startswith('AFO-'))

    def test_checkout_refuses_when_the_stock_dropped_since_the_cart_was_filled(self):
        # The cart page can sit open for a long time, so the stock is checked
        # again at checkout rather than trusting what was there earlier.
        self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        self.client.post(reverse('catalog:cart_update', args=[self.product.pk]), {'quantity': 4})
        self.product.stock = 1
        self.product.save()

        response = self.client.post(reverse('catalog:checkout'), self.address, follow=True)
        self.product.refresh_from_db()
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(self.product.stock, 1)
        self.assertContains(response, 'only has 1 left')

    def test_an_order_keeps_the_price_that_was_paid(self):
        # A later price change must not rewrite what an old order cost.
        self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        self.client.post(reverse('catalog:checkout'), self.address)
        self.product.price = Decimal('999.00')
        self.product.save()

        self.assertEqual(Order.objects.get().items.get().unit_price, Decimal('89.99'))

    def test_a_shopper_cannot_open_someone_elses_order(self):
        self.client.post(reverse('catalog:cart_add', args=[self.product.pk]))
        self.client.post(reverse('catalog:checkout'), self.address)
        order = Order.objects.get()

        other = User.objects.create_user(username='nosy', password='pw-for-tests')
        self.client.force_login(other)
        response = self.client.get(reverse('catalog:order_confirmation', args=[order.pk]))
        self.assertEqual(response.status_code, 404)


@override_settings(STRIPE_WEBHOOK_SECRET='whsec_test_secret_for_the_tests')
class StripeWebhookTests(ShopTestCase):
    # Stripe signs each webhook with the endpoint's secret. These build the same
    # signature Stripe would, so the view can be tested without the network.
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            user=self.user, ship_full_name='Test', ship_address='Street 1',
            ship_city='Athens', ship_postcode='14234', ship_country='Greece',
            total=Decimal('89.99'), stripe_session_id='cs_test_123',
        )
        self.order.items.create(product=self.product, quantity=2, unit_price=self.product.price)

    def post_event(self, payload, signature=None):
        import hashlib
        import hmac
        import json
        import time

        body = json.dumps(payload)
        if signature is None:
            timestamp = int(time.time())
            secret = 'whsec_test_secret_for_the_tests'
            signed = f'{timestamp}.{body}'.encode()
            digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
            signature = f't={timestamp},v1={digest}'
        return self.client.post(
            reverse('catalog:stripe_webhook'), data=body,
            content_type='application/json', HTTP_STRIPE_SIGNATURE=signature,
        )

    def completed_event(self, session_id='cs_test_123', payment_status='paid'):
        # The same shape Stripe posts, object: event and all, because its
        # library reads that field before anything else.
        return {
            'id': 'evt_test', 'object': 'event',
            'type': 'checkout.session.completed',
            'data': {'object': {'id': session_id, 'object': 'checkout.session',
                                'payment_status': payment_status}},
        }

    def test_a_signed_event_settles_the_order_and_takes_the_stock(self):
        response = self.post_event(self.completed_event())
        self.order.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order.status, Order.PAID)
        self.assertEqual(self.product.stock, 3)

    def test_an_unsigned_caller_cannot_mark_an_order_paid(self):
        # This is the whole reason the signature is checked. Without it anyone
        # who found the url could post this and be sent free gear.
        response = self.post_event(self.completed_event(), signature='t=1,v1=made-up')
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.order.status, Order.PENDING)

    def test_a_missing_signature_is_refused(self):
        response = self.client.post(
            reverse('catalog:stripe_webhook'), data='{}', content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_the_same_event_twice_only_takes_the_stock_once(self):
        # Stripe retries until it gets a 200, and the success page may have got
        # there first, so this has to be safe to repeat.
        self.post_event(self.completed_event())
        self.post_event(self.completed_event())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_an_unpaid_session_settles_nothing(self):
        response = self.post_event(self.completed_event(payment_status='unpaid'))
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order.status, Order.PENDING)

    def test_an_event_for_an_unknown_session_is_shrugged_off(self):
        response = self.post_event(self.completed_event(session_id='cs_not_ours'))
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order.status, Order.PENDING)

    def test_an_event_we_do_not_act_on_still_gets_a_200(self):
        # Anything other than a 200 makes Stripe retry it forever.
        response = self.post_event({
            'id': 'evt_x', 'object': 'event', 'type': 'payment_intent.created',
            'data': {'object': {'id': 'pi_x', 'object': 'payment_intent'}},
        })
        self.assertEqual(response.status_code, 200)

    @override_settings(STRIPE_WEBHOOK_SECRET='')
    def test_with_no_secret_configured_nothing_is_accepted(self):
        response = self.post_event(self.completed_event())
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.order.status, Order.PENDING)


class RatingTests(ShopTestCase):
    def test_the_database_refuses_a_rating_outside_one_to_five(self):
        for bad in (0, 6, 99):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Rating.objects.create(user=self.user, product=self.product, stars=bad)

    def test_rating_again_replaces_the_old_one(self):
        self.client.force_login(self.user)
        url = reverse('catalog:rate', args=[self.product.pk])
        self.client.post(url, {'stars': 2, 'comment': 'first go'})
        response = self.client.post(url, {'stars': 5, 'comment': 'changed my mind'})

        self.assertEqual(Rating.objects.filter(user=self.user, product=self.product).count(), 1)
        self.assertEqual(response.json()['average'], 5)

    def test_a_guest_cannot_rate(self):
        response = self.client.post(reverse('catalog:rate', args=[self.product.pk]), {'stars': 5})
        self.assertEqual(response.status_code, 302)


class SearchAndFilterTests(ShopTestCase):
    def test_search_matches_the_name_or_the_brand(self):
        self.make_product('Fleece Jacket')
        response = self.client.get(reverse('catalog:product_list'), {'q': 'fleece'})
        self.assertEqual([p.name for p in response.context['products']], ['Fleece Jacket'])

        response = self.client.get(reverse('catalog:product_list'), {'q': 'condor'})
        self.assertEqual([p.name for p in response.context['products']], ['Rain Shell'])

    def test_a_bad_filter_value_says_so_instead_of_listing_everything(self):
        response = self.client.get(reverse('catalog:product_list'), {'min_price': 'abc'})
        self.assertTrue(response.context['form'].errors)
        self.assertContains(response, 'Enter a number')

    def test_paging_keeps_the_search(self):
        for i in range(12):
            self.make_product(f'Jacket {i:02d}')
        response = self.client.get(reverse('catalog:product_list'), {'q': 'Jacket', 'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'q=Jacket')

    def test_a_nonsense_page_number_does_not_break_the_listing(self):
        for value in ('abc', '999', '-1'):
            self.assertEqual(
                self.client.get(reverse('catalog:product_list'), {'page': value}).status_code, 200
            )


class RecommenderTests(ShopTestCase):
    def test_it_suggests_from_the_same_subcategory_and_skips_what_was_seen(self):
        seen = self.make_product('Seen Jacket')
        fresh = self.make_product('Fresh Jacket')
        RecentlyViewed.objects.create(user=self.user, product=seen)

        suggestions = recommendations_for_user(self.user)
        self.assertIn(fresh, suggestions)
        self.assertNotIn(seen, suggestions)

    def test_someone_with_no_history_still_gets_something(self):
        # The block on the dashboard should never be empty.
        self.assertTrue(recommendations_for_user(self.user))

    def test_out_of_stock_items_are_never_suggested(self):
        Product.objects.update(stock=0)
        gone = self.make_product('Sold Out', stock=0)
        self.assertNotIn(gone, recommendations_for_user(self.user))
