#!/usr/bin/env python

import os
import sys
import pathlib


def main():

    root_dir = pathlib.Path(__file__).absolute().parent
    migrations_dir = root_dir / "main" / "migrations"
    db_file = root_dir / "db.sqlite3"

    confirm = input("Confirm to hard reset application? [y/N]: ")

    if confirm.lower().strip() != "y":
        print("Confirmation cancelled.")
        sys.exit(-1)

    for item in migrations_dir.iterdir():

        if item.name == "__init__.py":
            continue

        try:
            item.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            raise

    try:
        db_file.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        raise

    os.system("python manage.py makemigrations --settings=hlts.settings.dev")
    os.system("python manage.py migrate --settings=hlts.settings.dev")
    os.system("python manage.py loaddata fixtures/app_defaults.json --settings=hlts.settings.dev")
    os.system("python manage.py loaddata fixtures/dev_defaults.json --settings=hlts.settings.dev")
    os.system("python manage.py runserver --settings=hlts.settings.dev")

    print("App reset!")


if __name__ == "__main__":
    main()
