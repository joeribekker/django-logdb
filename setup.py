from setuptools import setup, find_packages

import djangologdb

setup(
    name='django-logdb',
    version='.'.join(map(str, djangologdb.__version__)),
    description='Django-logdb enables you to log entries to a database and aggregate them periodically.',
    author='Joeri Bekker',
    author_email='joeri@maykinmedia.nl',
    license='BSD',
    platforms = ['any'],
    url='http://github.com/joeribekker/django-logdb',
    install_requires=[
        'Django>=1.1',
        'django-picklefield>=0.1',
    ],
    include_package_data = True,
    packages=find_packages(),
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
