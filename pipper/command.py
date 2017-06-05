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


def run(cli_args: list = None):
    """ """

    args = parser.parse(cli_args)
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
