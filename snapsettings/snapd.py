""" Snapd bash commands recreated for Python using the Core REST API """

# Built on example shared by SO user david-k-hess:
# https://stackoverflow.com/a/59594889

import json
import requests
import socket

from snapsettings import util

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def get(self, node, child=None):
        """
        Requires elevated privileges.
        """
        payload = None
        if node == 'snaps' or node == 'find?select=refresh' or node == 'system-info':
            payload = f"v2/{node}"
            if node == 'snaps' and child:
                payload = f"{payload}/{child}"
        elif node == 'system':
            payload = f"v2/snaps/{node}/conf"
        if not payload:
            return None

        result = self.session.get(self.fake_http + payload).json()['result']
        if child and node != 'snaps':
            parts = child.split('.')
            for p in parts:
                result = result.get(p)
        return result

    def list(self):
        return self.get('snaps')

    def info(self, snap):
        return self.get('snaps', snap)

    def get_refresh_list(self):
        result = self.get('find?select=refresh')
        refresh_list = None
        if isinstance(result, list):
            refresh_list = result
        return refresh_list

    def get_refresh_time(self):
        """
        $ snap refresh --time
        """
        r = self.get('system-info', 'refresh')
        last_raw = r.get('last', '')
        last = ''
        if last_raw != '':
            last = util.make_human_readable(last_raw)
        next = util.make_human_readable(r.get('next'))
        time_output = [f"timer: {r.get('timer')}", f"last: {last}", f"next: {next}"]
        return time_output

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
