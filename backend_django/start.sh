#!/bin/sh
python3 manage.py makemigrations board
python3 manage.py migrate

# TODO Start: [Student] Run with uWSGI instead
python3 manage.py runserver 80
# uwsgi --module=mysite.wsgi:application \
#     --env DJANGO_SETTINGS_MODULE=mysite.settings \
#     --master \
#     --http=0.0.0.0:0 \
#     --processes=5 \
#     --harakiri=20 \
#     --max-requests=5000 \
#     --vacuum
# TODO End: [Student] Run with uWSGI instead
