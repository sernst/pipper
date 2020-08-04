import os
import subprocess
import sys
import typing

import pkg_resources

from pipper import versioning


def update_required(package_name: str, install_version: str) -> bool:
    """ """
    existing = status(package_name)

    if not existing:
        return True

    version = (
        versioning.deserialize(install_version)
        if install_version.startswith('v') else
        install_version
    )

    current = pkg_resources.parse_version(existing.version)
    target = pkg_resources.parse_version(version)
    return current != target


def clean_path(path: str) -> str:
    """Returns a fully-qualified absolute path for the source"""
    path = os.path.expanduser(path) if path.startswith('~') else path
    return os.path.realpath(path)


def status(package_name: str):
    """ """
    try:
        return pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        return None
    except Exception:
        raise


def install_wheel(
        wheel_path: str,
        to_user: bool = False,
        target_directory: str = None
):
    """
    Installs the specified wheel using the pip associated with the
    executing python.
    """
    cmd = [
        sys.executable,
        '-m', 'pip',
        'install', wheel_path,
    ]
    cmd += ['--user'] if to_user else []
    cmd += (
        ['--target={}'.format(clean_path(target_directory))]
        if target_directory else
        []
    )
    print('[COMMAND]:\n', ' '.join(cmd).replace(' --', '\n  --'))

    result = subprocess.run(cmd)
    result.check_returncode()


def install_pypi(
        package_name: str,
        to_user: bool = False,
        target_directory: str = None
):
    """
    Installs the specified package from pypi using pip.
    """
    cmd = [
        sys.executable,
        '-m', 'pip',
        'install', package_name,
    ]
    cmd += ['--user'] if to_user else []
    cmd += (
        ['--target={}'.format(clean_path(target_directory))]
        if target_directory else
        []
    )
    print('[COMMAND]:\n', ' '.join(cmd).replace(' --', '\n  --'))

    result = subprocess.run(cmd)
    result.check_returncode()


def install_conda(
        package: typing.Union[str, dict],
        to_user: bool = False,
        target_directory: str = None
):
    """
    Installs the specified package using conda.
    """
    if isinstance(package, dict):
        name = package['name']
        channel = package.get('channel')
    else:
        name = package
        channel = None

    cmd = [
        sys.executable,
        '-m', 'conda',
        'install', name,
    ]
    cmd += ['--channel', channel] if channel else []
    cmd += ['--user'] if to_user else []
    cmd += (
        ['--prefix={}'.format(clean_path(target_directory))]
        if target_directory else
        []
    )
    print('[COMMAND]:\n', ' '.join(cmd).replace(' --', '\n  --'))

    result = subprocess.run(cmd)
    result.check_returncode()
