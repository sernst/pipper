import typing
from pipper import wrapper


def install(package: str):
    """ 
    Installs the specified pipper package, which is specified by either a
    url or a path to a wheel file.
    """

    if package.startswith(('http://', 'https://')):
        if wrapper.update_required(package):
            print('[INSTALLING]: "{}"'.format(package))
            return wrapper.install_wheel(package)

        data = wrapper.parse_url(package)
        print('[SKIPPED]: "{}" version {} already installed'.format(
            data['package_name'],
            data['version'].replace('-', '.')
        ))
        return None

    return None


def install_many(packages: typing.List[str]):
    """ """

    return [install(p) for p in packages]


def install_from_args(**kwargs):
    """ """
