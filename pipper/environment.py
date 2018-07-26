import os
import json
import typing

from boto3.session import Session
from botocore.client import BaseClient
from botocore.credentials import Credentials

from pipper import s3

REPOSITORY_CONFIGS_PATH = os.path.join(
    os.path.expanduser('~'),
    '.pipper',
    'repositories.json'
)


class Environment:

    def __init__(self, args: dict = None):
        self.args = clean_args(args or {})

        repository = load_repository(self.args.get('repository_name'))
        default_repository = load_repository(None, True)
        self.repository = repository or default_repository

        self.aws_session = get_session(
            self.args,
            repository,
            default_repository
        )

        self.s3_client = self.aws_session.client('s3')  # type: BaseClient

    @property
    def quiet(self) -> bool:
        return self.args.get('quiet') or False

    @property
    def bucket(self) -> str:
        return (
            self.args.get('bucket') or
            self.repository.get('bucket')
        )

    @property
    def action(self) -> str:
        return self.args.get('action')


def clean_args(args: dict) -> dict:
    """Cleans the arguments by stripping them of whitespace and quotations"""

    def clean(arg):
        if isinstance(arg, str):
            return arg.strip(' "')
        return arg

    return {key: clean(value) for key, value in args.items()}


def load_repositories() -> dict:
    """ """
    try:
        with open(REPOSITORY_CONFIGS_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {'repositories': {}, 'default': None}


def save_repositories(config_data: dict) -> dict:
    """ """

    directory = os.path.dirname(REPOSITORY_CONFIGS_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(REPOSITORY_CONFIGS_PATH, 'w') as f:
        json.dump(config_data, f, indent=2)

    return config_data


def load_repository(
        repository_name: typing.Union[str, None],
        allow_default: bool = False
) -> dict:
    """ """

    results = load_repositories()

    try:
        return results['repositories'][repository_name]
    except Exception:
        if not allow_default:
            return {}

    try:
        return results['repositories'][results['default']]
    except Exception:
        return {}


def load_configs(configs_path: str = None):
    """ """

    path = os.path.realpath(
        configs_path or
        os.path.join(os.curdir, 'pipper.json')
    )

    if not os.path.exists(path):
        raise FileNotFoundError('Missing configuration file "{}"'.format(path))

    with open(path, 'r') as f:
        return json.load(f)


def get_session(
        args: dict,
        repository: dict,
        default_repository: dict
) -> Session:
    """ 
    Creates an S3 session using AWS credentials, which can be specified in a 
    myriad of potential ways.
    """

    aws_profile = args.get('aws_profile')
    command_credentials = args.get('aws_credentials') or []

    repo_aws_profile = repository.get('profile')
    repository_credentials = [
        repository.get('access_key_id'),
        repository.get('secret_access_key'),
        repository.get('session_token')
    ]

    default_repo_aws_profile = default_repository.get('profile')
    default_repository_credentials = [
        default_repository.get('access_key_id'),
        default_repository.get('secret_access_key'),
        default_repository.get('session_token')
    ]

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
        yield s3.session_from_credentials_list(command_credentials)
        yield s3.session_from_profile_name(repo_aws_profile)
        yield s3.session_from_credentials_list(repository_credentials)
        yield s3.session_from_profile_name(aws_profile)
        yield s3.session_from_credentials_list(specific_credentials)
        yield s3.session_from_credentials_list(env_credentials)
        yield s3.session_from_profile_name(default_repo_aws_profile)
        yield s3.session_from_credentials_list(default_repository_credentials)
        yield Session()

    session = next(s for s in generate_session() if s is not None)
    credentials: Credentials = session.get_credentials()

    token = credentials.token

    print('\n[LOADED]: AWS Credentials')
    print('    PROFILE: {}'.format(session.profile_name))
    print('    ACCESS: {}'.format(credentials.access_key))
    print('    SECRET: {}...'.format(credentials.secret_key[:8]))
    print('     TOKEN: {}{}'.format(
        token[:12] if token else 'NONE',
        '...' if token else ''
    ))
    print('    METHOD: {}'.format(credentials.method))

    return session
