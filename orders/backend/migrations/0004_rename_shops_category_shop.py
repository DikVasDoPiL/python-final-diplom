# Generated by Django 5.0 on 2023-12-23 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_alter_category_shops'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='shops',
            new_name='shop',
        ),
    ]
