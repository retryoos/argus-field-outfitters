# Deploying Argus Field Outfitters

The app is deployed on PythonAnywhere, since its free tier keeps the SQLite database
and uploaded product images between reloads, unlike some other free hosts that wipe
the disk on every redeploy.

## Environment variables

Set these in a .env file in the project folder on the server. Never commit real values.

- DEBUG must be False in production.
- ALLOWED_HOSTS lists your domain, for example yourusername.pythonanywhere.com.
- STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY hold your Stripe test mode keys.

The Django secret key is not an environment variable, it is the value already in
argus/settings.py, the same one Django generated when the project was created.

## Steps

1. Push the repository to GitHub, then clone it on PythonAnywhere in a Bash console.

       git clone https://github.com/retryoos/argus-field-outfitters.git
       cd argus-field-outfitters
       python3.12 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt

2. Copy .env.example to .env and fill in DEBUG, ALLOWED_HOSTS, and the Stripe keys.

3. Run the one time data steps.

       python manage.py migrate
       python manage.py collectstatic --no-input
       python manage.py loaddata sample_data
       python manage.py createsuperuser

4. On the Web tab, add a new web app, choose Manual configuration with the matching
   Python version, then set the source code and working directory to the project
   folder, and the virtualenv to its venv folder.

5. Open the WSGI configuration file and replace its contents with:

       import os
       import sys

       path = '/home/yourusername/argus-field-outfitters'
       if path not in sys.path:
           sys.path.insert(0, path)

       os.environ['DJANGO_SETTINGS_MODULE'] = 'argus.settings'

       from django.core.wsgi import get_wsgi_application
       application = get_wsgi_application()

   Settings.py loads the .env file itself, so nothing else needs to go in this file.

6. Add two static file mappings on the Web tab, the static url to the staticfiles
   folder, and the media url to the media folder. Turn on Force HTTPS.

7. Reload the web app.

## After deploying

- Check that the home page loads and the default page is the shop.
- Sign in, add an item to the cart, and run a test checkout with the Stripe test card 4242 4242 4242 4242.
- Confirm that a customer cannot open the backoffice and sees the custom Not allowed page.
- Visit a made up url and confirm the custom Page not found shows, not the default Django error page.
