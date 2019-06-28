#! /usr/local/bin/bash

python manage.py dumpdata \
    users \
    --indent 4 \
    --settings=config.settings.development \
    > tmp/dev_users.json