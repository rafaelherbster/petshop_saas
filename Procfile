# Executa migrações automaticamente ao iniciar
release: python manage.py migrate --noinput

# Inicia o servidor
web: gunicorn config.wsgi --log-file - --bind 0.0.0.0:$PORT --env DJANGO_SETTINGS_MODULE=config.settings.prod