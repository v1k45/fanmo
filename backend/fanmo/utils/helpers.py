from time import mktime

from django.template.defaultfilters import slugify as dj_slugify


def datestamp(date):
    return int(mktime(date.timetuple()) * 1000)


def slugify(value):
    return dj_slugify(value) or "post"
