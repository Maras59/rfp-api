from django.apps import AppConfig


class RfpApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rfp_api"

    def ready(self):
        import rfp_api.api.signals  # noqa

        return super().ready()
