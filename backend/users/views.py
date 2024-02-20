from django.contrib.auth import get_user_model, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator as token_generator
from rest_framework.authtoken.models import Token

from .models import Contact
from server.utils import send_email
from .serializers import AccountSerializer, AccountPublicSerializer, ContactSerializer

User = get_user_model()


class RegisterAccount(APIView):
    def post(self, request):
        required = {'email', 'password'}
        if required.issubset(self.request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                for item in password_error:
                    error_array.append(item)
                return JsonResponse(
                    {'Status': False,
                     'Errors': {'password': error_array}},
                    status=status.HTTP_403_FORBIDDEN)
            else:
                user_serializer = AccountSerializer(data=request.data)

                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(request.data['password'])
                    user.save()
                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    user_email = user.email
                    token = token_generator.make_token(user)
                    domain = get_current_site(request).domain
                    verify_link = '/'.join(['http:/', domain, 'api/v1/user/confirm', uidb64, token])
                    send_email(
                        'Verification e-mail',
                        f'Перейдите по ссылке {verify_link} для подтвержения адреса почты',
                        user_email
                    )
                    return JsonResponse({
                        'Status': True,
                        'token': token,
                        'uid': uidb64},
                        status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({
                        'Status': False,
                        'Errors': user_serializer.errors},
                        status=status.HTTP_403_FORBIDDEN)
        return JsonResponse({
            'Status': False,
            'Errors': f'Arguments {required} are not specified'},
            status=status.HTTP_400_BAD_REQUEST)


class EmailConfirm(APIView):

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def _confirm(self, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return JsonResponse({
                'Status': True,
                'User': user.email,
                'Result': 'Email confirmed'},
                status=status.HTTP_200_OK)

        return JsonResponse({
                'Status': False,
                'Errors': f'Bad request'},
            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, uidb64=None, token=None):
        return self._confirm(uidb64, token)

    def post(self, request, uid=None, token=None):
        try:
            uid = request.data['uid']
            token = request.data['token']
            return self._confirm(uid, token)
        except(KeyError):
            return JsonResponse({
                'Status': False,
                'Errors': f'Bad request'},
                status=status.HTTP_400_BAD_REQUEST)


class AccountLogin(APIView):
    @staticmethod
    def post(request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(
                request,
                username=request.data['email'],
                password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return JsonResponse({
                        'Status': True,
                        'Token': token.key},
                        status=status.HTTP_200_OK)

            return JsonResponse({
                'Status': False,
                'Errors': 'Не удалось авторизовать'},
                status=status.HTTP_401_UNAUTHORIZED)

        return JsonResponse({
            'Status': False,
            'Errors': 'Не указаны все необходимые аргументы'},
            status=status.HTTP_400_BAD_REQUEST)


class AccountDetails(APIView):

    # Просмотр
    @staticmethod
    def get(request: Request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'Status': False,
                'Error': 'Log in required',
                'details': request.data},
                status=status.HTTP_403_FORBIDDEN)

        serializer = AccountPublicSerializer(request.user)
        return Response(serializer.data)

    # Редактирование
    @staticmethod
    def post(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({
                'Status': False,
                'Error': 'Log in required'},
                status=status.HTTP_403_FORBIDDEN)
        # обязательные аргументы

        if 'password' in request.data:
            errors = {}
            # пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                error_array = []
                # noinspection PyTypeChecker
                for item in password_error:
                    error_array.append(item)
                return JsonResponse({
                    'Status': False,
                    'Errors': {'password': error_array}},
                    status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                request.user.set_password(request.data['password'])

        # остальные данные
        user_serializer = AccountSerializer(
            request.user,
            data=request.data,
            partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({
                'Status': 'OK',
                'id': user_serializer.data['id'],
                'email': user_serializer.data['email'],
                'first_name': user_serializer.data['first_name'],
                'last_name': user_serializer.data['last_name'],
                'type': user_serializer.data['type']},
                status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                'Status': False,
                'Errors': user_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)


class AccountContact(APIView):

    @staticmethod
    def get(request):
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        if {'city', 'street', 'phone'}.issubset(request.data):
            request.POST._mutable = True
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({
                    'Status': True,
                    'Details': serializer.data},
                    status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({
                    'Status': False,
                    'Error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'Status': False,
            'Error': 'All necessary arguments are not specified'},
            status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def put(request):
        if {'id'}.issubset(request.data):
            try:
                contact = get_object_or_404(Contact, pk=int(request.data["id"]))
            except ValueError:
                return JsonResponse({
                    'Status': False,
                    'Error': 'Invalid field type ID.'},
                    status=status.HTTP_400_BAD_REQUEST)

            serializer = ContactSerializer(
                contact,
                data=request.data,
                partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({
                    'Status': True,
                    'Details': serializer.data},
                    status=status.HTTP_200_OK)
            return JsonResponse({
                'Status': False,
                'Error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'Status': False,
            'Error': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request):
        if {'items'}.issubset(request.data):
            for item in request.data["items"].split(','):
                try:
                    contact = get_object_or_404(Contact, pk=int(item))
                    contact.delete()
                except ValueError:
                    return JsonResponse({
                        'Status': False,
                        'Error': 'Invalid argument type (items).'},
                        status=status.HTTP_400_BAD_REQUEST)

                except ObjectDoesNotExist:
                    return JsonResponse({
                        'Status': False,
                        'Error': f'There is no contact with ID{item}'},
                        status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({
                'Status': True},
                status=status.HTTP_200_OK)

        return JsonResponse({
            'Status': False,
            'Error': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)

