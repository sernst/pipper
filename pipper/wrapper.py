import pip
import pkg_resources
import semver

try:
    # Starting with pip10 the `main` function has moved
    # to the `_internal` module.
    from pip import _internal as pip10
except ImportError:
    pip10 = None

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

    result = semver.compare(existing.version, version)
    return result != 0


def status(package_name: str):
    """ """

    try:
        return pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        return None
    except Exception:
        raise


def install_wheel(wheel_path: str, to_user: bool = False):
    """ """

    cmd = ['install', wheel_path]
    cmd += ['--user'] if to_user else []
    print('COMMAND:', ' '.join(cmd))

    # pip 10.0.0 moves the main function. Handle both 9.x and 10
    # cases here for maximum compatibility.
    execution_function = (
        getattr(pip10, 'main', None)
        or getattr(pip, 'main', None)
    )
    execution_function(cmd)
