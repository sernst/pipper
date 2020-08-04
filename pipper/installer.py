import os
import shutil
import tempfile
import typing

from pipper import downloader
from pipper import environment
from pipper import s3
from pipper import wrapper
from pipper.environment import Environment


def install_pipper_file(
        local_source_path: str,
        to_user: bool = False,
        target_directory: str = None
) -> dict:
    """
    Installs the specified local pipper bundle file.
    
    :param local_source_path:
        An absolute path to the pipper bundle file to install
    :param to_user:
        Whether or not to install the package for the user or not. If not a
        user package, the package will be installed globally.
    :param target_directory:
        Alternate installation location if specified.
    :return
        The package metadata from the pipper bundle
    """
    directory = tempfile.mkdtemp(prefix='pipper-install-')

    try:
        extracted = downloader.extract_pipper_file(
            local_source_path,
            directory
        )
        wrapper.install_wheel(
            wheel_path=extracted['wheel_path'],
            to_user=to_user,
            target_directory=target_directory
        )
        return extracted['metadata']
    except Exception:
        raise
    finally:
        shutil.rmtree(directory)


def install_dependencies(env: Environment, dependencies: typing.List[str]):
    """
    
    :param env:
        Command environment in which this function is being executed
    :param dependencies:
        A list of package identifiers for dependent packages to be loaded. This 
        can be either a package name, or a package name and version 
        (NAME:VERSION) combination, but this version information is ignored for
        dependencies.
    """
    def do_install(package_name: str):
        try:
            data = downloader.parse_package_id(env, package_name)
            existing = wrapper.status(data['name'])
        except Exception:
            existing = wrapper.status(package_name)
        return install(env, package_name) if not existing else None

    for name in dependencies:
        do_install(name)


def install(env: Environment, package_id: str):
    """
    Installs the specified pipper package, which is specified by either a
    url or a path to a wheel file.
    
    :param env:
        Command environment in which this function is being executed
    :param package_id:
        Identifier for the package to be loaded. This can be either a package
        name, or a package name and version (NAME:VERSION) combination.
    """
    upgrade = env.args.get('upgrade')
    data = downloader.parse_package_id(env, package_id)
    is_url = 'url' in data

    if not upgrade and not data['version'] and wrapper.status(data['name']):
        print((
            '[SKIPPED]: "{}" already installed. '
            'Use the upgrade flag or specify a version if you want to '
            'change the installed version.'
        ).format(data['name']))
        return

    if not wrapper.update_required(data['name'], data['version']):
        print('[SKIPPED]: "{}" already installed at version {}'.format(
            data['name'],
            data['version']
        ))
        return

    remote_version_exists = (
        is_url
        or s3.key_exists(env.s3_client, data['bucket'], data['key'])
    )

    if not remote_version_exists:
        print('[ERROR]: Version {} not available for {} package'.format(
            data['version'],
            data['name']
        ))
        return

    directory = tempfile.mkdtemp(prefix='pipper-download-')
    path = os.path.join(directory, 'package.pipper')

    if is_url:
        downloader.save(package_id, path)
    else:
        env.s3_client.download_file(
            Bucket=data['bucket'],
            Key=data['key'],
            Filename=path
        )

    print('DOWNLOAD PATH:', os.path.exists(path), path)

    try:
        metadata = install_pipper_file(
            local_source_path=path,
            to_user=env.args.get('pip_user'),
            target_directory=env.args.get('target_directory')
        )
    except Exception:
        raise
    finally:
        shutil.rmtree(directory)

    dependencies = metadata.get('dependencies') or []
    install_dependencies(env, dependencies)


def install_many(env: Environment, package_ids: typing.List[str]):
    """
    Installs a list of package identifiers, which can be either package names
    or package name and version combinations.
    
    :param env:
        Command environment in which this function is being executed
    :param package_ids:
        A list of package names or package name and version combinations to
        install
    """
    for package_id in (package_ids or []):
        install(env, package_id)


def install_from_configs(env: Environment, configs_path: str = None):
    """
    Installs pipper dependencies specified in a pipper configs file. If the
    path to the configs file is not specified, the default path will be used
    instead. The default location is a pipper.json file in the current
    working directory.
    
    :param env:
        Command environment in which this function is being executed
    :param configs_path:
        Path to a pipper configuration JSON file. If not specified the default
        path will be used instead
    """
    to_user = env.args.get('pip_user')
    target_directory = env.args.get('target_directory')
    configs = environment.load_configs(configs_path)

    for package in configs.get('pypi', []):
        print('\n=== PYPI {} ==='.format(package))
        wrapper.install_pypi(
            package_name=package,
            to_user=to_user,
            target_directory=target_directory
        )

    for package in configs.get('conda', []):
        print('\n=== CONDA {} ==='.format(package))
        wrapper.install_conda(
            package=package,
            to_user=to_user,
            target_directory=target_directory
        )

    return install_many(env, configs.get('dependencies'))


def run(env: Environment):
    """
    Executes an installation command action under the given environmental
    conditions. If a packages argument is specified and contains one or more
    package IDs, they will be installed. If a path to a JSON pipper configs 
    file is specified, that will be installed instead. If nothing has been
    specified, pipper will look for a pipper.json configs file in the current
    directory and use that for installation.
    
    :param env:
        Command environment in which this function is being executed
    """
    packages = env.args.get('packages')
    if packages:
        return install_many(env, packages)

    install_from_configs(env, env.args.get('configs_path'))
