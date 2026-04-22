#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile translations (optional — skipped if gettext not available)
python manage.py compilemessages || echo "compilemessages skipped (gettext not available)"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Load initial data only if the database is empty (first deploy only)
python build_loaddata.py

echo "Build completed successfully!"
