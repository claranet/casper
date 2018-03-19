import re
from click import BadParameter


RFC1123_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

def regex_validate(pattern):
    def validate(ctx, param, value):
        if value is not None:
            if re.compile(pattern).match(value) == None:
                raise BadParameter('{} is not a valid value'.format(value))
        return value
    return validate