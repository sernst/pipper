import typing

from boto3.session import Session
from botocore.client import BaseClient


def session_from_credentials_list(
        credentials: list
) -> typing.Union[Session, None]:
    """ """
    is_valid = (
        credentials and
        len(credentials) > 1 and
        credentials[0] and
        credentials[1]
    )

    if not is_valid:
        return None

    token = (credentials[2] if len(credentials) > 2 else None)
    token = (token or '0').strip().strip('"\'')

    return Session(
        aws_access_key_id=credentials[0],
        aws_secret_access_key=credentials[1],
        aws_session_token=token if len(token) > 1 else None
    )


def session_from_profile_name(
        profile_name: typing.Union[str, None]
) -> typing.Union[Session, None]:
    """ """

    if not profile_name:
        return None

    return Session(profile_name=profile_name)


def key_exists(s3_client, bucket: str, key: str) -> bool:
    """ """
    try:
        response = s3_client.list_objects(
            Bucket=bucket,
            Prefix=key,
            MaxKeys=1
        )
        return len(response['Contents']) > 0
    except Exception:
        return False


def list_objects(
        execution_identifier: str,
        s3_client: BaseClient,
        bucket: str,
        prefix: str,
        **kwargs
) -> dict:
    """..."""
    return s3_client.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        **kwargs
    )
