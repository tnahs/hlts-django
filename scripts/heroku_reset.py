#!/usr/bin/env python

import os
import sys


def main():

    confirm = input("Confirm to hard reset application? [y/N]: ")

    if confirm.lower().strip() != "y":
        print("Confirmation cancelled.")
        sys.exit(-1)

    os.system("pg:reset DATABASE_URL --confirm hlts-django --app hlts-django")

    os.system("python manage.py migrate \
            --settings=hlts.settings.prod \
            --app hlts-django")

    os.system("python manage.py loaddata \
            fixtures/init_defaults.json \
            --settings=hlts.settings.prod \
            --app hlts-django")

    os.system("python manage.py loaddata \
            fixtures/prod_defaults.json \
            --settings=hlts.settings.prod \
            --app hlts-django")


if __name__ == "__main__":
    main()
