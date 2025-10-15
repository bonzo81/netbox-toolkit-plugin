from django import template

from ..forms import VARIABLE_FIELD_PREFIX

register = template.Library()


@register.filter
def startswith(value, prefix):
    """
    Template filter to check if a string starts with a given prefix.
    Usage: {% if field.name|startswith:'var_' %}
    """
    if value:
        return str(value).startswith(str(prefix))
    return False


@register.filter
def is_variable_field(field):
    """
    Template filter to check if a form field is a variable field.
    Usage: {% if field|is_variable_field %}
    """
    return hasattr(field, "name") and str(field.name).startswith(VARIABLE_FIELD_PREFIX)
