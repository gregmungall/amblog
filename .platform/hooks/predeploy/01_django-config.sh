#!/bin/bash

source /var/app/venv/*/bin/activate
cd /var/app/staging

if [[ "$EB_IS_COMMAND_LEADER" == "true" ]]; then
    python manage.py migrate --noinput
fi

python manage.py collectstatic --noinput
