
from pipper import versioning


def test_parse_package_url():
    """Should parse package URL"""
    rv = versioning.to_remote_version('fake', '1.0.1-alpha.1', 'fake-bucket')
    rv_url = versioning.parse_package_url(rv.url)
    assert rv == rv_url, 'Expect URL parsing to be consistent.'
