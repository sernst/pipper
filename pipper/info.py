import typing
import textwrap
import functools

import semver

from pipper import wrapper
from pipper import versioning
from pipper.environment import Environment


def list_remote_package_keys(
        env: Environment,
        package_name: str
) -> typing.List[str]:
    """ """

    remote_keys = []
    continuation_token = None

    for i in range(1000):
        list_kwargs = dict(
            Bucket=env.bucket,
            Prefix='pipper/{}'.format(package_name)
        )

        if continuation_token:
            list_kwargs['ContinuationToken'] = continuation_token

        response = env.s3_client.list_objects_v2(**list_kwargs)

        remote_keys += [item['Key'] for item in response['Contents']]
        if not response['IsTruncated']:
            break

        continuation_token = response['NextContinuationToken']

    return [key for key in remote_keys if key.endswith('.pipper')]


def list_remote_version_info(env: Environment, package_name: str) -> list:
    """ """

    def from_key(key: str) -> dict:
        filename = key.strip('/').split('/')[-1]
        safe_version = filename.rsplit('.', 1)[0]
        return dict(
            name=package_name,
            safe_version=safe_version,
            version=versioning.deserialize(safe_version)
        )

    versions = [
        from_key(key)
        for key in list_remote_package_keys(env, package_name)
    ]

    def compare_versions(a: dict, b: dict) -> int:
        return semver.compare(a['version'], b['version'])

    return sorted(versions, key=functools.cmp_to_key(compare_versions))


def get_package_metadata(
        env: Environment,
        package_name: str,
        package_version: str
):
    """ """

    response = env.s3_client.head_object(
        Bucket=env.bucket,
        Key=versioning.make_s3_key(package_name, package_version)
    )

    return {key: value for key, value in response['Metadata'].items()}


def print_local_only(package_name: str):
    """ """

    print('[PACKAGE]: {}'.format(package_name))

    local_data = wrapper.status(package_name)
    if local_data is None:
        print('[MISSING]: The package is not installed locally')
        return

    print('[EXISTS]: Installed version is {}'.format(
        package_name,
        local_data.version
    ))


def print_with_remote(env: Environment, package_name: str):
    """ """

    remote_versions = list_remote_version_info(env, package_name)
    latest = get_package_metadata(
        env,
        package_name,
        remote_versions[-1]['version']
    )

    local_data = wrapper.status(package_name)
    comparison = (
        0
        if local_data is None else
        semver.compare(local_data.version, latest['version'])
    )

    if local_data is None:
        message = '[MISSING]: The package is not installed locally'
    elif comparison < 0:
        message = '[BEHIND]: local {} version is older than {}'.format(
            local_data.version,
            latest['version']
        )
    elif comparison > 0:
        message = '[AHEAD]: Local version is newer than the released version'
    else:
        message = '[CURRENT]: The most recent version is already installed'

    print(textwrap.dedent(
        """
        [PACKAGE]: {name}
        
           * Latest version: {version}
           * Uploaded at: {timestamp}
           
        {message}        
        """.format(
            name=package_name,
            version=latest['version'],
            timestamp=latest['timestamp'],
            message=message
        )
    ))


def run(env: Environment):
    """ """

    local_only = env.args.get('local_only')
    package_name = env.args.get('package_name')

    if local_only:
        return print_local_only(package_name)

    return print_with_remote(env, package_name)

