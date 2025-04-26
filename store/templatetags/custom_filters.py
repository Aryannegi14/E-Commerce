# store/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return value * arg
    except:
        return value
@register.filter
def avg_rating(reviews):
    if not reviews:
        return 0
    total = sum(review.rating for review in reviews if review.rating)
    count = sum(1 for review in reviews if review.rating)
    return total / count if count > 0 else 0