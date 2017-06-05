import semver


def serialize(version: str) -> str:
    """ """

    try:
        info = semver.parse_version_info(version)
    except ValueError:
        raise ValueError('Invalid semantic version "{}"'.format(version))

    pre = info.prerelease.replace('.', '_') if info.prerelease else None
    build = info.build.replace('.', '_') if info.build else None

    return 'v{}-{}-{}{}{}'.format(
        info.major,
        info.minor,
        info.patch,
        '-p-{}'.format(pre) if pre else '',
        '-b-{}'.format(build) if build else ''
    )


def deserialize(version: str) -> str:
    """ """

    return (
        version
        .lstrip('v')
        .replace('-', '.', 2)
        .replace('-p-', '-')
        .replace('-b-', '+')
    )


def make_s3_key(package_name: str, package_version: str) -> str:
    """ """

    safe_version = (
        serialize(package_version)
        if not package_version.startswith('v') else
        package_version
    )

    return 'pipper/{}/{}.pipper'.format(package_name, safe_version)


def parse_s3_key(key: str) -> dict:
    """ """

    parts = key.strip('/').split('/')
    safe_version = parts[2].rsplit('.', 1)[0]

    return dict(
        name=parts[1],
        safe_version=safe_version,
        version=deserialize(safe_version)
    )
