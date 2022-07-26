import re
from time import mktime

from django.template.defaultfilters import slugify as dj_slugify


def datestamp(date):
    return int(mktime(date.timetuple()) * 1000)


def slugify(value):
    return dj_slugify(value) or "post"


def replace_format(html, template, value):
    return re.sub(template % "(.*)", template % value, html, 1)
