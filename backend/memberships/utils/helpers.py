from time import mktime


def datestamp(date):
    return int(mktime(date.timetuple()) * 1000)
