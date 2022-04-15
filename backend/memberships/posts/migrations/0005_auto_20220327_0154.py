# Generated by Django 3.2.8 on 2022-03-26 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscriptions", "0010_tier_benefits"),
        ("posts", "0004_reaction"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="minimum_tier",
        ),
        migrations.AddField(
            model_name="post",
            name="allowed_tiers",
            field=models.ManyToManyField(related_name="posts", to="subscriptions.Tier"),
        ),
        migrations.AlterField(
            model_name="post",
            name="visibility",
            field=models.CharField(
                choices=[
                    ("public", "Public"),
                    ("all_members", "All Members"),
                    ("allowed_tiers", "Allowed Tiers"),
                ],
                default="public",
                max_length=16,
            ),
        ),
    ]