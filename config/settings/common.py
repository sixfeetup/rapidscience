"""
Django settings for rlp project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

gettext = lambda s: s

import environ

# (rapidscience/config/settings/common.py - 3 = rapidscience/)
ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('rlp')

env = environ.Env()
env.read_env()

SITE_PREFIX = env('SITE_PREFIX')

USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'SAMEORIGIN'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
)

SITE_ID = 1

AUTH_USER_MODEL = 'accounts.User'

DEBUG = False

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = (
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'formtools',
    'localflavor',
    'rlp.accounts.apps.AccountsConfig',
    'actstream.apps.ActstreamConfig',
    'bootstrap3',
    'cms',
    'filer',
    'cmsplugin_filer_file',
    'cmsplugin_filer_folder',
    'cmsplugin_filer_image',
    'djangocms_blog',
    'djangocms_column',
    'django_fsm',
    'djangocms_link',
    'djangocms_text_ckeditor',
    'django_comments',
    'el_pagination',
    'embed_video',
    'polymorphic',
    'treebeard',
    'mptt',
    'menus',
    'sekizai',
    'reversion',
    'aldryn_apphooks_config',
    'aldryn_search',
    'easy_thumbnails',
    'compressor',
    'haystack',
    'meta',
    'parler',
    'taggit',
    'taggit_autosuggest',
    'rlp.bibliography.apps.BibliographyConfig',
    'rlp.bookmarks.apps.BookmarksConfig',
    'rlp.core.apps.CoreConfig',
    'rlp.discussions',
    'rlp.documents.apps.DocumentsConfig',
    'rlp.events.apps.EventsConfig',
    'rlp.newsfeed.apps.NewsFeedConfig',
    'rlp.projects.apps.ProjectsConfig',
    'rlp.search.apps.SearchConfig',
    'casereport',
    'captcha',
    'django_countries',
    'ajax_select',
    'inplaceeditform_bootstrap',
    'inplaceeditform',
    'inplaceeditform_extra_fields',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates', SITE_PREFIX)),
            str(APPS_DIR.path('templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'django.template.context_processors.csrf',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'rlp.core.context_processors.google_analytics',
                'rlp.core.context_processors.search_form',
            ],
        },
    },
]

LANGUAGES = (
    ('en-us', gettext('English')),
)

CMS_TEMPLATES = (
    ('home.html', 'Home Page'),
    ('cms/left_col.html', 'Content with left column'),
    ('cms/right_col.html', 'Content with right column'),
    ('projects/projects_list.html', 'Project Page'),
    ('newsfeed/newsfeed.html', 'News & Events'),
    ('cms/single_col.html', 'Full width content with no side columns'),
)

CMS_PLACEHOLDER_CONF = {
    'hero-text': {
        'plugins': ['TextPlugin'],
        'limits': {
            'TextPlugin': 1
        }
    },
    'hero-image': {
        'plugins': ['FilerImagePlugin'],
        'limits': {
            'FilerImagePlugin': 1
        }
    },
    'homepage-intro': {
        'plugins': ['TextPlugin'],
        'limits': {
            'TextPlugin': 1
        },
        'text_only_plugins': [
            'LinkPlugin',
            'FilerImagePlugin',
            'FilerFilePlugin',
        ]
    },
    'content': {
        'plugins': [
            'TextPlugin',
            'MultiColumnPlugin',
            'ProjectsPlugin'
        ],
        'text_only_plugins': [
            'LinkPlugin',
            'FilerImagePlugin',
            'FilerFilePlugin',
        ]
    },
    'bibliography': {
        'plugins': [
            'TextPlugin'
        ],
        'limits': {
            'TextPlugin': 1
        },
        'text_only_plugins': [
            'LinkPlugin',
            'FilerImagePlugin',
            'FilerFilePlugin',
        ]
    },
}

CMS_INTERNAL_IPS = []

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': env.db()
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True

# FIXTURE CONFIGURATION
# -----------------------------------------------------------------------------
# See:
#  https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(ROOT_DIR.path('fixtures')),
)

# Override these per site
REGISTRATION_REVIEWERS = []
REGISTRATION_REVIEWERS_FOR_APPROVAL_REQUIRED_PROJECTS = []

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

# STATIC_URL = 'http://static.TBD.org/'
STATIC_URL = '/static/'

STATIC_ROOT = str(ROOT_DIR('static'))

# MEDIA_URL = 'http://media.TBD.org/'
MEDIA_URL = '/media/'

MEDIA_ROOT = str(ROOT_DIR('media'))

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_OFFLINE=True
COMPRESS_CSS_HASHING_METHOD = 'content'
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_HIGH_RESOLUTION = True

GOOGLE_UA = ""

ORCID_CLIENT_ID = ''
ORCID_SECRET_KEY = ''

ZOTERO_URL = "in settings.py"

CACHES = {
    "default": env.cache()
}

CACHES['default']['KEY_PREFIX'] = SITE_PREFIX

ACTSTREAM_SETTINGS = {
    'MANAGER': 'actstream.managers.ActionManager',
    'FETCH_RELATIONS': False,
    'USE_JSONFIELD': False,
}

BOOTSTRAP3 ={
    'success_css_class': '',
    'set_placeholder': False,
    'required_css_class': 'required',
}

COMMENTS_APP = 'rlp.discussions'
COMMENTS_MAX_THREAD_LEVEL = 2
COMMENTS_MAX_THREAD_LEVEL_BY_APP_MODEL = {}
COMMENT_MAX_LENGTH = 2000


EL_PAGINATION_TEMPLATE_VARNAME = 'template_name'

EMBED_VIDEO_BACKENDS = [
    'embed_video.backends.YoutubeBackend',
    'embed_video.backends.VimeoBackend',
]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/collection1',
        'INCLUDE_SPELLING': True,
    },
}

# Use a custom Haystack signal processor since the casereports doesn't play
# nice with the realtime one.
HAYSTACK_SIGNAL_PROCESSOR = 'rlp.search.signals.RLPSignalProcessor'

INDEXABLE_EXTENSIONS = (
    'doc',
    'docx',
    'pdf',
    'ppt',
    'pptx',
    'rtf',
    'txt',
    'xls',
    'xlsx',
)

META_SITE_PROTOCOL = 'https'
META_USE_SITES = True

PUBMED_EMAIL = ''

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': ROOT_DIR.path('log').file('rlp.log').name,
        }
    },
    'loggers': {
        '': {
            'handlers': ['mail_admins', 'file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['file'],
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['file'],
        }
    },
}

ACCOUNT_ACTIVATION_DAYS = 14

GROUP_INVITATION_TEMPLATE = '''{user} has approved your request to join the “{group}” group:

{link}

You may post discussions, files, case reports, and references to this group, and participate in member discussions. If you wish to invite others to join the group, please contact the moderator(s).

If you have questions, please contact us at ​info@rapidscience.org.

Best wishes,

The Rapid Science Team
'''


# CRDB support
HAVOC_USER = env('HAVOC_USER')
HAVOC_TOKEN = env('HAVOC_TOKEN')
HAVOC_BASE_URL = env('HAVOC_BASE_URL')
VOCABS = env('VOCABS')

CRDB_DOMAIN = '127.0.0.1:8000'
APPROVED_MESSAGE = (
    'Your approved case report has been submitted.'
    ' You will be notified shortly when it is posted'
    ' to the Cases Central database.'
)
EDITED_MESSAGE = (
    'Your edits to the case report have been submitted. '
    ' We will email you as soon as we review your changes'
    ' for final approval and posting to Cases Central.'
)
CASE_SUBMIT = 'Your case report submission'
NEW_CASE = "New Case Report"
CASE_READY_SUBJECT = "A new case awaits your approval"
CASE_APPROVED_SUBJECT = "Case Approved"
DATA_SCIENCE_TEAM = ['nadeemaslam@trialx.com', 'priya@trialx.com']
BCC_LIST = ['nadeemaslam@trialx.com', 'sg@rapidscience.org']
EDITED = "Case Report Edited"

TOKEN_SALT = env('TOKEN_SALT')
CRDB_SERVER_EMAIL = env('CRDB_SERVER_EMAIL')
CRDB_BCC_LIST = env.list('CRDB_BCC_LIST')

# map content types to display names
TYPE_DISPLAY_NAMES = {
    ('discussions', 'threadedcomment'): 'Discussions',
    ('documents', 'document'): 'Docs/Media',
    ('bibliography', 'projectreference'): 'Bibliography',
    ('casereport', 'casereport'): 'Case Reports',
}
