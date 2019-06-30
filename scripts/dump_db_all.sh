#! /usr/local/bin/bash

python manage.py dumpdata \
    --exclude admin \
    --exclude auth \
    --exclude sessions \
    --exclude contenttypes \
    --settings=config.settings.development \
    --indent 4 \
    > tmp/dev_data.json