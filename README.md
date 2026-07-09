# Argus Field Outfitters

Argus Field Outfitters is an online store for tactical and outdoor gear. It is my final
project for ITC 4214 Internet Programming. The site is built with Django and Bootstrap.

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

Python, Django, SQLite, Bootstrap 5, jQuery, django-crispy-forms, Stripe in test mode,
WhiteNoise for static files, and gunicorn for serving.

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

Put your Stripe test keys in the .env file so checkout works. The .env file is ignored by
git and is never committed.

## Deployment

See DEPLOY.md for the steps to deploy on PythonAnywhere or Render.

## Project layout

argus holds the settings and the root urls. catalog, accounts, and backoffice are the
apps. Shared templates and the error pages live in the templates folder. Shared static
files live in the static folder. Uploaded images live in the media folder. The ERD and the
sitemap are in the docs folder.
