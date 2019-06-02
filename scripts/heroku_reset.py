#!/usr/bin/env python

import os


os.system("heroku run \
          python manage.py migrate \
          --settings=hlts.settings.prod \
          --app hlts-django")

os.system("heroku run \
          python manage.py loaddata \
          fixtures/init_defaults.json \
          --settings=hlts.settings.prod \
          --app hlts-django")

os.system("heroku run \
          python manage.py loaddata \
          fixtures/prod_defaults.json \
          --settings=hlts.settings.prod \
          --app hlts-django")

os.system("heroku run \
          python manage.py runserver \
          --settings=hlts.settings.prod \
          --app hlts-django")