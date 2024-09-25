# https://docs.python.org/3/distutils/setupscript.html

from setuptools import setup
from pathlib import Path

deb_pkg = 'snap-settings'
py3_pkg = 'snapsettings'

# Get version number from debian/changelog.
changelog = Path(__file__).parents[0] / 'debian' / 'changelog'
version = '0.0.0'
with open('snapsettings/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].replace("'", "").strip()

setup(
    name='Snap Settings',
    version=version,
    description="Manage snap system settings for better control over updates.",
    author="Nate Marti",
    author_email="nate_marti@sil.org",
    url=f"https://github.com/wasta-linux/{deb_pkg}",
    packages=[py3_pkg],
    package_data={py3_pkg: ['README.md']},
    scripts=[f"bin/{deb_pkg}"],
    data_files=[
        ('share/polkit-1/actions', [f"data/actions/org.wasta.apps.{deb_pkg}.policy"]),  # noqa: E501
        (f"share/{deb_pkg}/ui", [f"data/ui/{deb_pkg}.glade"]),
        ('share/applications', [f"data/applications/{deb_pkg}.desktop"]),
    ]
)
