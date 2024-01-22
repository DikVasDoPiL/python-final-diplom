from django.urls import path

from .views import ShopsView, CategoriesView, ProductInfoView, ShopState, ShopUpdate, PartnerUpdate, PartnerOrders

app_name = 'shops'

viewSets = {
    'get': 'retrieve',
    # 'post': 'create',
    # 'put': 'update',
    # 'delete': 'destroy'
}

urlpatterns = [
    path('shops', ShopsView.as_view(), name='shops'),
    path('categories', CategoriesView.as_view(), name='categories'),
    path('products', ProductInfoView.as_view({'get': 'list'}), name='products'),
    path('shop/state', ShopState.as_view(), name='shop-state'),
    path('shop/update', ShopUpdate.as_view(), name='shop-update'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
]