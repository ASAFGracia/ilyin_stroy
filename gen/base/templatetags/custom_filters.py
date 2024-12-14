from django import template
from django.forms import BoundField

register = template.Library()

@register.filter
def add_class(field, css):
    if isinstance(field, BoundField):
        existing_classes = field.field.widget.attrs.get("class", "")
        updated_classes = f"{existing_classes} {css}".strip()
        return field.as_widget(attrs={"class": updated_classes})
    return field
