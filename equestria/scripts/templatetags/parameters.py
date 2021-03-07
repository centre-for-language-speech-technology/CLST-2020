from django import template
from scripts.forms import ParameterForm

register = template.Library()


@register.inclusion_tag("scripts/parameter-form.html", takes_context=False)
def render_parameter_form(parameters):
    """Render parameter form."""
    if len(parameters) > 0:
        return {"show_form": True, "form": ParameterForm(parameters)}
    else:
        return {
            "show_form": False,
        }
