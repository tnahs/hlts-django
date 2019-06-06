#!/usr/bin/env python

import os
import sys
import pathlib


APP_NAME = "hlts"


def main():

    root_dir = pathlib.Path(__file__).parent.parent
    migration_dirs = [
        root_dir / "apps" / "passages" / "migrations",
        root_dir / "apps" / "users" / "migrations"
    ]
    db_file = root_dir / "tmp" / "db.sqlite3"
    fixtures_dir = root_dir / "fixtures"

    for dir_ in migration_dirs:
        if not dir_.exists():
            print(f"Migrations folder not found: {dir_}.")
            sys.exit(-1)

    if not fixtures_dir.exists():
        print(f"Fixtures folder not found: {fixtures_dir}.")
        sys.exit(-1)

    for dir_ in migration_dirs:
        for item in dir_.iterdir():

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

    os.system(f"python manage.py collectstatic --settings=config.settings.development --no-input")
    os.system(f"python manage.py makemigrations --settings=config.settings.development")
    os.system(f"python manage.py migrate --settings=config.settings.development")

    for item in fixtures_dir.iterdir():
        if item.is_file() and item.suffix == ".json":
            os.system(f"python manage.py loaddata {item} --settings=config.settings.development")

    os.system(f"python manage.py runserver --settings=config.settings.development")

    print(f"{APP_NAME} successfully reset!")


if __name__ == "__main__":

    confirm = input(f"Confirm to hard reset {APP_NAME}. [y/N]: ")

    if confirm.lower().strip() != "y":
        print("Hard reset cancelled.")
        sys.exit(-1)

    main()
