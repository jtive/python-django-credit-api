"""
Test settings for local testing with in-memory SQLite
No external database required!
"""
from .settings import *

# Override database settings for testing - uses in-memory SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory database - no file needed!
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Disable migrations for faster testing
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
SECRET_KEY = 'test-secret-key-for-local-testing'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Disable SSL for testing
DB_SSLMODE = 'disable'

# Speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}
