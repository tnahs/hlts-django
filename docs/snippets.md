``` shell
# Heroku commands

heroku run <command> --settings=hlts.settings.prod


# Django dumpdata

python manage.py dumpdata \
    --indent 4 \
    --exclude auth.permission \
    --exclude contenttypes \
    --settings=hlts.settings.dev \
    > db.json

python manage.py loaddata db.json


# Django

python manage.py shell --settings=hlts.settings.dev

```