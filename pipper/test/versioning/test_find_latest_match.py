from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pipper import versioning

listed_versions = list(reversed([
    versioning.to_remote_version('test', '0.0.1', 'FAKE'),
    versioning.to_remote_version('test', '0.0.1-alpha.1', 'FAKE'),
    versioning.to_remote_version('test', '0.0.1-alpha.2', 'FAKE'),
    versioning.to_remote_version('test', '0.0.1-alpha.2+build.122', 'FAKE'),
    versioning.to_remote_version('test', '0.0.1-alpha.2+build.123', 'FAKE'),
    versioning.to_remote_version('test', '0.0.2', 'FAKE'),
    versioning.to_remote_version('test', '0.1.0', 'FAKE'),
    versioning.to_remote_version('test', '0.1.1', 'FAKE'),
    versioning.to_remote_version('test', '1.0.0', 'FAKE'),
    versioning.to_remote_version('test', '2.0.0-alpha.1', 'FAKE'),
    versioning.to_remote_version('test', '2.0.0-alpha.2', 'FAKE'),
    versioning.to_remote_version('test', '2.0.0-beta.1', 'FAKE'),
    versioning.to_remote_version('test', '2.0.0-beta.2', 'FAKE'),
    versioning.to_remote_version('test', '2.0.0-rc.1+build.2', 'FAKE'),
    versioning.to_remote_version('test', '2.0.0-rc.1+build.3', 'FAKE')
]))

validations = [
    ('=0.0.1', False, '0.0.1'),
    ('=0.0.1', True, '0.0.1-alpha.2+build.123'),
    ('=0.0.1+build.122', True, '0.0.1-alpha.2+build.122'),
    ('<0.0.1+build.123', True, '0.0.1-alpha.2+build.122'),
    ('=0.0.1-alpha.1', True, '0.0.1-alpha.1'),
    ('<0.0.2', False, '0.0.1'),
    ('<=0.0.2', False, '0.0.2'),
    ('=0.0.*', False, '0.0.2'),
    ('=0.*', False, '0.1.1'),
    ('=*', False, '1.0.0'),
    ('=*', True, '2.0.0-rc.1+build.3'),
    ('>0.1.1', False, '1.0.0'),
    ('>=1.0.0', False, '1.0.0'),
    ('', False, '1.0.0'),
    ('', True, '2.0.0-rc.1+build.3'),
]


@pytest.mark.parametrize('constraint,unstable,expected', validations)
@patch('pipper.versioning.list_versions')
def test_find_latest_match(
        list_versions: MagicMock,
        constraint: str,
        expected: str,
        unstable: bool
):
    """Should find correct latest match for given constraint"""
    list_versions.return_value = [
        v for v in listed_versions
        if not v.is_prerelease or unstable
    ]

    result = versioning.find_latest_match(
        environment=MagicMock(),
        package_name='test',
        version_constraint=constraint,
        include_prereleases=unstable
    )
    assert expected == result.version
