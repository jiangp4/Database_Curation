from django import template

# add a few global custom filter here
register = template.Library()

@register.filter(name='get_class')
def get_class(value): return value.__class__.__name__
