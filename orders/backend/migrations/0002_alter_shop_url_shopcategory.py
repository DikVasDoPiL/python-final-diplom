# Generated by Django 5.0 on 2023-12-23 16:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='url',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name='ShopCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='positions', to='backend.category')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='positions', to='backend.shop')),
            ],
        ),
    ]
