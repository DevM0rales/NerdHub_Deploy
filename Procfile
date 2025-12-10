release: python manage.py migrate --noinput && python manage.py loaddata seed.json || true
web: gunicorn Nerdhub.wsgi --log-file -
