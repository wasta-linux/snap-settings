# https://docs.python.org/3/distutils/setupscript.html

import glob
from setuptools import setup

setup(
    name='Snap Settings',
    version=0.1,
    description="Set basic snap settings in a user-friendly window.",
    author="Nate Marti",
    author_email="nate_marti@sil.org",
    url="https://github.com/wasta-linux/snap-settings",
    packages=['snapsettings'],
    package_data={
        'snapsettings': [
            'README.md',
            'data/ui/*.glade',
        ],
    },
    scripts=['bin/basic-snap-settings'],
    data_files=[
        ('share/polkit-1/actions', glob.glob('data/actions/*')),
        ('share/icons/hicolor/scalable/apps', glob.glob('data/icons/*.svg')),
        ('share/basic-snap-sesttings/ui', glob.glob('data/ui/*.glade')),
        ('share/applications', glob.glob('data/*.desktop')),
    ],
)
