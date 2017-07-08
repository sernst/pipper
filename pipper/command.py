import sys
import json
import os

from pipper import parser
from pipper import installer
from pipper import bundler
from pipper import publisher
from pipper import info
from pipper import authorizer
from pipper import downloader
from pipper import repository
from pipper.environment import Environment


ACTIONS = dict(
    authorize=authorizer.run,
    download=downloader.run,
    install=installer.run,
    bundle=bundler.run,
    publish=publisher.run,
    info=info.run,
    repository=repository.run
)


def show_version():
    """Shows the pipper version information and then exits"""

    settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
    with open(settings_path) as f:
        settings = json.load(f)

    print('Version: {}'.format(settings.get('version') or 'Unknown'))


def run(cli_args: list = None):
    """ """

    args = parser.parse(cli_args)

    if args.get('version'):
        show_version()
        sys.exit(0)

    env = Environment(args)

    action = ACTIONS.get(env.action)
    if action is None:
        message = 'Unrecognized command action "{}"'.format(env.action)
        print('[ERROR]: {}'.format(message))
        args['parser'].print_help()
        raise ValueError(message)

    print('\n\n=== {} ===\n'.format(env.action.upper()))

    try:
        action(env)
    except Exception as err:
        print('[ERROR]: Unable to complete action. {}\n'.format(err))
        raise

    print('\n')
