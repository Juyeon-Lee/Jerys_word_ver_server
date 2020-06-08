from django import template
import datetime

register = template.Library()


@register.filter()
def subDays(days) :
    if isinstance(days, str) :
        days = int(days)
    newDate = datetime.date.today() - datetime.timedelta(days=days)
    return newDate
