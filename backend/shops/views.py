
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.serializers import OrderSerializer
from server.utils import IsShop, IsOwner, get_import, send_email
from .models import Shop, Category, ProductInfo
from .serializers import ShopSerializer, CategoriesSerializer, ProductInfoSerializer

from django.db.models import Q, Sum, F

def not_requireds(requireds):
    return JsonResponse({
        'Status': False,
        'Error': f'Need all required fields {requireds}'},
        status=status.HTTP_400_BAD_REQUEST)


def not_exist():
    return Response({
        'Status': False,
        'Details': 'Shop not exist'},
        status=status.HTTP_404_NOT_FOUND)


def bad_request():
    return JsonResponse({
        'Status': False,
        'Details': 'Bad request'},
        status=status.HTTP_400_BAD_REQUEST)


class ShopsView(generics.ListAPIView):
    queryset = Shop.objects.filter(status=True)
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]


class CategoriesView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [IsAuthenticated]


class ProductInfoView(viewsets.ModelViewSet):
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    http_method_names = ['get', ]
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        query = Q(shop__status=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop',
            'product__category').prefetch_related(
            'product_parameters__parameter').distinct()
        serializer = ProductInfoSerializer(
            queryset,
            many=True)

        return Response(serializer.data)


class ShopState(APIView):
    permission_classes = [IsAuthenticated, IsShop]
    required = {'name', }

    def get(self, request):
        shop = Shop.objects.filter(user_id=request.user.id).first()
        if not shop:
            return not_exist()
        return JsonResponse({
            'Status': True,
            'Details': ShopSerializer(shop).data},
            status=status.HTTP_200_OK)

    def post(self, request):
        request.POST._mutable = True
        request.data.update({'user': request.user.id, 'status': True})
        serializer = ShopSerializer(data=request.data)
        if serializer.is_valid() and self.required.issubset(request.data):
            serializer.save()
        else:
            return JsonResponse({
                'Status': False,
                'Details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({
            'Status': True,
            'Details': serializer.data},
            status=status.HTTP_200_OK)


class ShopUpdate(APIView):
    permission_classes = [IsAuthenticated, IsShop, IsOwner]

    @staticmethod
    def put(request):
        shop = Shop.objects.filter(user_id=request.user.id).first()
        if shop:
            request.POST._mutable = True
            request.data.update({'user': request.user.id, 'name': shop.name})
            serializer = ShopSerializer(shop, data=request.data)
            if serializer.is_valid():
                serializer.save()
            else:
                return JsonResponse({
                    'Status': False,
                    'Details': serializer.errors},
                    status=status.HTTP_409_CONFLICT)
        else:
            return not_exist()
        return JsonResponse({
            'Status': True,
            'Details': serializer.data},
            status=status.HTTP_200_OK)

    @staticmethod
    def delete(request):
        user_id = request.user.id
        shop = Shop.objects.filter(user_id=user_id).first()
        if shop:
            shop.delete()
        else:
            return not_exist()
        return JsonResponse({
            'Status': True,
            'Details': f'DELETED shop {user_id}'},
            status=status.HTTP_200_OK)


class PartnerUpdate(APIView):
    permission_classes = [IsAuthenticated, IsShop, IsOwner]

    @staticmethod
    def post(request):
        url = request.data.get('url')
        if url:
            try:
                get_import(request.user.id, url)
            except IntegrityError as e:
                return JsonResponse({
                    'Status': False,
                    'Errors': f'Integrity Error: {e}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return JsonResponse({
                'Status': True},
                status=status.HTTP_200_OK)

        return JsonResponse({
            'Status': False,
            'Errors': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)


class PartnerOrders(APIView):
    permission_classes = [IsAuthenticated, IsShop]

    @staticmethod
    def get(request, *args, **kwargs):

        order = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(
            status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()

        serializer = OrderSerializer(order, many=True)
        send_email(
            'Order status update',
            'The order has been processed',
            request.user.email)

        return Response(serializer.data)
