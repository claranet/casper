import re
from click import BadParameter

RFC1123_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


def regex_validate(pattern):
    def validate(ctx, param, value):
        if value is not None:
            if re.compile(pattern).match(value) is None:
                raise BadParameter('{} is not a valid value'.format(value))
        return value

    return validate


def is_dev_version(version):
    if version.startswith('GHOST-'):
        version = 'dev'
    if version in {'dev', 'master', 'stable'}:
        return True
    return False
