import os

from setuptools import find_packages
from setuptools import setup

setup(
    name='hello_pipper',
    version='0.0.0',
    description='A hello world pipper library for testing.',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'pip',
        'requests',
        'wheel',
        'setuptools',
        'semver',
        'boto3'
    ],
)
