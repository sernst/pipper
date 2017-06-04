import os
import typing
import tempfile
import shutil
import json
import zipfile

from pipper import wrapper
from pipper import info
from pipper import s3
from pipper import versioning
from pipper.environment import Environment


def parse_package_id(env: Environment, package_id: str):
    """ """

    package_parts = package_id.split(':')
    name = package_parts[0]
    version = (
        package_parts[1]
        if len(package_parts) > 1 else
        info.list_remote_version_info(env, package_id)[-1]['version']
    )

    return dict(
        name=name,
        version=version,
        bucket=env.args.get('bucket'),
        key=versioning.make_s3_key(name, version)
    )


def install(env: Environment, package_id: str):
    """
    Installs the specified pipper package, which is specified by either a
    url or a path to a wheel file.
    """

    data = parse_package_id(env, package_id)

    if not s3.key_exists(env.s3_client, data['bucket'], data['key']):
        print('[ERROR]: Version {} not available for {} package'.format(
            data['version'],
            data['name']
        ))
        return

    if not wrapper.update_required(data['name'], data['version']):
        print('[SKIPPED]: "{}" already installed at version {}'.format(
            data['name'],
            data['version']
        ))
        return

    directory = tempfile.mkdtemp(prefix='pipper-download-')
    path = os.path.join(directory, 'package.pipper')

    env.s3_client.download_file(
        Bucket=data['bucket'],
        Key=data['key'],
        Filename=path
    )

    with zipfile.ZipFile(path, 'r') as zipper:
        contents = zipper.read('package.meta')
    metadata = json.loads(contents)
    wheel_path = os.path.join(directory, metadata['wheel_name'])

    with zipfile.ZipFile(path, 'r') as zipper:
        zipper.extract('package.whl', directory)
        shutil.copy2(os.path.join(directory, 'package.whl'), wheel_path)

    wrapper.install_wheel(wheel_path)
    print(directory)
    shutil.rmtree(directory)


def install_many(env: Environment, packages: typing.List[str]):
    """ """

    return [install(env, p) for p in packages]


def run(env: Environment):
    """ """

    packages = env.args.get('packages')
    if packages:
        return install_many(env, packages)
