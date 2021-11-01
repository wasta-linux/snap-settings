import os
import unittest

from snapsettings import net


class App(unittest.TestCase):
    def setUp(self):
        # self.app = app.SettingsApp()
        pass

    def tearDown(self):
        pass

    def test_get_connection(self):
        connection = net.get_nmcli_connection()
        self.assertTrue(connection)

    def test_get_metered_status(self):
        # TODO: Verify this with all connection types:
        #   + offline
        #   + wifi
        #   - wired
        #   - ppp
        #   - bluetooth?
        metered_status = net.get_metered_status(net.get_nmcli_connection())
        valid = [
            '0', '1', '2', '3', '4',
            'unknown', 'yes', 'no', 'yes (guessed)', 'no (guessed)'
        ]
        self.assertTrue(metered_status in valid)


if __name__ == '__main__':
    unittest.main()
