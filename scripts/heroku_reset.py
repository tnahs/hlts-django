#!/usr/bin/env python

import os
import sys
import pathlib


APP_NAME = "hlts"
APP_NAME_HEROKU = "hlts-django"


def main():

    root_dir = pathlib.Path(__file__).parent.parent
    fixtures_dir = root_dir / "fixtures"

    os.system(f"heroku pg:reset DATABASE_URL --confirm {APP_NAME_HEROKU} --app {APP_NAME_HEROKU}")

    os.system(f"heroku run --app {APP_NAME_HEROKU} \
              python manage.py migrate --settings={APP_NAME}.settings.prod ")

    for item in fixtures_dir.iterdir():
        if item.is_file() and item.suffix == ".json":
            os.system(f"heroku run --app {APP_NAME_HEROKU} \
                      python manage.py loaddata {item} --settings={APP_NAME}.settings.prod")


if __name__ == "__main__":

    confirm = input(f"Confirm to hard reset {APP_NAME} on Heroku. [y/N]: ")

    if confirm.lower().strip() != "y":
        print("Hard reset cancelled.")
        sys.exit(-1)

    main()
