# Generated by Django 3.2.14 on 2022-10-22 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_auto_20220725_0043"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="social_image",
            field=models.ImageField(blank=True, upload_to="profiles/social/"),
        ),
    ]