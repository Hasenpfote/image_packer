#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from setuptools import setup, find_packages


# Get version without importing, which avoids dependency issues
def get_version():
    with open('image_packer/version.py') as version_file:
        return re.search(r"""__version__\s+=\s+(['"])(?P<version>.+?)\1""",
                         version_file.read()).group('version')


def _long_description():
    with open('README.rst', 'r') as f:
        return f.read()


def exclude_packages(names):
    packages = list()
    for name in names:
        for pattern in ('{}', '{}.*', '*.{}', '*.{}.*'):
            packages.append(pattern.format(name))
    return packages


required = [
    'Pillow>=5.0.0',
]


if __name__ == '__main__':
    setup(
        name='image_packer',
        version=get_version(),
        description='Pack multiple images of different sizes or formats into one image.',
        long_description=_long_description(),
        author='Hasenpfote',
        author_email='Hasenpfote36@gmail.com',
        url='https://github.com/Hasenpfote/',
        download_url='',
        packages=find_packages(exclude=exclude_packages(names=('test', 'tests'))),
        keywords=['packing', 'rectangle-packing'],
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Development Status :: 5 - Production/Stable',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        python_requires='>=3.4',
        install_requires=required,
        entry_points={
            'console_scripts': [
                'impack=image_packer.cli.pack:main'
            ],
        }
    )
