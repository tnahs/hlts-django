#!/usr/bin/env python

import os
import sys


def main():

    confirm = input("Confirm to hard reset heroku application? [y/N]: ")

    if confirm.lower().strip() != "y":
        print("Confirmation cancelled.")
        sys.exit(-1)

    os.system("heroku pg:reset DATABASE_URL --confirm hlts-django --app hlts-django")

    os.system("heroku run \
              python manage.py migrate \
              --settings=hlts.settings.prod \
              --app hlts-django")

    os.system("heroku run \
              python manage.py loaddata \
              fixtures/app_defaults.json \
              --settings=hlts.settings.prod \
              --app hlts-django")

    os.system("heroku run \
              python manage.py loaddata \
              fixtures/dev_defaults.json \
              --settings=hlts.settings.prod \
              --app hlts-django")


if __name__ == "__main__":
    main()
