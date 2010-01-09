from setuptools import setup, find_packages

import djangologdb

setup(
    name='django-logdb',
    version='.'.join(map(str, djangologdb.__version__)),
    description='Django-logdb enables you to log entries to a database and aggregate them periodically.',
    author='Joeri Bekker',
    author_email='joeri@maykinmedia.nl',
    license="BSD",
    #url='http://github.com/dcramer/django-db-log',
    install_requires=[
        'Django>=1.1',
        'django-picklefield>=0.1',
    ],
    packages=find_packages(),
    include_package_data=True,
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
