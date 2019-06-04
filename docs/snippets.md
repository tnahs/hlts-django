``` shell
# Heroku commands

heroku run python manage.py makemigrations --app hlts-django
heroku run python manage.py migrate --app hlts-django
heroku run python manage.py createsuperuser --app hlts-django

# Django dumpdata

python manage.py dumpdata \
    --indent 4 \
    --exclude auth.permission \
    --exclude contenttypes \
    --settings=hlts.settings.dev \
    > db.json

python manage.py loaddata db.json

```