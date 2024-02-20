import json

from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from ujson import loads as load_json
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from server.utils import send_email
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


# Create your views here.

@extend_schema(
        request=OrderSerializer,
        responses=None
    )
class BasketView(APIView):
    permission_classes = [IsAuthenticated]


    @staticmethod
    def get(request):
        basket = Order.objects.filter(
            user_id=request.user.id, status='basket').prefetch_related(
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).distinct()
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        items = request.data.get('items')
        if items:
            try:
                items_dict = json.dumps(items)
            except ValueError as e:
                JsonResponse({
                    'Status': False,
                    'Errors': f'Invalid request format {e}'},
                    status=status.HTTP_204_NO_CONTENT)
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id,
                    status='basket'
                )
                objects_created = 0
                for order_item in load_json(items_dict):
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid(raise_exception=True):
                        try:
                            serializer.save()
                        except IntegrityError as e:
                            return JsonResponse({
                                'Status': False,
                                'Errors': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
                        else:
                            objects_created += 1

                    else:
                        JsonResponse({
                            'Status': False,
                            'Errors': serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return JsonResponse({
                    'Status': True,
                    'Objects created': objects_created},
                    status=status.HTTP_201_CREATED)
        return JsonResponse({
            'Status': False,
            'Errors': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = json.dumps(items_sting)
            except ValueError as e:
                JsonResponse({
                    'Status': False,
                    'Errors': f'Invalid request format {e}'},
                    status=status.HTTP_204_NO_CONTENT)
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id,
                    status='basket'
                )
                objects_updated = 0
                for order_item in json.loads(items_dict):
                    if isinstance(order_item['id'], int) and isinstance(order_item['quantity'], int):
                        objects_updated += OrderItem.objects.filter(
                            order_id=basket.id,
                            product_info_id=order_item['id']).update(
                            quantity=order_item['quantity'])

                return JsonResponse({
                    'Status': True,
                    'Objects created': objects_updated},
                    status=status.HTTP_201_CREATED)

        return JsonResponse({
            'Status': False,
            'Errors': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, *args, **kwargs):

        items = request.data.get('items')
        if items:
            items_list = items.split(',')
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id,
                status='basket'
            )
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return JsonResponse({
                    'Status': True,
                    'Objects created': deleted_count},
                    status=status.HTTP_200_OK)
        return JsonResponse({
            'Status': False,
            'Error': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
        request=OrderSerializer,
        responses=None
    )
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        order = Order.objects.filter(
            user_id=request.user.id).exclude(status='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))
        ).distinct().order_by('-date')

        serializer = OrderSerializer(
            order,
            many=True
        )

        return Response(serializer.data)

    @staticmethod
    def post(request):

        if {'id', 'contact'}.issubset(request.data):
            if request.data['id'].isdigit():
                try:
                    is_updated = Order.objects.filter(
                        user_id=request.user.id, id=request.data['id']).update(
                        contact_id=request.data['contact'],
                        status='new')
                except IntegrityError as e:
                    return JsonResponse({
                        'Status': False,
                        'Errors': f'The arguments are incorrectly specified {e}'},
                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    if is_updated:
                        send_email(
                            'Order status update',
                            'The order has been formed ',
                            request.user.email)
                        return JsonResponse({
                            'Status': True},
                            status=status.HTTP_200_OK)

        return JsonResponse({
            'Status': False,
            'Errors': 'All necessary arguments are not specified'},
            status=status.HTTP_400_BAD_REQUEST)
