import semver
from pipper.versioning import serde


class RemoteVersion(object):
    """
    Data structure for storing information about remote data sources.
    """

    def __init__(self, bucket: str, key: str):
        """_ doc..."""
        self._key = key
        self._bucket = bucket

    @property
    def key(self) -> str:
        return self._key

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def package_name(self) -> str:
        return self._key.strip('/').split('/')[1]

    @property
    def filename(self) -> str:
        return self.key.rsplit('/', 1)[-1]

    @property
    def version(self) -> str:
        return serde.deserialize(self.key.rsplit('/', 1)[-1].rsplit('.', 1)[0])

    @property
    def safe_version(self) -> str:
        return self.key.rsplit('/', 1)[-1].rsplit('.', 1)[0]

    def __lt__(self, other):
        return semver.compare(self.version, other.version) < 0

    def __le__(self, other):
        return semver.compare(self.version, other.version) != 1

    def __gt__(self, other):
        return semver.compare(self.version, other.version) > 0

    def __ge__(self, other):
        return semver.compare(self.version, other.version) != -1

    def __eq__(self, other):
        return semver.compare(self.version, other.version) == 0

    def __repr__(self):
        return '<{} {}:{}>'.format(
            self.__class__.__name__,
            self.package_name,
            self.version
        )
