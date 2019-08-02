from django import template
register = template.Library()

@register.filter()
def filter_cycle_counter(forloop_counter, currentPage):
    return (currentPage - 1) * 15 + forloop_counter