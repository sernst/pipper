import pytest

from pipper import versioning

TEST_PARAMETERS = [
    ('1.2.3-alpha-beta.1', 'v1-2-3__pre_alpha-beta_1'),
    ('1.2.3-alpha.1+2-test', 'v1-2-3__pre_alpha_1__build_2-test'),
    ('1.2.3+2-test', 'v1-2-3__build_2-test'),
    ('1.2.0-2+2-test', 'v1-2-0__pre_2__build_2-test')
]


@pytest.mark.parametrize('source,expected', TEST_PARAMETERS)
def test_serialize(source: str, expected: str):
    """Should serialize the source version to the expected value"""
    result = versioning.serialize(source)
    assert result == expected, """
        Expected "{}" to be serialized as "{}" and not "{}".
        """.format(source, expected, result)


@pytest.mark.parametrize('expected,source', TEST_PARAMETERS)
def test_deserialize(source: str, expected: str):
    """Should deserialize the source version to the expected value"""
    result = versioning.deserialize(source)
    assert result == expected, """
        Expected "{}" to be deserialized as "{}" and not "{}".
        """.format(source, expected, result)


def test_serialize_invalid():
    """Should raise error trying to serialize invalid value."""
    with pytest.raises(ValueError):
        versioning.serialize('1.2')


def test_deserialize_invalid():
    """Should raise error trying to deserialize invalid value."""
    with pytest.raises(ValueError):
        versioning.deserialize('v1-2')
