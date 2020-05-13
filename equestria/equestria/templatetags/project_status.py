from django import template

register = template.Library()


@register.simple_tag
def project_status(**kwargs):
    """
    Check the status of a current project.

    :param kwargs: keyword arguments
    :return: a string, FA if the project is currently running an FA script, G2P if the project is currently running a
    G2P script, Finished if the project is currently finished running FA and None if the project has not started FA yet
    """
    project = kwargs.get("project", None)
    if project is not None:
        return project.get_next_step()
    return -1
