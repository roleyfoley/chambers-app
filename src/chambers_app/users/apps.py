from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "chambers_app.users"
    verbose_name = "Users"

    def ready(self):
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
