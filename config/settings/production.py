from .common import *
import socket

hostname = socket.gethostname()
if any(pat in hostname for pat in ('tst0', 'stg0')):
    EMAIL_PORT = 1025 # for locally run maildump
else:
    EMAIL_HOST = 'smtp.mailgun.org'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'postmaster@mg.rapidscience.org'
    EMAIL_HOST_PASSWORD = env('MAILGUN_EMAIL_HOST_PASSWORD', default='nope')
    EMAIL_USE_TLS = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

if SITE_PREFIX == 'chci':
    # Old hashers here for backwards compatibility
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.CryptPasswordHasher',
    )
SECRET_KEY = env('DJANGO_SECRET_KEY', default='')
