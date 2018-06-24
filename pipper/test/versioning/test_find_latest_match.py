from unittest import patch
from unittest import MagicMock

import pytest

from pipper import versioning


listed_versions = [
    versioning.to_remote_version('test', '0.0.1', 'FAKE'),
    versioning.to_remote_version('test', '0.0.2', 'FAKE'),
    versioning.to_remote_version('test', '0.1.0', 'FAKE'),
    versioning.to_remote_version('test', '0.1.1', 'FAKE'),
    versioning.to_remote_version('test', '1.0.0', 'FAKE')
]

validations = [
    ('0.0.1', '0.0.1'),
    ('0.0.*', '0.0.2'),
    ('0.*', '0.1.1'),
    ('*', '1.0.0')
]


@pytest.mark.parameterize('constraint,expected', validations)
@patch('pipper.versioning.list_versions')
def test_find_latest_match(list_versions: MagicMock, constraint: str, expected: str):
    """Should find correct latest match for given constraint"""
    list_versions.return_value = listed_versions
    result = versioning.find_latest_match(MagicMock(), 'test', constraint)
    assert expected == result.version
