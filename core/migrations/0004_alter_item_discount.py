# Generated by Django 4.2.4 on 2023-08-06 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_order_ordered_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='discount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]