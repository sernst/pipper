import pytest

from pipper import versioning

TEST_PARAMETERS = [
    ('', ''),
    ('1.2', 'v1-2'),
    ('0.4.', 'v0-4'),
    ('1.2.3-alpha-beta.1', 'v1-2-3__pre_alpha-beta_1'),
    ('1.2.3-alpha.1+2-test', 'v1-2-3__pre_alpha_1__build_2-test'),
    ('1.2.3+2-test', 'v1-2-3__build_2-test'),
    ('1.2-2+2-test', 'v1-2__pre_2__build_2-test'),
    ('1+2-test', 'v1__build_2-test'),
]


@pytest.mark.parametrize('source,expected', TEST_PARAMETERS)
def test_serialize_prefix(source: str, expected: str):
    """Should serialize the source prefix to the expected value"""
    result = versioning.serialize_prefix(source)
    assert result == expected, """
        Expected "{}" to be serialized as "{}" and not "{}".
        """.format(source, expected, result)


@pytest.mark.parametrize('expected,source', TEST_PARAMETERS)
def test_deserialize_prefix(source: str, expected: str):
    """Should deserialize the source prefix to the expected value"""
    expected = expected.rstrip('.)+-_')
    result = versioning.deserialize_prefix(source)
    assert result == expected, """
        Expected "{}" to be deserialized as "{}" and not "{}".
        """.format(source, expected, result)


def test_serialize_prefix_already():
    """Should not modify a prefix that is already serialized."""
    result = versioning.serialize_prefix('v1-2')
    assert 'v1-2' == result, 'Expected prefix to remain unchanged.'


def test_deserialize_prefix_already():
    """Should not modify a prefix that has already been deserialized."""
    result = versioning.deserialize_prefix('1.2')
    assert '1.2' == result, 'Expected prefix to remain unchanged.'
