from unittest.mock import patch
from unittest.mock import MagicMock

import pytest

from pipper import versioning


listed_versions = list(reversed([
    versioning.to_remote_version('test', '0.0.1', 'FAKE'),
    versioning.to_remote_version('test', '0.0.2', 'FAKE'),
    versioning.to_remote_version('test', '0.1.0', 'FAKE'),
    versioning.to_remote_version('test', '0.1.1', 'FAKE'),
    versioning.to_remote_version('test', '1.0.0', 'FAKE')
]))

validations = [
    ('=0.0.1', False, '0.0.1'),
    ('<0.0.2', False, '0.0.1'),
    ('<=0.0.2', False, '0.0.2'),
    ('=0.0.*', False, '0.0.2'),
    ('=0.*', False, '0.1.1'),
    ('=*', False, '1.0.0'),
    ('>0.1.1', False, '1.0.0'),
    ('>=1.0.0', False, '1.0.0'),
    ('', False, '1.0.0'),
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
    list_versions.return_value = listed_versions + []
    result = versioning.find_latest_match(
        environment=MagicMock(),
        package_name='test',
        version_constraint=constraint,
        include_prereleases=unstable
    )
    assert expected == result.version
