def pytest_configure():
    import django
    from django.conf import settings
    from django.core.management import call_command

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        SITE_ID=1,
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL="/static/",
        ROOT_URLCONF="tests.urls",
        TEMPLATE_LOADERS=(
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ),
        MIDDLEWARE_CLASSES=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "jwt_devices.middleware.PermittedHeadersMiddleware",
        ),
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "rest_framework",
            "rest_framework_jwt",
            "jwt_devices",
            "tests",
        ),
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
        REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "jwt_devices.authentication.PermanentTokenAuthentication"
            ]
        },
    )

    try:
        import oauth_provider  # NOQA
        import oauth2  # NOQA
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += ("oauth_provider",)

    try:
        if django.VERSION >= (1, 8):
            # django-oauth2-provider does not support Django1.8
            raise ImportError
        import provider  # NOQA
    except ImportError:
        pass
    else:
        settings.INSTALLED_APPS += ("provider", "provider.oauth2")

    try:
        import django

        django.setup()
    except AttributeError:
        pass

    call_command("migrate")
    call_command("makemigrations", "--dry-run", "--check")
