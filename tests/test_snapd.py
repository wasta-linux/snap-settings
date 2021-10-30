import os
import unittest

from snapsettings import snapd


class Snapd(unittest.TestCase):
    def setUp(self):
        self.snap = snapd.Snap()

    def tearDown(self):
        pass

    def test_get(self):
        result = self.snap.get('connections').get('result')
        self.assertTrue(isinstance(result, dict))

    def test_get_refresh_list(self):
        refresh_list = self.snap.get_refresh_list()
        self.assertTrue(refresh_list)

    def test_get_refresh_config(self):
        result = self.snap.get('system', 'refresh').get('result')
        refresh_config = result.get('refresh')
        self.assertTrue(refresh_config)

    def test_get_refresh_metered(self):
        refresh_metered = self.snap.get('system', 'refresh.metered').get('result')
        self.assertTrue(refresh_metered)

    def test_get_refresh_time(self):
        refresh_time = self.snap.get_refresh_time()
        self.assertTrue(refresh_time)

    def test_get_refresh_timer(self):
        refresh_config = self.snap.get('system', 'refresh.timer').get('result')
        self.assertTrue(refresh_config)

    def test_list(self):
        snap_list = self.snap.list()
        self.assertTrue(len(snap_list)>0)

    def test_info_installed(self):
        info = self.snap.info('snapd')
        self.assertTrue(info.get('id'))

    def test_info_not_installed(self):
        info = self.snap.info('hillbilly')
        self.assertEqual(info.get('message'), 'snap not installed')


if __name__ == '__main__':
    unittest.main()
