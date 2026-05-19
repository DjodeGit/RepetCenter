# emploidutemps/templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Récupérer une valeur dans un dictionnaire"""
    if dictionary is None:
        return {}
    return dictionary.get(key, {})