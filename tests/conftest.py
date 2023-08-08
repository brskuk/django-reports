"""Test fixtures and utilities."""
import os
import sys
from contextlib import contextmanager

import django
from django.core import management


def pytest_configure(config):
    from django.conf import settings

    # USE_L10N is deprecated, and will be removed in Django 5.0.
    use_l10n = {"USE_L10N": True} if django.VERSION < (4, 0) else {}
    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
            "secondary": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        SITE_ID=1,
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        STATIC_URL="/static/",
        ROOT_URLCONF="tests.urls",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "debug": True,  # We want template errors to raise
                },
            },
        ],
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ),
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "django_reports",
        ),
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
        **use_l10n,
    )

    if config.getoption("--no-pkgroot", False):
        sys.path.pop(0)

        # import django_reports before pytest re-adds the package root directory.
        import django_reports

        package_dir = os.path.join(os.getcwd(), "django_reports")
        assert not django_reports.__file__.startswith(package_dir)

    # Manifest storage will raise an exception if static files are not present (ie, a packaging failure).
    if config.getoption("--staticfiles", False):
        import django_reports

        settings.STATIC_ROOT = os.path.join(
            os.path.dirname(django_reports.__file__), "static-root"
        )
        settings.STATICFILES_STORAGE = (
            "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        )

    django.setup()

    if config.getoption("--staticfiles", False):
        management.call_command("collectstatic", verbosity=0, interactive=False)


@contextmanager
def does_not_raise():
    """No-op context manager to compliment pytest.raises.

    Yields:
        None
    """
    yield
