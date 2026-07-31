"""
Development settings — extends base.py.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Show all SQL queries in development (set to False if too noisy)
# SHOW_SQL = True

# Django Debug Toolbar (optional — uncomment when needed)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
# INTERNAL_IPS = ["127.0.0.1"]
