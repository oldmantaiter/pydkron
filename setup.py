import os
import re
import sys

from setuptools import setup, find_packages


if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

with open(os.path.join(os.path.dirname(__file__), 'pydkron', '__init__.py')) as f:
    VERSION = re.search("__version__ = '([^']+)'", f.read()).group(1)

INSTALL_REQUIRES = [
    'requests',
    'six'
]

setup(
    name='pydkron',
    version=VERSION,
    description='pydkron: Python Client for Dkron',
    keywords='dkron',
    author='Tait Clarridge',
    author_email='tait@clarridge.ca',
    url='https://github.com/oldmantaiter/pydkron',
    download_url='https://github.com/oldmantaiter/pydkron/archive/'+VERSION+'.tar.gz',
    license='MIT License',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)
