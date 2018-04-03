import typing
import pkg_resources

import semver

from pipper.environment import Environment


class RemoteVersion(object):
    """
    Data structure for storing information about remote data sources
    """

    def __init__(self, bucket: str, key: str):
        """_ doc..."""
        self._key = key
        self._bucket = bucket

    @property
    def key(self) -> str:
        return self._key

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def package_name(self) -> str:
        return self._key.strip('/').split('/')[1]

    @property
    def filename(self) -> str:
        return self.key.rsplit('/', 1)[-1]

    @property
    def version(self) -> str:
        return deserialize(self.key.rsplit('/', 1)[-1].rsplit('.', 1)[0])

    @property
    def safe_version(self) -> str:
        return self.key.rsplit('/', 1)[-1].rsplit('.', 1)[0]

    def __lt__(self, other):
        return semver.compare(self.version, other.version) < 0

    def __le__(self, other):
        return semver.compare(self.version, other.version) != 1

    def __gt__(self, other):
        return semver.compare(self.version, other.version) > 0

    def __ge__(self, other):
        return semver.compare(self.version, other.version) != -1

    def __eq__(self, other):
        return semver.compare(self.version, other.version) == 0

    def __repr__(self):
        return '<{} {}:{}>'.format(
            self.__class__.__name__,
            self.package_name,
            self.version
        )


def serialize(version: str) -> str:
    """ """
    try:
        info = semver.parse_version_info(version)
    except ValueError:
        raise ValueError('Invalid semantic version "{}"'.format(version))

    pre = info.prerelease.replace('.', '_') if info.prerelease else None
    build = info.build.replace('.', '_') if info.build else None

    return 'v{}-{}-{}{}{}'.format(
        info.major,
        info.minor,
        info.patch,
        '-p-{}'.format(pre) if pre else '',
        '-b-{}'.format(build) if build else ''
    )


def deserialize(version: str) -> str:
    """ """
    return (
        version
        .lstrip('v')
        .replace('-', '.', 2)
        .replace('-p-', '-')
        .replace('-b-', '+')
    )


def make_s3_key(package_name: str, package_version: str) -> str:
    """ """

    safe_version = (
        serialize(package_version)
        if not package_version.startswith('v') else
        package_version
    )

    return 'pipper/{}/{}.pipper'.format(package_name, safe_version)


def parse_s3_key(key: str) -> dict:
    """ """

    parts = key.strip('/').split('/')
    safe_version = parts[2].rsplit('.', 1)[0]

    return dict(
        name=parts[1],
        safe_version=safe_version,
        version=deserialize(safe_version)
    )


def list_versions(
        environment: Environment,
        package_name: str,
        version_prefix: str = None
) -> typing.List[RemoteVersion]:
    """..."""
    client = environment.aws_session.client('s3')
    prefix = (
        (version_prefix or '')
        .lstrip('v')
        .replace('.', '-')
        .split('*')[0]
    )
    key_prefix = 'pipper/{}/v{}'.format(package_name, prefix)

    responses = []
    while not responses or responses[-1].get('NextContinuationToken'):
        continuation_kwargs = (
            {'ContinuationToken': responses[-1].get('NextContinuationToken')}
            if responses else
            {}
        )
        responses.append(client.list_objects_v2(
            Bucket=environment.bucket,
            Prefix=key_prefix,
            **continuation_kwargs
        ))

    results = [
        RemoteVersion(key=entry['Key'], bucket=environment.bucket)
        for response in responses
        for entry in response.get('Contents')
        if entry['Key'].endswith('.pipper')
    ]

    return sorted(results)


def compare_constraint(version: str, constraint: str) -> int:
    """Returns comparison between versions"""
    if version == constraint:
        return 0

    version_parts = version.split('.')
    constraint_parts = constraint.split('.')

    def compare_part(a: str, b: str) -> int:
        if a == b or a == '*' or b == '*':
            return 0
        return -1 if int(a) < int(b) else 1

    comparisons = [
        compare_part(v, c)
        for v, c in zip(version_parts, constraint_parts)
    ]

    return next((c for c in comparisons if c != 0), 0)


def find_latest_match(
        environment: Environment,
        package_name: str,
        version_constraint: str = None
) -> typing.Union[RemoteVersion, None]:
    """..."""

    available = list_versions(environment, package_name)
    available.reverse()

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
