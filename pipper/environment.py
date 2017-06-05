import os
import json

from pipper import s3


class Environment:

    def __init__(self, args: dict = None):
        self.args = args
        self.aws_session = s3.get_session(
            aws_profile=args.get('aws_profile'),
            aws_credentials=args.get('aws_credentials')
        )
        self.s3_client = self.aws_session.client('s3')

    @property
    def action(self):
        return self.args.get('action')


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
