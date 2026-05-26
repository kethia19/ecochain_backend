release: python manage.py migrate --noinput
web: gunicorn eco_chain.wsgi:application --bind 0.0.0.0:$PORT