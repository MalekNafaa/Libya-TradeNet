import django
import os
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libya_tradenet.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models.signals import post_save
from trade_management import signals as app_signals

if not User.objects.exists():
    print("Loading initial fixture data...")

    utf8_fixture = 'fixtures/initial_data_utf8.json'
    if not os.path.exists(utf8_fixture):
        print("Converting fixture encoding...")
        with open('fixtures/initial_data.json', 'rb') as f:
            raw = f.read()
        data = json.loads(raw.decode('windows-1252'))
        with open(utf8_fixture, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        print("Encoding fixed.")

    post_save.disconnect(app_signals.create_user_profile, sender=User)
    post_save.disconnect(app_signals.save_user_profile, sender=User)

    call_command('loaddata', utf8_fixture)
    print("Initial data loaded successfully.")
else:
    print(f"Database already has {User.objects.count()} users — skipping loaddata.")
