# Generated by Django 5.1.3 on 2024-11-30 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_alter_order_options_alter_product_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.BigIntegerField(null=True),
        ),
    ]
