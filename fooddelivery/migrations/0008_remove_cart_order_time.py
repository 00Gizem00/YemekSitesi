# Generated by Django 4.2.5 on 2023-10-18 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fooddelivery', '0007_cart_delete_shoppingcart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='order_time',
        ),
    ]