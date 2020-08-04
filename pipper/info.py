import typing
import textwrap
import functools

import semver

from pipper import wrapper
from pipper import versioning
from pipper.environment import Environment


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
    remote_versions = versioning.list_versions(env, package_name)

    try:
        latest = get_package_metadata(
            env,
            package_name,
            remote_versions[-1].version
        )
    except IndexError:
        latest = dict(
            version='None',
            timestamp='Never'
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
    """Executes an info command for the specified environment."""
    local_only = env.args.get('local_only')
    package_name = env.args.get('package_name')

    if local_only:
        return print_local_only(package_name)
    return print_with_remote(env, package_name)

