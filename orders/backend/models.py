from django.db import models


# Create your models here.
class Shop(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField()

    def __str__(self):
        return f"<class Shop {self.name}: {self.url}>"


class Category(models.Model):
    name = models.CharField(max_length=100)
    shops = models.ManyToManyField("Shop")

    def __str__(self):
        return f"<class Category {self.name}>"

