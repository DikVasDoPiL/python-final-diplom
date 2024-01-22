from rest_framework import serializers

from shops.serializers import ProductInfoSerializer
from users.serializers import ContactSerializer
from .models import OrderItem, Order


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ('id', )
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(
        read_only=True
    )


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(
        read_only=True,
        many=True
    )

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(
        read_only=True
    )

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', )
