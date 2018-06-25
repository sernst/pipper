import typing

from pipper import s3
from pipper.environment import Environment
from pipper.versioning.definitions import RemoteVersion
from pipper.versioning.serde import deserialize
from pipper.versioning.serde import deserialize_prefix
from pipper.versioning.serde import explode
from pipper.versioning.serde import serialize
from pipper.versioning.serde import serialize_prefix


def to_remote_version(
        package_name: str,
        package_version: str,
        bucket: str
) -> RemoteVersion:
    """
    Converts the constituent properties of a pipper remote file into a
    RemoteVersion object.
    """
    return RemoteVersion(
        bucket=bucket,
        key=make_s3_key(package_name, package_version)
    )


def make_s3_key(package_name: str, package_version: str) -> str:
    """
    Converts a package name and version into a fully-qualified S3 key to the
    location where the file resides in the hosting S3 bucket. The package
    version must be a complete semantic version but can be serialized or not.
    """
    safe_version = (
        serialize(package_version)
        if not package_version.startswith('v') else
        package_version
    )
    return 'pipper/{}/{}.pipper'.format(package_name, safe_version)


def list_versions(
        environment: Environment,
        package_name: str,
        version_prefix: str = None,
        reverse: bool = False
) -> typing.List[RemoteVersion]:
    """..."""
    prefix = serialize_prefix(version_prefix or '').split('*')[0]
    key_prefix = 'pipper/{}/v{}'.format(package_name, prefix)

    responses = []
    while not responses or responses[-1].get('NextContinuationToken'):
        continuation_kwargs = (
            {'ContinuationToken': responses[-1].get('NextContinuationToken')}
            if responses else
            {}
        )
        responses.append(s3.list_objects(
            execution_identifier='list_versions',
            s3_client=environment.s3_client,
            bucket=environment.bucket,
            prefix=key_prefix,
            **continuation_kwargs
        ))

    results = [
        RemoteVersion(key=entry['Key'], bucket=environment.bucket)
        for response in responses
        for entry in response.get('Contents')
        if entry['Key'].endswith('.pipper')
    ]

    return sorted(results, reverse=reverse)


def compare_constraint(version: str, constraint: str) -> int:
    """Returns comparison between versions"""
    if version == constraint:
        return 0

    version_parts = explode(version)
    constraint_parts = explode(constraint)

    def compare_part(v: str, c: str) -> int:
        print(version_parts, constraint_parts)
        is_equal = (
            v == c  # direct match
            or '*' in [v, c]  # one is a wildcard
            or c == ''  # no constraint specified
        )
        if is_equal:
            return 0

        if v == '':
            return -1

        v = v.zfill(64)
        c = c.zfill(64)
        items = sorted([v, c])
        return -1 if items.index(v) == 0 else 1

    comparisons = (
        compare_part(v, c)
        for v, c in zip(version_parts, constraint_parts)
    )

    return next((c for c in comparisons if c != 0), 0)


def find_latest_match(
        environment: Environment,
        package_name: str,
        version_constraint: str = None,
        include_prereleases: bool = False
) -> typing.Union[RemoteVersion, None]:
    """..."""
    available = [
        a for a in list_versions(environment, package_name, reverse=True)
        if include_prereleases or not a.is_prerelease
    ]

    if not version_constraint:
        return available[0]

    comparison = version_constraint.strip('=<>')

    if version_constraint.startswith('<='):
        choices = (
            a for a in available
            if compare_constraint(a.version, comparison) != 1
        )
    elif version_constraint.startswith('<'):
        choices = (
            a for a in available
            if compare_constraint(a.version, comparison) < 0
        )
    elif version_constraint.startswith('>='):
        choices = (
            a for a in available
            if compare_constraint(a.version, comparison) != -1
        )
    elif version_constraint.startswith('>'):
        choices = (
            a for a in available
            if compare_constraint(a.version, comparison) > 0
        )
    else:
        choices = (
            a for a in available
            if compare_constraint(a.version, comparison) == 0
        )

    return next(choices, None)
