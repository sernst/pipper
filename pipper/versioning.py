import typing

import semver

from pipper import s3
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
    """
    Converts the specified semantic version into a URL/filesystem safe
    version. If the version argument is not a valid semantic version a
    ValueError will be raised.
    """
    try:
        semver.parse_version_info(version)
    except ValueError:
        raise ValueError('Invalid semantic version "{}"'.format(version))

    return serialize_prefix(version)


def serialize_prefix(version_prefix: str) -> str:
    """
    Serializes the specified prefix into a URL/filesystem safe version that
    can be used as a filename to store the versioned bundle.

    :param version_prefix:
        A partial or complete semantic version to be converted into its
        URL/filesystem equivalent.
    """
    if version_prefix.startswith('v'):
        return version_prefix

    searches = [
        ('+', 'split'),
        ('-', 'split'),
        ('.', 'rsplit'),
        ('.', 'rsplit')
    ]

    sections = []
    remainder = version_prefix.rstrip('.')
    for separator, operation in searches:
        parts = getattr(remainder, operation)(separator, 1)
        remainder = parts[0]
        section = parts[1] if len(parts) == 2 else ''
        sections.insert(0, section.replace('.', '_'))
    sections.insert(0, remainder)

    prefix = '-'.join([section for section in sections[:3] if section])
    if sections[3]:
        prefix += '__pre_{}'.format(sections[3])
    if sections[4]:
        prefix += '__build_{}'.format(sections[4])

    return 'v{}'.format(prefix) if prefix else ''


def deserialize_prefix(safe_version_prefix: str) -> str:
    """
    Deserializes the specified prefix from a URL/filesystem safe version into
    its standard semantic version equivalent.

    :param safe_version_prefix:
        A partial or complete URL/filesystem safe version prefix to convert
        into a standard semantic version prefix.
    """
    if not safe_version_prefix.startswith('v'):
        return safe_version_prefix

    searches = [
        ('__build_', 'split'),
        ('__pre_', 'split'),
        ('-', 'rsplit'),
        ('-', 'rsplit')
    ]

    sections = []
    remainder = safe_version_prefix.strip('v').rstrip('_')
    for separator, operator in searches:
        parts = getattr(remainder, operator)(separator, 1)
        remainder = parts[0]
        section = parts[1] if len(parts) == 2 else ''
        sections.insert(0, section.replace('_', '.'))
    sections.insert(0, remainder)

    prefix = '.'.join([section for section in sections[:3] if section])
    if sections[3]:
        prefix += '-{}'.format(sections[3])
    if sections[4]:
        prefix += '+{}'.format(sections[4])

    return prefix


def deserialize(safe_version: str) -> str:
    """
    Converts the specified URL/filesystem safe version into a standard semantic
    version. If the converted output is not a valid semantic version a
    ValueError will be raised.
    """
    result = deserialize_prefix(safe_version)

    try:
        semver.parse_version_info(result)
    except ValueError:
        raise ValueError('Invalid semantic version "{}"'.format(result))

    return result


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
