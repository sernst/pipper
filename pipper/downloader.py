import os

import requests

from pipper import environment
from pipper import info
from pipper import versioning
from pipper import wrapper
from pipper.environment import Environment


def parse_package_id(env: Environment, package_id: str) -> dict:
    """ 
    Parses a package id into its constituent name and version information. If
    the version is not specified as part of the identifier, a version will
    be determined. If the package is already installed and the upgrade flag is
    not set in the environment arguments, the current local version will be
    used. If the package is not installed or the upgrade flag is set, the 
    remote version will be used.

    :param env:
        Command environment in which this function is being executed
    :param package_id:
        Identifier for the package to be loaded. This can be either a package
        name, or a package name and version (NAME:VERSION) combination.

    :return:
        A dictionary containing installation information for the specified
        package. The dictionary has the following fields:
            - name: Name of the package
            - version: SemVer package version
            - bucket: Name of the S3 bucket where the remote page resides
            - key: S3 key for the remote pipper file where the specified 
                    package name and version reside
    """

    package_parts = package_id.split(':')
    name = package_parts[0]
    upgrade = env.args.get('upgrade')

    def possible_versions():
        yield package_parts[1] if len(package_parts) > 1 else None
        if not upgrade:
            existing = wrapper.status(name)
            yield existing.version if existing else None
        yield info.list_remote_version_info(env, package_id)[-1]['version']

    version = next(v for v in possible_versions() if v is not None)

    return dict(
        name=name,
        version=version,
        bucket=env.args.get('bucket'),
        key=versioning.make_s3_key(name, version)
    )


def save(url: str, local_path: str) -> str:
    """ 
    """

    response = requests.get(url)
    with open(local_path, 'wb') as f:

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return local_path


def download_package(env: Environment, package_id: str) -> str:
    """ 
    """

    data = parse_package_id(env, package_id)
    directory = os.path.realpath(env.args.get('save_directory') or '.')
    path = os.path.join(directory, '{}-{}.pipper'.format(
        data['name'],
        data['version']
    ))

    env.s3_client.download_file(
        Bucket=data['bucket'],
        Key=data['key'],
        Filename=path
    )

    print('[DOWNLOADED]: {} -> {}'.format(data['name'], path))

    return path


def download_many(env: Environment, package_ids: list) -> dict:
    """ 
    """

    return {pid: download_package(env, pid) for pid in package_ids}


def download_from_configs(env: Environment, configs_path: str = None) -> dict:
    """ 
    """

    configs = environment.load_configs(configs_path)
    return download_many(env, configs.get('dependencies') or [])


def run(env: Environment):
    """ 
    """

    package_ids = env.args.get('packages')
    if not package_ids:
        return download_from_configs(env, env.args.get('configs_path'))

    return download_many(env, package_ids)
