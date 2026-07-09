#!/usr/bin/env bash
# Build steps for deploying Argus Field Outfitters on a host such as Render.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
