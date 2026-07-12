# Technical notes

This is a short guide to the parts of Argus Field Outfitters that go past the
plain class material, so it is easy to find them quickly rather than reading
every file. Everything else in the project follows the patterns straight from
the lectures, Django forms, the ORM, template inheritance, the built in
authentication system.

## Role based access beyond login required

`backoffice/permissions.py` defines two decorators, `staff_required` and
`owner_required`. They wrap a view the same way `login_required` does, but
also check the signed in user's role on their profile before letting the
request through, and raise `PermissionDenied` otherwise, which renders the
custom 403 page. This is what actually enforces that an employee cannot open
the user management screen, not just a hidden navbar link.

## Two custom admin panels instead of only the Django admin

The `backoffice` app is a second, purpose built admin interface, one screen
for managing products, categories, and subcategories that both employees and
owners can reach, and a separate screen for managing user roles that only
owners and the superuser can reach. The built in Django admin is still
registered and still works, kept as a fallback for the superuser only.

## Stripe test mode checkout

`catalog/views.py`, the checkout view and the four private helper functions
above it, `_create_order`, `_finalize_order`, `_stripe_enabled`, and
`_start_stripe_session`, build a Stripe Checkout Session and redirect the
shopper to Stripe's own hosted payment page. The card number is entered on
Stripe's page, never on this site, so no card data is ever stored here. If
the Stripe keys are left empty, checkout completes immediately instead, which
keeps local development simple without needing real API keys.

## A cart that works for a guest

The shopping cart is not a database table. `catalog/cart.py` keeps it as a
dictionary in the session, so someone browsing without an account can add
items, and it only becomes a real `Order` once they sign in and check out.

## The recommender

`catalog/recommendations.py` suggests other products from the same
subcategory as whatever the shopper most recently viewed, falling back to the
newest items if they have no browsing history yet. It is one straightforward
query, not a machine learning model, by design.

## AJAX throughout the shopping flow

Rating a product, adding to cart, changing a quantity, removing an item, and
saving or removing a wishlist item all happen without a full page reload.
`static/catalog/ratings.js` and `static/catalog/cart.js` handle this with
jQuery, posting to the same Django views used for the plain form fallback,
and updating the page in place from the JSON response.

## Partial fill star ratings

`catalog/templates/catalog/_stars.html` and the `.star-rating` rules in
`static/css/site.css` draw a row of empty stars with a second, filled row
stacked on top of it, clipped to a percentage width. An average of 3.7 shows
a partly filled fourth star instead of rounding to a whole number.

## Production settings

`argus/settings.py` reads `DEBUG`, `ALLOWED_HOSTS`, and the Stripe keys from
an environment file rather than hardcoding them, and the block at the bottom
of the file only takes effect when `DEBUG` is off, forcing https and marking
cookies secure. The Django secret key itself is the one value left as the
plain string Django generated when the project was created, since it does
not need to differ between a development machine and the live server.
