import pytest

from pipper.versioning import serde


checks = [
    ('0.0.1', ('0', '0', '1', '', '')),
    ('0.1.12+build.1', ('0', '1', '12', '', 'build.1')),
    ('0.1.*-beta.4', ('0', '1', '*', 'beta.4', '')),
    ('1.*.*-beta.4+build.12', ('1', '*', '*', 'beta.4', 'build.12')),
    ('1.12-beta.4', ('1', '12', '', 'beta.4', ''))
]


@pytest.mark.parametrize('version,expected', checks)
def test_explode(version, expected):
    """..."""
    observed = serde.explode(version)
    assert expected == observed

