# Generated by Django 4.2.4 on 2023-08-07 07:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_alter_item_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('province', models.CharField(choices=[('CH', 'Choose...'), ('EA', 'آذربایجان شرقی'), ('WA', 'آذربایجان غربی'), ('AR', 'اردبیل'), ('ES', 'اصفهان'), ('AL', 'البرز'), ('IL', 'ایلام'), ('BU', 'بوشهر'), ('TH', 'تهران'), ('CB', 'چهارمحال و بختیاری'), ('KJ', 'خراسان جنوبی'), ('KR', 'خراسان رضوی'), ('KS', 'خراسان شمالی'), ('KZ', 'خوزستان'), ('ZN', 'زنجان'), ('SM', 'سمنان'), ('SB', 'سیستان و بلوچستان'), ('FR', 'فارس'), ('QZ', 'قزوین'), ('QM', 'قم'), ('KD', 'کردستان'), ('KN', 'کرمان'), ('KM', 'کرمانشاه'), ('KB', 'کهگیلویه و بویراحمد'), ('GL', 'گلستان'), ('GI', 'گیلان'), ('LR', 'لرستان'), ('MZ', 'مازندران'), ('MK', 'مرکزی'), ('HR', 'هرمزگان'), ('HM', 'همدان'), ('YZ', 'یزد')], max_length=2)),
                ('city', models.CharField(max_length=50)),
                ('postal_code', models.CharField(max_length=50)),
                ('full_address', models.CharField(max_length=250)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.billingaddress'),
        ),
    ]