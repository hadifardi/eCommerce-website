# Generated by Django 4.2.4 on 2023-08-09 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_payment_tracking_code'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]