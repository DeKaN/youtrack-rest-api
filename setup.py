from setuptools import setup

from youtrack import __version__, __author__

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='youtrack-rest-api',
    version=__version__,
    packages=['youtrack'],
    url='https://github.com/DeKaN/youtrack-rest-api',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    license='Apache 2.0',
    author=__author__,
    author_email='dekanszn@gmail.com',
    description='YouTrack JSON REST API Python 3 Client Library',
    long_description=readme,
    install_requires=[
        'requests>=2.13.0'
    ]
)
