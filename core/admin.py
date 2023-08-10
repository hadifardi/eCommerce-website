from django.contrib import admin
from .models import Item, OrderItem, Order, BillingAddress, Code, Payment, Refund

@admin.action(description='Grant refund reqeust')
def grant_refund_request(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)

class OrderAdmin(admin.ModelAdmin):
    # list_per_page = 2
    actions = [grant_refund_request]
    list_display = [
        'user',
        'order_id',
        'ordered',
        'being_delivered',
        'recived',
        'refund_requested',
        'refund_granted',
        'billing_address',
        'payment'
    ]

    list_display_links = [
        'user',
    ]

    list_filter = [
        'being_delivered',
        'recived',
        'refund_requested'
    ]

    search_fields = [
        'order_id__icontains',
        'user__username__icontains',
    ]

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(BillingAddress)
admin.site.register(Code)
admin.site.register(Refund)
admin.site.register(Payment)
