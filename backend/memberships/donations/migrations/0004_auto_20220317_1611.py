# Generated by Django 3.2.8 on 2022-03-17 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("donations", "0003_alter_donation_external_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="donation",
            old_name="receiver_user",
            new_name="creator_user",
        ),
        migrations.RenameField(
            model_name="donation",
            old_name="sender_user",
            new_name="fan_user",
        ),
    ]