#!/usr/bin/env python3

""" Gtk window to manage Snapd settings """

import gi
import json
import netifaces
import os
import re
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from pathlib import Path


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

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # Instantiate builder.
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.app_ui_dir + 'snap-settings.glade')

        # Get initial values. (requires pkexec)
        self.metered_handling, self.revisions_kept = self.get_system_settings() # pkexec
        self.connection, self.metered_status = self.get_metered_status()
        self.refresh_timer, self.last_refresh, self.next_refresh = self.get_refresh_info()

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
        Returns the connection name and nmcli's metered status.
        If there is no internet connection, then "disconnected" is returned.
        statuses: unknown, yes, no, yes (guessed), no (guessed)
        """
        # TODO: Verify this with other connections:
        #   + offline
        #   + wired
        #   - ppp
        #   - bluetooth?
        # Get device from the default route.
        gws = netifaces.gateways()
        try:
            gw4_device = gws['default'][netifaces.AF_INET][1]
        except KeyError:
            self.inet_connection = "(offline)"
            self.metered_status = "disconnected"
            # TODO: Need to disable checkbox_metered when disconnected.
            self.builder.get_object('box_connection').hide()
            return self.inet_connection, self.metered_status
        subproc = subprocess.run(
            ['nmcli', '-t', '-f', 'GENERAL.CONNECTION', '--mode', 'tabular', 'dev', 'show', gw4_device],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        # Get connection name.
        self.inet_connection = subproc.stdout.rstrip()
        # Get metered status.
        if self.inet_connection:
            subproc = subprocess.run(
                ['nmcli', '-f', 'connection.metered', 'connection', 'show', self.inet_connection],
                env={'LANG': 'C'},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            self.metered_status = subproc.stdout.split(':')[1].strip()
        return self.inet_connection, self.metered_status

    def sanitize_json(self, input):
        # Need to strip anything outside of { ... }.
        #   Extra text (e.g. "WARNING...") can be returned by $ snap get ...
        output = str(re.search('^\{\n(.*\n)*\}$', input, re.MULTILINE).group(0))
        return output

    def get_system_settings(self):
        """ Returns system settings requiring elevated privileges. """
        # Get refresh.retain setting.
        try:
            subproc = subprocess.run(
                ['pkexec', 'snap', 'get', '-d', 'system', 'refresh.retain'],
                stdout=subprocess.PIPE,
                universal_newlines=True,
                check=True
            )
            data = json.loads(self.sanitize_json(subproc.stdout))
            self.revisions_kept = data['refresh.retain']
        except subprocess.CalledProcessError as e:
            # Is this a pkexec error or a snap error?
            if e.returncode == 126: # User cancelled pkexec authorization window.
                exit(1)
            else: # Error in snap command; most likely due to unset refresh.retain.
                self.revisions_kept = 2
        try:
            subproc = subprocess.run(
                ['pkexec', 'snap', 'get', '-d', 'system', 'refresh.metered'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                check=True
            )
            data = json.loads(self.sanitize_json(subproc.stdout))
            self.metered_handling = data['refresh.metered']
        except subprocess.CalledProcessError as e:
            # Error in snap command; most likely due to unset refresh.metered.
            self.metered_handling = 'null'
        return self.metered_handling, self.revisions_kept

    def get_refresh_info(self):
        """ Returns value of snapd's refresh timer. """
        subproc = subprocess.run(
            ['snap', 'refresh', '--time'],
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        lines = subproc.stdout.splitlines()
        self.refresh_timer = lines[0].split()[1]
        self.last_refresh = lines[1].split()[1]
        self.next_refresh = lines[2].split(':',1)[1]
        return self.refresh_timer, self.last_refresh, self.next_refresh

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
            item.set_value(value)
        elif func == 'set_label':
            item.set_label(value)
        elif func == 'set_active':
            if value == 'unknown' or value == 'no' or value == 'no (guessed)' or value == 'disconnected':
                state = False
            elif value == 'yes' or value == 'yes (guessed)':
                state = True
            item.set_active(state)

        else:
            print("error: unkown function")
            exit(1)

    def set_metered_status(self, connection, state):
        """
        statuses: unknown, yes, no, yes (guessed), no (guessed)
        """
        status = 'no'
        if state == True:
            status = 'yes'
        subproc = subprocess.run(
            ['nmcli', 'connection', 'modify', connection, 'connection.metered', status],
            env={'LANG': 'C'},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def set_metered_handling(self, state):
        subproc = subprocess.run(
            ['pkexec', 'snap', 'set', 'system', 'refresh.metered='+state],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def set_refresh_timer(self, value):
        try:
            subproc = subprocess.run(
                ['pkexec', 'snap', 'set', 'system', 'refresh.timer='+value],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except:
            value = refresh_timer
            subproc = subprocess.run(
                ['pkexec', 'snap', 'set', 'system', 'refresh.timer='+value],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

    def set_revisions_kept(self, revs):
        try:
            subproc = subprocess.run(
                ['pkexec', 'snap', 'set', 'system', 'refresh.retain='+revs],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                check=True
            )
        except CalledProcessError:
            print(subproc.CalledProcessError)

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
        app.set_metered_status(self.connection, state)

    def on_timer_apply_clicked(self, *args):
        input_obj = app.builder.get_object('timer_entry')
        suggested_obj = app.builder.get_object('timer_suggested')
        if input_obj.get_text():
            input = input_obj.get_text()
        else:
            input = suggested_obj.get_text()
            input_obj.set_text(input)
        app.set_refresh_timer(input)

    def on_revs_kept_value_changed(self, *args):
        entry = app.builder.get_object('revs_kept')
        revs = entry.get_text()
        app.set_revisions_kept(revs)


app = SettingsApp()
