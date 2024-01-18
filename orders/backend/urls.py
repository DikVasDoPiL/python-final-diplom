from django.urls import path
from backend.views import PartnerUpdate, ShopsApiView

from rest_framework.routers import DefaultRouter


r = DefaultRouter()


app_name = 'backend'
urlpatterns = r.urls
urlpatterns += [
    path('shops', ShopsApiView.as_view(), name='shops'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
]

