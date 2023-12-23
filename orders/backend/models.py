from django.db import models


# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    shop = models.ManyToManyField(Shop, related_name='shops')

    def __str__(self):
        return self.name


class ShopCategory(models.Model):
    shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        related_name='positions',
    )
    product = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='positions',
    )
