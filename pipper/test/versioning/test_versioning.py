from pipper import versioning


def test_make_s3_key():
    """Should convert package name and version to an associated S3 key."""
    name = 'fake-package'
    version = '1.2.3-alpha.1+2-test'
    key = versioning.make_s3_key(name, version)
    assert key.endswith('.pipper'), 'Expected a pipper file key.'
    assert key.find(f'/{name}/'), 'Expected the package name as a folder.'
