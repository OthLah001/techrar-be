release: python manage.py migrate && python manage.py collectstatic --clear --noinput
web: gunicorn config.wsgi --log-file -
worker: celery -A config worker --loglevel=info