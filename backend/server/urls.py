
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('shops.urls', namespace='shop_backend')),
    path('api/v1/', include('users.urls', namespace='user_backend')),
    path('api/v1/', include('orders.urls', namespace='orders_backend')),
    path('api/v1/auth/', include('rest_framework.urls', namespace='rest_framework')),
]
