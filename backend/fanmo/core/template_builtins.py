from django import template
from django.conf import settings

from fanmo.utils.storages import MediaRootS3Boto3Storage

register = template.Library()


@register.simple_tag
def image_url(file_instance):
    if isinstance(file_instance.storage, MediaRootS3Boto3Storage):
        return file_instance.storage.url(file_instance.name, expire=3600 * 24 * 365)
    else:
        return settings.BASE_URL + file_instance.storage.url
