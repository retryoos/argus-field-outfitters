# Argus Field Outfitters

Argus Field Outfitters is an online store for tactical and outdoor gear. It is my final
project for ITC 4214 Internet Programming. The site is built with Django and Bootstrap.

## Links

- Live site: https://retryoos.pythonanywhere.com/
- GitHub: https://github.com/retryoos/argus-field-outfitters
- Demo video: (to be added)

## Demo accounts

Sign in at https://retryoos.pythonanywhere.com/accounts/login/ to try each role. They all
share the same password, `ArgusDemo2026`.

| Role     | Username   | Password      |
|----------|------------|---------------|
| Owner    | owner1     | ArgusDemo2026 |
| Employee | employee1  | ArgusDemo2026 |
| Customer | customer1  | ArgusDemo2026 |

## What it does

- Browse a catalogue of gear by category and sub category.
- Search by name or brand, and filter by price, brand, color, size, and stock.
- Register, sign in, edit a profile, and see a personalised dashboard.
- Rate items and read the community reviews, keep a wishlist, and track recently viewed items.
- Add items to a session cart as a guest, then sign in to check out through Stripe test mode.
- Manage the catalogue, orders, and user roles from custom Owner and Employee panels.

## Roles

- A guest can browse, search and fill a session cart, and is asked to sign in at checkout.
- A customer is the default role on signup. Customers rate and review items, keep a wishlist, check out and see their order history.
- An employee manages the catalogue and views orders from the backoffice.
- An owner does everything an employee does and also manages users and their roles.
- Root is the Django superuser and the only account that uses the built in Django admin.

## Technology

Python, Django, SQLite, Bootstrap 5, jQuery, django-crispy-forms, and Stripe in test mode.

## Apps

- catalog holds the products and categories, the session cart, checkout, orders, ratings, the wishlist and the recommender.
- accounts holds registration, login, logout, roles, the profile and the customer dashboard.
- backoffice holds the custom Owner and Employee panels.

## Running it locally

    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python manage.py migrate
    python manage.py loaddata sample_data
    python manage.py createsuperuser
    python manage.py runserver

Then open the local address that the server prints, usually http://127.0.0.1:8000.

Fill in the .env file before running. It holds the secret key, DEBUG, and the Stripe test
keys, and it is ignored by git so it is never committed. Left without Stripe keys the
checkout skips the payment page and completes right away, which is handy while developing.

## Tests

    python manage.py test

They cover the cart and its stock rules, checkout, ratings, search and filters, the
recommender, registration, and every role check.

## Deployment

Live at https://retryoos.pythonanywhere.com/, deployed on PythonAnywhere. See DEPLOY.md
for the steps.

## Project layout

argus holds the settings, the root urls and the paging helpers both apps share. catalog,
accounts, and backoffice are the apps, and anything belonging to one of them lives inside
it, so catalog's own javascript sits in catalog/static/catalog. Only genuinely site wide
files sit at the top level, the base template and the error pages in templates, and the
site stylesheet in static. Uploaded images live in the media folder, and the ERD and the
sitemap are in the docs folder.
