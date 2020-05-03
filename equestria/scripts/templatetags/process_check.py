from django import template

register = template.Library()


@register.simple_tag
def check_project(**kwargs):
    project = kwargs.get("project")
    if project.can_start_new_process():
        if project.has_empty_extension_file([".oov"]):
            return "Finished"
    elif project.current_process is not None:
        if project.current_process_script == project.pipeline.fa_script:
            return "FA"
        elif project.current_process_script == project.pipeline.g2p_script:
            return "G2P"
    return "None"
