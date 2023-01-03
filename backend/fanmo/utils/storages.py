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

    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        Re-use already generated signed S3 URLs to make use of browser cache.
        """
        # extract the URL from cache if available
        expire = expire or settings.AWS_QUERYSTRING_EXPIRE
        file_name_hash = hashlib.md5(name.encode()).hexdigest()
        cache_key = f"cachedmedia:{file_name_hash}:{expire}"
        if result := cache.get(cache_key):
            return result

        # set cache timeout to less than 1 hour irrespecitve of the actual expiration
        # this keeps the URL refreshed for cases where it is intended to be consumed by an external system like an e-mail client.
        # by refreshing the link early, the e-mail client will be able display the media upto the specified expiration time (e.g. a year)
        # if this is not done, we could hit an edge-case where the email client consumes a URL which is valid but about to expire very soon. 
        timeout = int(settings.AWS_QUERYSTRING_EXPIRE * 0.75)
        result = super().url(name, parameters, expire, http_method)
        cache.set(cache_key, result, timeout)
        return result
