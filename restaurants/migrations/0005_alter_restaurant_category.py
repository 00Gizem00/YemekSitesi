# Generated by Django 4.2.5 on 2023-10-17 13:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0004_remove_restaurant_category_restaurant_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants', to='restaurants.restaurant_category'),
        ),
    ]