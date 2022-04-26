# Generated by Django 3.2.8 on 2022-04-25 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0009_auto_20220413_2032"),
    ]

    operations = [
        migrations.AddField(
            model_name="reaction",
            name="comment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reactions",
                to="posts.comment",
            ),
        ),
        migrations.AlterField(
            model_name="reaction",
            name="post",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reactions",
                to="posts.post",
            ),
        ),
    ]