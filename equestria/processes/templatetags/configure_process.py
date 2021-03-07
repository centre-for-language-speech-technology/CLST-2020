from django import template

register = template.Library()


@register.inclusion_tag("processes/configure-process.html", takes_context=False)
def render_profile_form(script, project, refresh_on_file_change=False):
    """Render configure process screen."""
    return {
        "script": script,
        "project": project,
        "refresh_on_file_change": refresh_on_file_change,
        "script_type": "FA" if script == project.pipeline.fa_script else "G2P",
    }
