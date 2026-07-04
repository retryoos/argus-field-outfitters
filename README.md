# Argus Field Outfitters

Argus Field Outfitters is an online store for tactical and outdoor gear. This is my final project for ITC 4214 Internet Programming. The site is built with Django and Bootstrap.

## What it does

Visitors can browse a catalogue of gear by category and sub category, search and filter, and view item details. Registered users can rate items, keep a wishlist, add items to a cart, and run a simulated checkout. Staff manage the catalogue from the Django admin.

## Running it locally

    python3.12 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Then open the local address that the server prints, usually http://127.0.0.1:8000.

## Project layout

argus is the project package with the settings and the root urls. catalog is the store app. Shared templates live in the templates folder. Shared static files live in the static folder. Uploaded images live in the media folder.
