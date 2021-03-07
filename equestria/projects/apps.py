from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Config class for Django Projects app."""

    name = "projects"

    def ready(self):
        """
        Ready method.

        :return: None
        """
        from projects import signals  # noqa
