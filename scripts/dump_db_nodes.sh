#! /usr/local/bin/bash

python manage.py dumpdata \
    nodes \
    --indent 4 \
    --settings=config.settings.development \
    > tmp/dev_nodes.json