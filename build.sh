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
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.exists():
    from django.core.management import call_command
    call_command('loaddata', 'fixtures/initial_data.json')
    print('Initial data loaded.')
else:
    print('Database already has data — skipping loaddata.')
"

echo "Build completed successfully!"
