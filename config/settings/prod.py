from .base import *
import logging

DEBUG = False

ALLOWED_HOSTS = ['petshop-saas.onrender.com']

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# ✅ Conexão com banco mais robusta para Render
# Render pode hibernar bancos free após 5 min de inatividade
DATABASES['default']['CONN_MAX_AGE'] = 30  # Reduzido de 600 para 30 segundos

# ✅ Close connection after each request to avoid stale connections
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
}

# Logging para produção - agora mostra WARNING também para debug
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',  # Mudado de ERROR para WARNING
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',  # Mudado de ERROR para WARNING
            'propagate': False,
        },
        # Adicionar logger do app para ver erros
        'core': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}