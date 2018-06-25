import typing
from urllib.parse import urlparse

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


def parse_package_url(package_url: str) -> RemoteVersion:
    """
    Parses a standard S3 URL of the format:

    `https://s3.amazonaws.com/bucket-name/pipper/package-name/v0-0-18.pipper`

    into a RemoteVersion object.
    """
    url_data = urlparse(package_url)
    parts = url_data.path.strip('/').split('/', 1)
    return RemoteVersion(bucket=parts[0], key=parts[1], url=package_url)


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
        include_prereleases: bool = False,
        reverse: bool = False
) -> typing.List[RemoteVersion]:
    """
    Lists the available versions of the specified package by querying the
    remote S3 storage and returns those as keys. The results are sorted in
    order of increasing version unless `reverse` is True in which case the
    returned list is sorted from highest version to lowest one.

    By default, only stable releases are returned, but pre-releases can be
    included as well if the `include_prereleases` argument is set to True.

    :param environment:
        Context object for the currently running command invocation.
    :param package_name:
        Name of the pipper package to list versions of.
    :param version_prefix:
        A constraining version prefix, which may include wildcard characters.
        Constraints are hierarchical, which means satisfying the highest
        level constraint automatically satisfies the subsequent ones.
        Therefore, a constraint like `1.*.4` would ignore the `4` patch value.
    :param reverse:
        Whether or not to reverse the order of the returned results.
    :param include_prereleases:
        Whether or not to include pre-release versions in the results.
    """
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

    return [
        r for r in sorted(results, reverse=reverse)
        if not r.is_prerelease or include_prereleases
    ]


def compare_constraint(version: str, constraint: str) -> int:
    """
    Returns an integer representing the sortable comparison between two
    versions using standard sorting values:
        -1 (version is less than constraint)
        0 (version is equal to constraint)
        1 (version is greater than constraint)
    The use-case is to compare a version against a version
    constraint to determine how the version satisfies the constraint.
    """
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

        a = ''.join([x.zfill(32) for x in v.split('.')])
        b = ''.join([x.zfill(32) for x in c.split('.')])
        items = sorted([a, b])
        return -1 if items.index(a) == 0 else 1

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
    """
    Searches through available remote versions of the specified package and
    returns the highest version that satisfies the specified version
    constraint. If no constraint is specified, the highest version available
    is returned. If no match is found, a `None` value is returned instead.

    :param environment:
        Context object for the currently running command invocation.
    :param package_name:
        Name of the pipper package to list versions of.
    :param version_constraint:
        A constraining version or partial version, which may include wildcard
        characters. Constraints are hierarchical, which means satisfying the
        highest level constraint automatically satisfies the subsequent ones.
        Therefore, a constraint like `=1.*.4` would ignore the `4` patch value.
        Constraints should be prefixed by an equality such as `<`, `<=`, `=`,
        `>=` or `>`.
    :param include_prereleases:
        Whether or not to include pre-release versions when looking for a
        match.
    """
    available = list_versions(
        environment=environment,
        package_name=package_name,
        reverse=True,
        include_prereleases=include_prereleases
    )

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
