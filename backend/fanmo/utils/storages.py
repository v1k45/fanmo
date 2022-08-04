import hashlib

from django.conf import settings
from django.core.cache import cache
from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = False

    def url(self, name):
        """
        Re-use already generated signed S3 URLs to make use of browser cache.
        """
        cache_key = "cachedmedia:" + hashlib.md5(name.encode()).hexdigest()
        result = cache.get(cache_key)
        if result:
            return result

        # cache miss
        result = super().url(name)
        timeout = int(settings.AWS_QUERYSTRING_EXPIRE * 0.75)
        cache.set(cache_key, result, timeout)
        return result
