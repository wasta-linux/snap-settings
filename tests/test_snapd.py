import os
import unittest
import warnings

from snapsettings import snapd


class API(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
        self.snap = snapd.Snap()

    def tearDown(self):
        pass

    def test_get_snap_refresh(self):
        refresh_config = self.snap.get('system', 'refresh')
        self.assertTrue(refresh_config)

    def test_get_snap_refresh_metered(self):
        refresh_config = self.snap.get('system', 'refresh.metered')
        self.assertTrue(refresh_config)

    def test_get_snap_refresh_time(self):
        refresh_time = self.snap.get_refresh_time()
        self.assertTrue(refresh_time)

    def test_get_snap_refresh_timer(self):
        refresh_config = self.snap.get('system', 'refresh.timer')
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

    def test_get_refresh_list(self):
        refresh_list = self.snap.get_refresh_list()
        self.assertTrue(refresh_list)


if __name__ == '__main__':
    unittest.main()
