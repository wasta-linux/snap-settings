import os
import unittest

from snapsettings import app


class App(unittest.TestCase):
    def setUp(self):
        self.app = app.SettingsApp()

    def tearDown(self):
        pass

    def test_get_refresh_config(self):
        refresh_config = self.app.get_refresh_config()
        self.assertTrue(len(refresh_config) == 2)

    def test_get_refresh_timer(self):
        refresh_timer = self.app.get_refresh_timer_info()
        self.assertTrue(len(refresh_timer) == 3)


if __name__ == '__main__':
    unittest.main()
