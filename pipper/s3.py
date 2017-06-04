import os

import typing
from boto3.session import Session


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

    token = (
        credentials[2]
        if len(credentials) > 2 and len(credentials[2]) > 1 else
        None
    )

    return Session(
        aws_access_key_id=credentials[0],
        aws_secret_access_key=credentials[1],
        aws_session_token=token
    )


def get_session(
        aws_profile: str = None,
        aws_credentials: typing.List[str] = None
) -> Session:
    """ """

    specific_credentials = [
        os.environ.get('PIPPER_AWS_ACCESS_KEY_ID'),
        os.environ.get('PIPPER_AWS_SECRET_ACCESS_KEY'),
        os.environ.get('PIPPER_AWS_SESSION_TOKEN')
    ]

    env_credentials = [
        os.environ.get('AWS_ACCESS_KEY_ID'),
        os.environ.get('AWS_SECRET_ACCESS_KEY'),
        os.environ.get('AWS_SESSION_TOKEN')
    ]

    def generate_session():
        yield Session(profile_name=aws_profile) if aws_profile else None
        yield session_from_credentials_list(aws_credentials)
        yield session_from_credentials_list(specific_credentials)
        yield session_from_credentials_list(env_credentials)
        yield Session()

    return next(s for s in generate_session() if s is not None)


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
