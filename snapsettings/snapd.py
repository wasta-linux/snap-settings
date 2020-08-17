""" Snapd bash commands recreated for Python using the Core REST API """

# Built on example shared by SO user david-k-hess:
# https://stackoverflow.com/a/59594889

import datetime
import json
import requests
import socket
import time

from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from requests.adapters import HTTPAdapter


class SnapdConnection(HTTPConnection):
    def __init__(self):
        super().__init__("localhost")

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect("/run/snapd.socket")

class SnapdConnectionPool(HTTPConnectionPool):
    def __init__(self):
        super().__init__("localhost")

    def _new_conn(self):
        return SnapdConnection()

class SnapdAdapter(HTTPAdapter):
    def get_connection(self, url, proxies=None):
        return SnapdConnectionPool()

class Snap():
    def __init__(self):
        self.session = requests.Session()
        self.fake_http = 'http://snapd/'
        self.session.mount(self.fake_http, SnapdAdapter())

    def list(self):
        payload = 'v2/snaps'
        result = self.session.get(self.fake_http + payload).json()['result']
        return result

    def info(self, snap):
        payload = 'v2/snaps/' + snap
        result = self.session.get(self.fake_http + payload).json()['result']
        return result

    def refresh_list(self):
        payload = 'v2/find?select=refresh'
        result = self.session.get(self.fake_http + payload).json()['result']
        if type(result) is dict:
            print(result['message'])
            result = []
        return result

    def refresh_time(self):
        """
        $ snap refresh --time
        """
        def make_human_readable(input):
            # input has this form: 2020-08-30T02:00:00+01:00
            # strip ':' from TZ
            t = input[:-3] + input[-2:]

            # Define formats.
            fmt_in = '%Y-%m-%dT%H:%M:%S%z'
            #fmt_out = '%c' # locale date & time
            fmt_out = '%a, %d %B %Y, %H:%M %Z'

            # Convert to Posix, then convert to human readable.
            pos = time.mktime(datetime.datetime.strptime(t, fmt_in).timetuple())
            human_readable = datetime.datetime.fromtimestamp(pos).strftime(fmt_out)
            return human_readable

        payload = 'v2/system-info'
        result = self.session.get(self.fake_http + payload).json()['result']
        r = result['refresh']
        last = make_human_readable(r['last'])
        next = make_human_readable(r['next'])
        time_output = ['timer: ' + r['timer'], 'last: ' + last, 'next: ' + next]
        return time_output

    def get_system_info(self):
        """ Not used. """
        payload = 'v2/system-info'
        result = self.session.get(self.fake_http + payload).json()['result']
        return result

    def get_refresh_settings(self):
        payload = 'v2/snaps/system/conf'
        result = self.session.get(self.fake_http + payload).json()['result']['refresh']
        return result

    def set_refresh_retain(self, value):
        """
        Equivalent to:
        $ sudo snap set system refresh.retain=value
        """
        dest = 'v2/snaps/system/conf'
        # payload needs to be JSON-encoded
        payload = json.dumps({'refresh.retain': value})
        result = self.session.put(self.fake_http + dest, data=payload)
        return result

    def set_refresh_metered(self, value):
        """
        Equivalent to:
        $ snap set system refresh.metered=value
        """
        dest = 'v2/snaps/system/conf'
        # 'null' value needs to be PUT as ''
        value = '' if value == 'null' else value
        # payload needs to be JSON-encoded
        payload = json.dumps({'refresh.metered': value})
        result = self.session.put(self.fake_http + dest, data=payload)
        return result

    def set_refresh_timer(self, value):
        """
        Equivalent to:
        $ snap set system refresh.timer=value
        """
        dest = 'v2/snaps/system/conf'
        # payload needs to be JSON-encoded
        payload = json.dumps({'refresh.timer': value})
        result = self.session.put(self.fake_http + dest, data=payload)
        return result
