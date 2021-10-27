# Generated by Django 3.2.8 on 2021-10-27 01:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import hashid_field.field
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', auto_created=True, min_length=7, prefix='', primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('link', 'Link')], max_length=16)),
                ('text', models.TextField(blank=True)),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to='uploads/content/')),
                ('link', models.URLField()),
                ('link_og', models.JSONField()),
                ('link_embed', models.JSONField()),
            ],
            options={
                'db_table': 'contents',
                'ordering': ('-created_at',),
                'abstract': False,
                'default_related_name': 'contents',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', auto_created=True, min_length=7, prefix='', primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', django_extensions.db.fields.AutoSlugField(allow_duplicates=True, blank=True, editable=False, populate_from='title')),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('all_members', 'All Members'), ('minimum_tier', 'Minimum Tier')], default='public', max_length=16)),
                ('is_published', models.BooleanField(default=True)),
                ('author_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
                ('content', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='posts.content')),
                ('minimum_tier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='subscriptions.tier')),
            ],
            options={
                'db_table': 'posts',
                'ordering': ('-created_at',),
                'abstract': False,
                'default_related_name': 'posts',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', hashid_field.field.HashidAutoField(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', auto_created=True, min_length=7, prefix='', primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('body', models.TextField()),
                ('is_published', models.BooleanField(default=True)),
                ('author_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.post')),
            ],
            options={
                'db_table': 'comments',
                'ordering': ('-created_at',),
                'abstract': False,
                'default_related_name': 'comments',
            },
        ),
    ]
