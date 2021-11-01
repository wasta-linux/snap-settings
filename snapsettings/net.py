import os
import subprocess
# import gi

# gi.require_version("NM", "1.0")
# from gi.repository import NM


# def get_nm_connection():
#     # Get connection name from NM client object.
#     client = NM.Client.new(None)
#     primary_connection = client.get_primary_connection()
#     if not primary_connection:
#         return '--', client
#     return primary_connection.get_id(), client

def get_nmcli_connection():
    primary_connection = '--'
    ipvs = ['IP4', 'IP6']
    connections = {}
    for ipv in ipvs:
        cmd = [
            f"{os.environ['SNAP']}/usr/bin/nmcli",
            '--terse',
            f"--field=GENERAL.CONNECTION,{ipv}.GATEWAY",
            'device',
            'show',
        ]
        p = subprocess.run(
            cmd,
            env={'LANG': 'C'},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        output = p.stdout.decode().splitlines()
        con = None
        gw = None
        for i, line in enumerate(output):
            if line[:12] == 'IP4.GATEWAY:':
                g = line.split(':')[1]
                if g:
                    gw = g
                    con = output[i-1].split(':')[1]
                    connections[ipv] = con
                    break
    # Default to IPv4 route.
    # TODO: Is this really the way to go? Can there be an IP4 route on one
    #   connection and an IP6 route on another?
    for ipv in ipvs[::-1]:
        if connections.get(ipv):
            primary_connection = connections.get(ipv)

    return primary_connection

# def get_metered_status(app):
#     """
#     Returns the connection name and NetworkManager's metered status.
#     If there is no internet connection, then "disconnected" is returned.
#     statuses: 0 unknown, 1 yes, 2 no, 3 yes (guessed), 4 no (guessed)
#     """
#     # TODO: Verify this with other connections:
#     #   + offline
#     #   + wired
#     #   - ppp
#     #   - bluetooth?
#
#     # Get connection name.
#     app.inet_connection, nmclient = get_nm_connection()
#     if app.inet_connection == '--':
#         app.metered_status = 0
#         return app.inet_connection, app.metered_status
#
#     # Get metered status.
#     # https://developer.gnome.org/NetworkManager/unstable/nm-dbus-types.html#NMMetered
#     app.metered_status = nmclient.props.metered
#
#     return app.inet_connection, app.metered_status

def get_metered_status(inet_connection):
    """
    Returns the connection name and NetworkManager's metered status.
    statuses: 0 unknown, 1 yes, 2 no, 3 yes (guessed), 4 no (guessed)
    """
    # Get connection name from nmcli.
    # app.inet_connection = get_nmcli_connection()
    # if not app.inet_connection:
    #     app.inet_connection = '--'
    #     app.metered_status = 0
    #     return app.inet_connection, app.metered_status

    if inet_connection == '--':
        return '0'

    # Get metered status.
    cmd = [
        'nmcli',
        '--field',
        'connection.metered',
        'connection',
        'show',
        # app.inet_connection,
        inet_connection,
    ]
    p = subprocess.run(cmd, env={'LANG': 'C'}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # app.metered_status = p.stdout.decode().split()[1]
    return p.stdout.decode().split()[1]

def set_metered_status(app, connection, state):
    """
    statuses: unknown, yes, no, yes (guessed), no (guessed)
    (requires elevated privileges)
    """
    status = 'no'
    if state == True:
        status = 'yes'
    # TODO: Figure out how to use NM API for this.
    #   NOTE: NetworkManager seems to override snap-settings from "no" to
    #       "guess yes" when on an Android hotspot connection.
    subproc = subprocess.run(
        ['nmcli', 'connection', 'modify', connection, 'connection.metered', status],
        env={'LANG': 'C'},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
