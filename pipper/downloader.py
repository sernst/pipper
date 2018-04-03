import os
import json
import zipfile
import shutil
from urllib.parse import urlparse
from contextlib import closing

import requests
from pipper import environment
from pipper import info
from pipper import versioning
from pipper import wrapper
from pipper.environment import Environment


def parse_package_url(package_url: str) -> dict:
    """ """

    url_data = urlparse(package_url)
    parts = url_data.path.strip('/').split('/')
    filename = parts[-1]
    safe_version = filename.rsplit('.', 1)[0]

    return dict(
        url=package_url,
        bucket=parts[0],
        name=parts[-2],
        safe_version=safe_version,
        version=versioning.deserialize(safe_version),
        key='/'.join(parts[1:])
    )


def parse_package_id(
        env: Environment,
        package_id: str,
        use_latest_version: bool = False
) -> dict:
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
    :param use_latest_version:
        Whether or not to use the latest version.
    :return:
        A dictionary containing installation information for the specified
        package. The dictionary has the following fields:
            - name: Name of the package
            - version: SemVer package version
            - bucket: Name of the S3 bucket where the remote page resides
            - key: S3 key for the remote pipper file where the specified 
                    package name and version reside
    """

    if package_id.startswith('https://'):
        return parse_package_url(package_id)

    package_parts = package_id.split(':')
    name = package_parts[0]
    upgrade = use_latest_version or env.args.get('upgrade')

    def possible_versions():
        yield (
            versioning.find_latest_match(env, *package_parts).version
            if len(package_parts) > 1 else
            None
        )
        if not upgrade:
            existing = wrapper.status(name)
            yield existing.version if existing else None
        yield versioning.find_latest_match(env, name).version

    try:
        version = next((v for v in possible_versions() if v is not None))
    except IndexError:
        print('[ERROR]: Unable to acquire version of "{}"'.format(package_id))
        raise

    print('[PACKAGE]:', package_id, version)

    return dict(
        name=name,
        version=version,
        bucket=env.bucket,
        key=versioning.make_s3_key(name, version)
    )


def save(url: str, local_path: str) -> str:
    """ 
    """

    with closing(requests.get(url, stream=True)) as response:
        if response.status_code != 200:
            print((
                '[ERROR]: Unable to download remote package. Has your'
                'authorized URL expired? Is there internet connectivity?'
            ))

        with open(local_path, 'wb') as f:
            for chunk in response:
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())

    return local_path


def extract_pipper_file(
        local_bundle_path: str,
        extract_directory: str = None
) -> dict:
    """ """

    directory = extract_directory or os.path.dirname(local_bundle_path)

    with zipfile.ZipFile(local_bundle_path, 'r') as zipper:
        contents = zipper.read('package.meta')

    metadata = json.loads(contents)
    wheel_path = os.path.join(directory, metadata['wheel_name'])
    metadata_path = os.path.join(
        directory,
        '{}.meta.json'.format(metadata['wheel_name'])
    )

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

    with zipfile.ZipFile(local_bundle_path, 'r') as zipper:
        zipper.extract('package.whl', directory)
        shutil.move(os.path.join(directory, 'package.whl'), wheel_path)

    return dict(
        meta_path=metadata_path,
        wheel_path=wheel_path,
        metadata=metadata,
        bundle_path=local_bundle_path
    )


def download_package(env: Environment, package_id: str) -> str:
    """ 
    """

    data = parse_package_id(env, package_id)
    directory = os.path.realpath(env.args.get('save_directory') or '.')
    path = os.path.join(directory, '{}-{}.pipper'.format(
        data['name'],
        data['version']
    ))

    if not os.path.exists(directory):
        os.makedirs(directory)

    if 'url' in data:
        save(package_id, path)
    else:
        env.s3_client.download_file(
            Bucket=data['bucket'],
            Key=data['key'],
            Filename=path
        )

    print('[DOWNLOADED]: {} -> {}'.format(data['name'], path))

    if env.args.get('extract'):
        paths = extract_pipper_file(path, directory)
        print(
            '[EXTRACTED]:',
            '\n  *', paths['wheel_path'],
            '\n  *', paths['meta_path']
        )

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
