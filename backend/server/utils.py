import requests
from django.db import IntegrityError
from yaml import load as load_yaml, Loader
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework import permissions

from shops.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


def send_email(title, message, email, *args, **kwargs):
    email_list = list()
    email_list.append(email)
    try:
        msg = EmailMultiAlternatives(
            subject=title,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=email_list
        )
        msg.send()
        return f'{title}: {msg.subject}, Message:{msg.body}'
    except Exception as e:
        raise e


def get_import(partner, url):
    if url:
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError as e:
            return {'Status': False, 'Error': str(e)}
        else:
            stream = requests.get(url).content

        data = load_yaml(stream, Loader=Loader)
        try:
            shop, _ = Shop.objects.get_or_create(name=data['shop'],
                                            user_id=partner)
        except IntegrityError as e:
            return {'Status': False, 'Error': str(e)}

        for category in data['categories']:
            category_object, _ = Category.objects.get_or_create(
                id=category['id'], name=category['name'])
            category_object.shops.add(shop.id)
            category_object.save()

        ProductInfo.objects.filter(shop_id=shop.id).delete()
        for item in data['goods']:
            product, _ = Product.objects.get_or_create(
                name=item['name'], category_id=item['category']
            )
            product_info = ProductInfo.objects.create(
                product_id=product.id, external_id=item['id'],
                model=item['model'], price=item['price'],
                price_rrc=item['price_rrc'], quantity=item['quantity'],
                shop_id=shop.id
            )
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(
                    name=name
                )
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=parameter_object.id, value=value
                )
        return {'Status': True}
    return {'Status': False, 'Errors': 'Url is false'}


class IsShop(permissions.BasePermission):
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.type == 'shop'


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow updating his own profile
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # obj here is a UserProfile instance
        return obj.user == request.user



