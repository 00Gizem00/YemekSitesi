# Generated by Django 4.2.5 on 2023-10-17 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0003_restaurant_category_restaurant_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant_category',
            name='restaurant_category',
        ),
        migrations.AddField(
            model_name='restaurant_category',
            name='name',
            field=models.CharField(max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants', to='restaurants.restaurant_category', to_field='name'),
        ),
    ]
