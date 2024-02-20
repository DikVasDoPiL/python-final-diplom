from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm
# from rest_framework.urlpatterns import format_suffix_patterns

from .views import RegisterAccount, EmailConfirm, AccountLogin, AccountDetails, AccountContact

app_name = 'users'
urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='register-account'),
    path('user/confirm/<str:uidb64>/<str:token>/', EmailConfirm.as_view(), name='email-confirm'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('user/confirm', EmailConfirm.as_view(), name='email-api-confirm'),
    path('user/login', AccountLogin.as_view(), name='user-login'),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    path('user/contact', AccountContact.as_view(), name='user-contact'),
]
# urlpatterns = format_suffix_patterns(urlpatterns)