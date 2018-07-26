import subprocess
import sys

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


def status(package_name: str):
    """ """
    try:
        return pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        return None
    except Exception:
        raise


def install_wheel(wheel_path: str, to_user: bool = False):
    """
    Installs the specified wheel using the pip associated with the
    executing python.
    """
    cmd = [
        sys.executable,
        '-m', 'pip',
        'install', wheel_path
    ]
    cmd += ['--user'] if to_user else []
    print('COMMAND:', ' '.join(cmd))

    result = subprocess.run(cmd)
    result.check_returncode()
