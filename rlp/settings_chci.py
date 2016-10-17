from .settings_base import *

SITE_PREFIX = 'chci'

ALLOWED_HOSTS = [
    '.chcimedicalhumanities.org',
]

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

TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'rlp', 'templates', SITE_PREFIX),
    os.path.join(BASE_DIR, 'rlp', 'templates'),
]

DATABASES['default']['NAME'] = SITE_PREFIX

CACHES['default']['KEY_PREFIX'] = SITE_PREFIX

HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = SITE_PREFIX

ACCOUNT_ACTIVATION_DAYS = 14
