from django.contrib import admin
from django.urls import path, include
from azbankgateways.urls import az_bank_gateways_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    # https://github.com/pennersr/django-allauth/blob/main/allauth/account/urls.py
    path('accounts/', include('allauth.urls')),
    path('',include('core.urls', namespace='core')),
    path('bankgateways/', az_bank_gateways_urls()),
]
