import os
import json
import glob
from setuptools import setup
from setuptools import find_packages

# python3 setup.py register -r pypitest

# UNIX:
# rm -rf ./dist
# python3 setup.py sdist bdist_wheel
# twine upload dist/pipper*
# python3 conda-recipe/conda-builder.py

# WINDOWS:
# rmdir dist /s /q
# python setup.py sdist bdist_wheel
# twine upload dist/pipper*
# python conda-recipe\conda-builder.py

PACKAGE_NAME = 'pipper'
MY_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SETTINGS_PATH = os.path.join(MY_DIRECTORY, PACKAGE_NAME, 'settings.json')

with open(SETTINGS_PATH, 'r') as f:
    settings = json.load(f)


def populate_extra_files():
    """
    Creates a list of non-python data files to include in package distribution
    """
    glob_path = os.path.join(MY_DIRECTORY, PACKAGE_NAME, '**', '*.txt')
    return (
        [SETTINGS_PATH] +
        [e for e in glob.iglob(glob_path, recursive=True)]
    )


setup(
    name=PACKAGE_NAME,
    version=settings['version'],
    description='Private package management on an S3 bucket',
    url='https://github.com/sernst/pipper',
    author='Scott Ernst',
    author_email='swernst@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={'': populate_extra_files()},
    include_package_data=True,
    zip_safe=False,
    entry_points=dict(
        console_scripts=[
            'pipper=pipper.command:run'
        ]
    ),
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
    ]
)
