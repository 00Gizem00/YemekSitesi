# Generated by Django 4.2.5 on 2023-09-20 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fooddelivery', '0010_alter_product_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
