import datetime
import time


def make_human_readable(input):
    # input has this form: 2020-08-30T02:00:00+01:00
    # strip ':' from TZ
    if input:
        t = input[:-3] + input[-2:]

        # Define formats.
        fmt_in = '%Y-%m-%dT%H:%M:%S%z'
        #fmt_out = '%c' # locale date & time
        fmt_out = '%a, %d %B %Y, %H:%M %Z'

        # Convert to Posix, then convert to human readable.
        pos = time.mktime(datetime.datetime.strptime(t, fmt_in).timetuple())
        human_readable = datetime.datetime.fromtimestamp(pos).strftime(fmt_out)
        return human_readable
    return None
