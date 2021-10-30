#!/usr/bin/env python3

""" Gtk window to manage Snapd settings """

import gi
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("NM", "1.0")
from gi.repository import NM
from pathlib import Path

from snapsettings import snapd
from snapsettings import util


class SettingsApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id='org.wasta.apps.snap-settings',
        )

        # Add glade GUI file.
        self.app_ui_dir = '/usr/share/snap-settings/ui/'
        dir = Path(self.app_ui_dir)
        if not dir.is_dir():
            self.app_ui_dir = '../data/ui/'

        # Instantiate builder.
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.app_ui_dir + 'snap-settings.glade')

        # Get snapd instance.
        self.snap = snapd.Snap()

        # Get initial values. (requires pkexec)
        self.metered_handling, self.revisions_kept = self.get_refresh_config() # pkexec
        self.connection, self.metered_status = self.get_metered_status()
        self.refresh_timer, self.last_refresh, self.next_refresh = self.get_refresh_timer_info()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        """
        # Instantiate builder.
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.app_ui_dir + 'snap-settings.glade')

        # Get initial values. (requires pkexec)
        self.metered_handling, self.revisions_kept = self.get_refresh_config() # pkexec
        self.connection, self.metered_status = self.get_metered_status()
        self.refresh_timer, self.last_refresh, self.next_refresh = self.get_refresh_timer_info()
        """
        # Set initial GUI values for properties of Gtk widgets not set by Glade.
        ids = {
            'switch_metered': ['set_state', self.metered_handling],
            'current_connection': ['set_text', self.connection],
            'checkbox_metered': ['set_active', self.metered_status],
            'timer_entry': ['set_text', self.refresh_timer],
            'revs_kept': ['set_value', self.revisions_kept],
            'refresh_dates': ['set_label', self.next_refresh]
        }
        for id, list in ids.items():
            func = list[0]
            value = list[1]
            self.set_entity_value(id=id, func=func, value=value)

    def do_activate(self):
        self.builder.connect_signals(Handler())

        window = self.builder.get_object("window_settings")
        self.add_window(window)
        window.show()

    def get_metered_status(self):
        """
        Returns the connection name and NetworkManager's metered status.
        If there is no internet connection, then "disconnected" is returned.
        statuses: 0 unknown, 1 yes, 2 no, 3 yes (guessed), 4 no (guessed)
        """
        # TODO: Verify this with other connections:
        #   + offline
        #   + wired
        #   - ppp
        #   - bluetooth?

        # Get the default route.
        #gws = netifaces.gateways()
        # Get device.
        #device = client.get_device_by_iface(gw4_device)

        # Get connection name from NM client object.
        client = NM.Client.new(None)
        primary_connection = client.get_primary_connection()
        if not primary_connection:
            self.inet_connection = '--'
            self.metered_status = 0
            return self.inet_connection, self.metered_status
        self.inet_connection = primary_connection.get_id()

        # Get metered status.
        # https://developer.gnome.org/NetworkManager/unstable/nm-dbus-types.html#NMMetered
        self.metered_status = client.props.metered

        return self.inet_connection, self.metered_status

    def get_refresh_config(self):
        """
        Returns system refresh.retain and refresh.metered settings.
        """
        # Get general refresh config.
        response = self.snap.get('system', 'refresh')
        if not util.verify_response(response):
            return None, None
        refresh_config = response.get('result')
        # Get specific values.
        metered_handling = refresh_config.get('metered', 'null')
        revisions_kept = int(refresh_config.get('retain', '2'))
        # print("refresh.retain defaults to 2 if unset")

        return metered_handling, revisions_kept

    def get_refresh_timer_info(self):
        """ Returns value of snapd's refresh timer. """
        result = self.snap.get('system-info', 'refresh.timer').get('result')
        refresh_timer = result.get('refresh').get('timer')
        last = self.last_refresh = result.get('refresh').get('last')
        if not last:
            last = ''
        last_refresh = last
        next_refresh = result.get('refresh').get('next')
        return refresh_timer, last_refresh, next_refresh

    def set_entity_value(self, **kwargs):
        """ Sets initial values of certain Gtk widget properties. """
        item = self.builder.get_object(kwargs['id'])
        func = kwargs['func']
        value = kwargs['value']
        if func == 'set_focus_on_click':
            item.set_focus_on_click(value)
        elif func == 'set_state':
            if value == 'hold':
                value = False
            elif value == 'null':
                value = True
            else:
                print(value)
                return
            item.set_state(value)
        elif func == 'set_text':
            item.set_text(value)
        elif func == 'set_value':
            item.set_value(int(value))
        elif func == 'set_label':
            item.set_label(value)
        elif func == 'set_active':
            if value == 0 or value == 2 or value == 4: # 'unknown', 'no', 'no (guessed)'
                state = False
            elif value == 1 or value == 3: # 'yes' or 'yes (guessed)'
                state = True
            item.set_active(state)
        else:
            print("error: unkown function")
            exit(1)

    def set_metered_status(self, connection, state):
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

    def set_metered_handling(self, state):
        """
        states: 'null' or 'hold'
        (requires elevated privileges)
        """
        self.snap.set_refresh_metered(state)

    def set_refresh_timer(self, value):
        """
        default value:  00:00~24:00/4
        wasta value:    sun5,02:00
        (requires elevated privileges)
        """
        self.snap.set_refresh_timer(value)

    def set_revisions_kept(self, revs):
        """
        default revs:   2
        wasta revs:     2
        (requires elevated privileges)
        """
        self.snap.set_refresh_retain(revs)

class Handler():
    def gtk_widget_destroy(self, *args):
        app.quit()

    def on_switch_metered_state_set(self, *args):
        if args[1] == True:
            state = 'null'
        elif args[1] == False:
            state = 'hold'
        app.set_metered_handling(state)

    def on_checkbox_metered_toggled(self, *args):
        state = args[0].get_active()
        if app.connection == '--':
            item = app.builder.get_object('checkbox_metered')
            item.set_active(False)
            return
        app.set_metered_status(app.connection, state)

    def on_timer_apply_clicked(self, *args):
        input_obj = args[0]
        suggested_obj = app.builder.get_object('timer_suggested')
        if input_obj.get_text():
            input = input_obj.get_text()
        else:
            input = suggested_obj.get_text()
            input_obj.set_text(input)
        app.set_refresh_timer(input)

    def on_revs_kept_value_changed(self, *args):
        revs = int(args[0].get_value())
        app.set_revisions_kept(revs)


app = SettingsApp()
