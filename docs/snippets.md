``` shell
# Heroku commands

heroku run <command> --settings=config.settings.production


# Django dumpdata

python manage.py dumpdata \
    --indent 4 \
    --exclude auth.permission \
    --exclude contenttypes \
    --settings=config.settings.development \
    > db.json

python manage.py loaddata db.json


# Django

python manage.py shell --settings=config.settings.development

```