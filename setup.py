from ez_setup import use_setuptools
use_setuptools()

import os
from setuptools import setup, find_packages

import djangologdb

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

readme = read_file('README.rst')
changes = read_file('CHANGES.rst')

setup(
    name='django-logdb',
    version='.'.join(map(str, djangologdb.__version__)),
    description='Django-logdb enables you to log entries to a database and aggregate them periodically.',
    long_description='\n\n'.join([readme, changes]),
    author='Joeri Bekker',
    author_email='joeri@maykinmedia.nl',
    license='MIT',
    platforms=['any'],
    url='http://github.com/joeribekker/django-logdb',
    #install_requires=[
    #    'Django>=1.1',
    #],
    include_package_data=True,
    packages=['djangologdb'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    zip_safe=False,
)
