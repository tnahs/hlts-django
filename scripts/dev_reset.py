#!/usr/bin/env python

import os
import sys
import pathlib


APP_NAME = "hlts"


def main():

    root_dir = pathlib.Path(__file__).parent.parent
    migrations_dir = root_dir / "main" / "migrations"
    db_file = root_dir / "db.sqlite3"
    fixtures_dir = root_dir / "fixtures"

    if not migrations_dir.exists():
        print(f"Migrations folder not found: {migrations_dir}.")
        sys.exit(-1)

    if not fixtures_dir.exists():
        print(f"Fixtures folder not found: {fixtures_dir}.")
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

    os.system(f"python manage.py collectstatic --settings={APP_NAME}.settings.dev --no-input")

    os.system(f"python manage.py makemigrations --settings={APP_NAME}.settings.dev")

    os.system(f"python manage.py migrate --settings={APP_NAME}.settings.dev")

    for item in fixtures_dir.iterdir():
        if item.is_file() and item.suffix == ".json":
            os.system(f"python manage.py loaddata {item} --settings={APP_NAME}.settings.dev")

    os.system(f"python manage.py runserver --settings={APP_NAME}.settings.dev")

    print(f"{APP_NAME} successfully reset!")


if __name__ == "__main__":

    confirm = input(f"Confirm to hard reset {APP_NAME}. [y/N]: ")

    if confirm.lower().strip() != "y":
        print("Hard reset cancelled.")
        sys.exit(-1)

    main()
