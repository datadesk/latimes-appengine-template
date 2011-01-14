from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os
import sys

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
len_root_dir = len(root_dir)
django_dir = os.path.join(root_dir, 'django')

for dirpath, dirnames, filenames in os.walk(django_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        package = dirpath[len_root_dir:].lstrip('/').replace('/', '.')
        packages.append(package)
    else:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Small hack for working with bdist_wininst.
# See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
    for file_info in data_files:
        file_info[0] = '/PURELIB/%s' % file_info[0]

setup(
    name = "Django",
    version = "0.96.4",
    url = 'http://www.djangoproject.com/',
    author = 'Django Software Foundation',
    author_email = 'foundation@djangoproject.com',
    download_url = 'http://media.djangoproject.com/releases/0.96/Django-0.96.4.tar.gz',
    description = 'A high-level Python Web framework that encourages rapid development and clean, pragmatic design.',
    packages = packages,
    data_files = data_files,
    scripts = ['django/bin/django-admin.py'],
)
