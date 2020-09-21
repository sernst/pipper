
from pipper import versioning


def test_parse_package_url():
    """Should parse package URL"""
    rv = versioning.to_remote_version('fake', '1.0.1-alpha.1', 'fake-bucket')
    rv_url = versioning.parse_package_url(rv.url)
    assert rv == rv_url, 'Expect URL parsing to be consistent.'


def test_parse_package_url_custom_prefix():
    """Should parse package URL with a non-standard prefix."""
    rv = versioning.to_remote_version(
        package_name='fake',
        package_version='1.0.1-alpha.1',
        bucket='fake-bucket',
        root_prefix='foo/bar',
    )
    rv_url = versioning.parse_package_url(rv.url)
    assert rv == rv_url, 'Expect URL parsing to be consistent.'
