from django.apps import AppConfig


class HxRequestsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hx_requests"

    def ready(self):
        # Register system checks (e.g. auth-mixin ordering on HtmxViewMixin views).
        from hx_requests import checks  # noqa: F401
