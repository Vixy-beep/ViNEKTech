web: gunicorn config.wsgi --log-file - --workers 2 --threads 2 --timeout 120
release: python manage.py migrate
