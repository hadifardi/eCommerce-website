# Generated by Django 4.2.4 on 2023-08-09 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_order_order_id_userprofile_payment_order_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='tracking_code',
            field=models.CharField(default='1234', max_length=60),
            preserve_default=False,
        ),
    ]
