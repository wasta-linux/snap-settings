""" Snapd bash commands recreated for Python using the Core REST API """

import json
import subprocess

from snapsettings import util


class Snap():
    def __init__(self, *args, **kwargs):
        self.args = [*args]
        self.kwargs = {**kwargs}

#     def __enter__(self):
#         return self
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         self.session.close()

    def info(self, snap):
        return self.get('snaps', snap).get('result')

    def list(self):
        return self.get('snaps').get('result')

    def get_refresh_list(self):
        result = self.get('find?select=refresh').get('result')
        refresh_list = None
        if isinstance(result, list):
            refresh_list = result
        return refresh_list

    def get_refresh_time(self):
        """
        $ snap refresh --time
        """
        result = self.get('system-info', 'refresh').get('result')
        r = result.get('refresh')

        last_raw = r.get('last', '')
        last = ''
        if last_raw != '':
            last = util.make_human_readable(last_raw)
        next = util.make_human_readable(r.get('next'))
        time_output = [f"timer: {r.get('timer')}", f"last: {last}", f"next: {next}"]
        return time_output

    def get(self, node, child=None):
        """
        Some calls require elevated privileges.
        """
        typical = [
            'connections',
            'find?select=refresh',
            'snaps',
            'system-info',
        ]
        path = 'snapd:///'
        if node in typical:
            path = f"{path}v2/{node}"
            if node == 'snaps' and child:
                path = f"{path}/{child}"
        elif node == 'system':
            path = f"{path}v2/snaps/{node}/conf"
        if path == 'snapd:///':
            return None

        cmd = ['/snap/bin/http', path]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = json.loads(p.stdout.decode())
        return output
        # result = out.get('result')
        # if child and node != 'snaps':
        #     parts = child.split('.')
        #     for part in parts:
        #         result = result.get(part)
        # return result
