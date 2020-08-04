from pipper import versioning
import pytest

comparisons = [
    ('0.0.1', '0.0.1', 0),
    ('0.0.1', '0.0.2', -1),
    ('0.0.1', '0.0.1-alpha.1', -1),
    ('0.0.1', '0.0.1-alpha.1+build.2', -1),
    ('0.0.1', '0.0.*', 0)
]


@pytest.mark.parametrize('version,constraint,expected', comparisons)
def test_compare_constraint(version, constraint, expected):
    """Should correctly compare between two versions"""
    result = versioning.compare_constraint(version, constraint)
    assert expected == result, """
        Expect comparison of "{version}" with "{constraint}" to produce
        a {expected} result instead of a {result} result.
        """.format(
            version=version,
            constraint=constraint,
            expected=expected,
            result=result
        )
