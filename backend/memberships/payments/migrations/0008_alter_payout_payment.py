# Generated by Django 3.2.8 on 2022-04-22 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_auto_20220317_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payout',
            name='payment',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to='payments.payment'),
        ),
    ]
