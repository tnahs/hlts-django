``` shell
# Heroku commands

heroku run <command> --settings=config.settings.production


# Django dumpdata

python manage.py dumpdata \
    --indent 4 \
    --exclude admin \
    --exclude auth \
    --exclude users \
    --exclude sessions \
    --exclude contenttypes \
    --settings=config.settings.development \
    > tmp/db.json

python manage.py loaddata db.json


# Django

python manage.py shell --settings=config.settings.development

```