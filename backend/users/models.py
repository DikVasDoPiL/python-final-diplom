from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_confirmed', True)
        return self.create_user(email, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
                ('shop', 'Shop'),
                ('buyer', 'Buyer'),
            )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    type = models.CharField(
                verbose_name='Тип пользователя',
                choices=USER_TYPE_CHOICES,
                max_length=8,
                default='B'
            )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'email {self.email}, is_staff {self.is_staff}'

    def get_short_name(self):
        return self.email


class Contact(models.Model):
    user = models.ForeignKey(
        Account,
        verbose_name='Пользователь',
        related_name='contacts',
        blank=True,
        on_delete=models.CASCADE
    )
    city = models.CharField(
        max_length=50,
        verbose_name='Город'
    )
    street = models.CharField(
        max_length=100,
        verbose_name='Улица'
    )
    house = models.CharField(
        max_length=15,
        verbose_name='Дом',
        blank=True
    )
    structure = models.CharField(
        max_length=15,
        verbose_name='Корпус',
        blank=True
    )
    building = models.CharField(
        max_length=15,
        verbose_name='Строение',
        blank=True
    )
    apartment = models.CharField(
        max_length=15,
        verbose_name='Квартира',
        blank=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'
