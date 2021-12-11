from django import template
register = template.Library()

@register.filter
def dictionary_lookup(Dictionary, i):
    return Dictionary.get(i)
