
from django.db import models

from shops.models import Product, Shop
from users.models import Account as User

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Order(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='orders',
        blank=True,
        on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        verbose_name='Статус',
        choices=STATE_CHOICES,
        max_length=15)


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name='Магазин',
        related_name='ordered_items',
        blank=True,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Заказанные позиции"

