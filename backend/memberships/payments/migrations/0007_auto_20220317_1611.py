# Generated by Django 3.2.8 on 2022-03-17 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_auto_20220219_0210'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='seller_user',
            new_name='creator_user',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='buyer_user',
            new_name='fan_user',
        ),
    ]
