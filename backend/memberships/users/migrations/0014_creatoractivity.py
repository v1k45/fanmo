# Generated by Django 3.2.8 on 2022-05-25 10:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("donations", "0008_auto_20220406_0700"),
        ("subscriptions", "0012_auto_20220513_0408"),
        ("posts", "0010_auto_20220426_0122"),
        ("users", "0013_notification_prefs"),
    ]

    operations = [
        migrations.CreateModel(
            name="CreatorActivity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("new_membership", "New Membership"),
                            ("membership_update", "Membership Update"),
                            ("membership_stop", "Membership Stop"),
                            ("donation", "Donation"),
                            ("comment", "Comment"),
                            ("comment_reply", "Comment Reply"),
                            ("follower", "Follower"),
                        ],
                        max_length=32,
                    ),
                ),
                ("message", models.TextField()),
                ("data", models.JSONField(default=dict)),
                (
                    "comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator_activities",
                        to="posts.comment",
                    ),
                ),
                (
                    "creator_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "donation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator_activities",
                        to="donations.donation",
                    ),
                ),
                (
                    "fan_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fan_activities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "membership",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator_activities",
                        to="subscriptions.membership",
                    ),
                ),
            ],
            options={
                "db_table": "creator_activities",
                "ordering": ("-created_at",),
                "default_related_name": "creator_activities",
            },
        ),
    ]
