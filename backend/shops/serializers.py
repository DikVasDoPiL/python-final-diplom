from rest_framework import serializers


from .models import Shop, Category, ProductInfo


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = ('id', )


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id', )


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ('id', 'name')
        read_only_fields = ('id', )
