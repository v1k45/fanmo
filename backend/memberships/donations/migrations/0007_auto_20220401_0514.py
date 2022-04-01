# Generated by Django 3.2.8 on 2022-03-31 23:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("donations", "0006_auto_20220401_0510"),
    ]

    operations = [
        migrations.RenameField(
            model_name="donation",
            old_name="is_anonymous",
            new_name="is_hidden",
        ),
        migrations.RenameField(
            model_name="historicaldonation",
            old_name="is_anonymous",
            new_name="is_hidden",
        ),
        migrations.RemoveField(
            model_name="donation",
            name="name",
        ),
        migrations.RemoveField(
            model_name="historicaldonation",
            name="name",
        ),
        migrations.AlterField(
            model_name="donation",
            name="creator_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="donations_received",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="donation",
            name="fan_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="donations",
                to="users.user",
            ),
        ),
    ]
