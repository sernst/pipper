import pip
import pkg_resources
import semver

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


def install_wheel(wheel_path: str):
    """ """

    pip.main(['install', wheel_path])
