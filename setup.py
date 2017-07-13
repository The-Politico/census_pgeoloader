import os

from setuptools import setup

REPO_URL = 'https://github.com/The-Politico/census_pgeoloader/'

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="census_pgeoloader",
    version='0.1.0',
    py_modules=['census_pgeoloader'],
    install_requires=[
        'click',
        'psycopg2',
        'requests',
        'us',
    ],
    entry_points='''
        [console_scripts]
        pgeoloader=census_pgeoloader:load
    ''',
    author='Jon McClure',
    author_email='jmcclure@politico.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Sociology',
    ],
)
