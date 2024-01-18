from django.urls import path
from backend.views import PartnerUpdate, ShopsApiView, LoginUser, RegisterUser

from rest_framework.routers import DefaultRouter


r = DefaultRouter()


app_name = 'backend'
urlpatterns = r.urls
urlpatterns += [
    path('user/login/', LoginUser.as_view(), name='user-login'),
    path('user/register/', RegisterUser.as_view(), name='user-register'),
    path('shops/', ShopsApiView.as_view(), name='shops'),
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
]

