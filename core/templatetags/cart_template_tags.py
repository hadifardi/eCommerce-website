from django import template
from core.models import Order

register = template.Library()

def get_order_items_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(
            user=user,
            ordered=False,
        )
        if qs.exists():
            order = qs.first()
            return order.items.count()
        else:
            return 0
    else:
        return 0
    
register.filter('get_order_items_count', get_order_items_count)