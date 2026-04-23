import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libya_tradenet.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command

if not User.objects.exists():
    print("Loading initial fixture data...")
    call_command('loaddata', 'fixtures/initial_data.json')
    print("Initial data loaded successfully.")
else:
    print(f"Database already has {User.objects.count()} users — skipping loaddata.")
