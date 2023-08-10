from django.urls import path
from .views import (
    HomePage,
    ProductPage,
    CheckoutPage,
    OrderSummary,
    AddPromo,
    Profile,
    OrderDetail,
    RequestRefund,
    add_to_cart,
    remove_from_cart,
    decrease_item_quantity,
    callback_gateway_view
)
app_name = 'core'

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('product/<slug>/', ProductPage.as_view(), name= 'product'),
    path('checkout/', CheckoutPage.as_view(), name= 'checkout'),
    path('order-summary/', OrderSummary.as_view(), name= 'order-summary'),
    path('add-to-cart/<slug>', add_to_cart, name= 'add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name= 'remove-from-cart'),
    path('decrease-item-quantity/<slug>/', decrease_item_quantity, name= 'decrease-item-quantity'),
    path('callback-gateway/', callback_gateway_view, name='callback-gateway'),
    path('add-promo-code/',AddPromo.as_view(), name='add-promo-code'),
    path('profile/', Profile.as_view(), name='profile'),
    path('order-detail/', OrderDetail.as_view(), name='order-detail'),
    path('request-refund/', RequestRefund.as_view(), name='request-refund')
]