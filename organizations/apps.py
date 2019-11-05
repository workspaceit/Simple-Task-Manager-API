from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    name = 'organizations'
    verbose_name = 'Organization Module'

    def ready(self):
        import organizations.signals