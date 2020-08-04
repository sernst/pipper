from pipper import versioning


def test_attributes():
    """Should have correct attributes specified in assignment"""
    bucket = 'FAKE'
    package = 'test'
    version = '0.0.1'
    rv = versioning.to_remote_version(package, version, bucket)
    assert rv.bucket == bucket
    assert rv.key.find(package) > 0
    assert str(rv).find(package) > 0
    assert str(rv).find(version) > 0
    assert not rv.is_url_based


def test_comparison():
    """Should compare two remote versions correctly"""
    rv1 = versioning.to_remote_version('test', '0.0.1-alpha.1', 'FAKE')
    rv2 = versioning.to_remote_version('test', '0.0.1', 'FAKE')
    rv3 = versioning.to_remote_version('test', '0.1.0', 'FAKE')

    assert rv1 < rv2 < rv3
    assert rv1 <= rv2 <= rv3
    assert not rv1 >= rv2
    assert not rv1 > rv2
    assert not rv1 == rv2
    assert rv1 == rv1
