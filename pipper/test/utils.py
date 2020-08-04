import typing
import functools
from unittest.mock import MagicMock
from unittest.mock import patch


class BotoMocks(typing.NamedTuple):
    """Data structure for boto3 mocked objects"""

    session: MagicMock
    s3_client: MagicMock


class PatchSession:
    """A Patch function for the boto3 session"""

    def __init__(self, *args, **kwargs):
        """Create decorator with arguments"""
        pass

    def __call__(self, test_function):
        """
        Decorates the specified test function by returning a new function
        that wraps it with patching in place for mocked phalanx functions.
        """
        @patch('pipper.environment.get_session')
        def patch_session(get_session: MagicMock, *args, **kwargs):
            boto_mocks = _create_boto_mocks()
            get_session.return_value = boto_mocks.session
            test_function(boto_mocks, *args, **kwargs)

        return patch_session


def affect_by_identifier(**identifiers):
    """..."""
    def side_effect(execution_identifier: str, *args, **kwargs):
        return identifiers.get(execution_identifier)
    return side_effect


def make_list_objects_response(
        contents: list = None,
        next_continuation_token: str = None
) -> dict:
    """..."""
    return dict(
        Contents=contents or [],
        NextContinuationToken=next_continuation_token
    )


def _get_client(
        mocked_clients: typing.Dict[str, MagicMock],
        identifier: str,
        **kwargs
) -> MagicMock:
    """..."""
    return mocked_clients.get(identifier) or MagicMock()


def _create_boto_mocks() -> BotoMocks:
    """..."""
    s3_client = MagicMock()
    session = MagicMock()
    session.client.side_effect = functools.partial(
        _get_client,
        {'s3': s3_client}
    )
    return BotoMocks(session=session, s3_client=s3_client)  # noqa
