from .settings_base import *

SITE_PREFIX = 'sobc'

TEMPLATES[0]['DIRS'] = [
    os.path.join(BASE_DIR, 'rlp', 'templates', SITE_PREFIX),
    os.path.join(BASE_DIR, 'rlp', 'templates'),
]

DATABASES['default']['NAME'] = SITE_PREFIX

CACHES['default']['KEY_PREFIX'] = SITE_PREFIX

HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = SITE_PREFIX

ACCOUNT_ACTIVATION_DAYS = 14
