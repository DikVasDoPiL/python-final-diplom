from django.contrib.auth import get_user_model
from rest_framework import serializers

from shops.serializers import ShopSerializer
from .models import Contact

user = get_user_model()


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = "__all__"
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {
                'write_only': True
            }
        }


class AccountSerializer(serializers.ModelSerializer):

    contacts = ContactSerializer(
        read_only=True,
        many=True
    )
    shop = ShopSerializer(
        read_only=True,
        many=False
    )

    class Meta:
        model = user
        fields = "__all__"
        read_only_fields = ('id', )


class AccountPublicSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = user
        fields = ['id', 'email', 'first_name', 'last_name', 'type', 'contacts', 'shop']
        # fields = "__all__"
        read_only_fields = ('id', )

