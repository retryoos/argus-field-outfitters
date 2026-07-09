# Deploying Argus Field Outfitters

The app reads its configuration from environment variables, serves static files with
WhiteNoise, and runs under gunicorn. It works on PythonAnywhere or on a platform such as
Render. Pick one of the two guides below.

## Environment variables

Set these on the host. Never commit real values.

- SECRET_KEY holds a fresh Django secret key.
- DEBUG must be False in production.
- ALLOWED_HOSTS lists your domain, for example argus.example.com.
- STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY hold your Stripe test mode keys.

## Option A, Render

1. Push the repository to GitHub.
2. Create a new Web Service on Render and connect the repository.
3. Set the build command to bash build.sh and the start command to gunicorn argus.wsgi.
4. Add the environment variables listed above.
5. Deploy. The build runs collectstatic and migrate.
6. Open a shell on the service and run the one time data steps.

       python manage.py loaddata sample_data
       python manage.py createsuperuser

7. Sign in as the superuser and set at least one Employee and one Owner from the backoffice user page.

## Option B, PythonAnywhere

1. Push the repository to GitHub, then clone it on PythonAnywhere.
2. Create a virtual environment and install the requirements.

       python3.12 -m venv venv
       source venv/bin/activate
       pip install -r requirements.txt

3. Create a Web app that points at the argus project, and set the virtual environment path.
4. In the WSGI configuration file, load the environment variables and point at argus.wsgi.
5. Set the environment variables listed above.
6. Run the one time steps.

       python manage.py migrate
       python manage.py collectstatic --no-input
       python manage.py loaddata sample_data
       python manage.py createsuperuser

7. Add a static files mapping for the static url to the staticfiles folder, and one for the media url to the media folder.
8. Reload the web app.

## After deploying

- Check that the home page loads and the default page is the shop.
- Sign in, add an item to the cart, and run a test checkout with the Stripe test card 4242 4242 4242 4242.
- Confirm that a customer cannot open the backoffice and sees the custom Not allowed page.
