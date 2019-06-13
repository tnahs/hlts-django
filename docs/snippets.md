``` shell
# Heroku commands

heroku run <command> --settings=config.settings.production


# Django dumpdata

python manage.py dumpdata \
    --exclude admin \
    --exclude auth \
    --exclude users \
    --exclude sessions \
    --exclude contenttypes \
    --settings=config.settings.development \
    --indent 4 \
    > tmp/db.json

python manage.py dumpdata \
    users \
    --indent 4 \
    --settings=config.settings.development \
    > tmp/db.json


python manage.py loaddata db.json


# Django

python manage.py shell --settings=config.settings.development

```