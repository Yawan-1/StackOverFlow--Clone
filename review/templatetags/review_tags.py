from django import template

register = template.Library()

@register.filter
def sortIt(queryset, order):
    return queryset.order_by(order)[:5]


# @register.filter
# def filterIt(queryset, by):
#     return queryset.filter(by)