release: python manage.py migrate --noinput && python manage.py loaddata nucleo/fixtures/seed.json
web: gunicorn Nerdhub.wsgi --log-file -