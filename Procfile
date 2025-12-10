release: python manage.py migrate --noinput && python manage.py loaddata seed.json || true && python manage.py collectstatic --noinput
web: gunicorn Nerdhub.wsgi --log-file 