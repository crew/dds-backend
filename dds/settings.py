# Django settings for dds project.

import utils

ROOT = utils.root(__file__)
MODULE = utils.module(__file__)

DEVELOP = True
DEBUG = True or DEVELOP
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Alex Lee', 'lee@ccs.neu.edu'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

if DEVELOP:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = ROOT('temp.sqlite3')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ROOT('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://bigpicture.ccs.neu.edu/media/'

if DEVELOP:
    MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'k+*cv$agm@dh))o03zm38jgvz)6=9_t3qrj@0&6u02ewz)vvn7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = '%s.urls' % MODULE

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT('templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    '%s.slide' % MODULE,
)

AUTHENTICATION_BACKENDS = (
    '%s.ccis.backends.CCISLDAPBackend' % MODULE,
    'django.contrib.auth.backends.ModelBackend',
)

############# Jabber ############
JABBER_CLIENT = utils.JabberClientWrapper('test', 'test', 'dds-server',
                                          'dds-master.ccs.neu.edu')
J_CLIENT_RESOURCE = 'dds-client'

############# LDAP ##############
LDAPBACKEND_HOST = 'ldap://cluster.ldap.ccs.neu.edu/'
LDAPBACKEND_DN   = 'uid=%s,ou=people,dc=ccs,dc=neu,dc=edu'
