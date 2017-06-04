from pipper import parser
from pipper import installer
from pipper import bundler
from pipper import publisher
from pipper.environment import Environment


ACTIONS = dict(
    install=installer.run,
    bundle=bundler.run,
    publish=publisher.run
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

    print('\n\n=== {} ==='.format(env.action.upper()))

    try:
        action(env)
    except Exception as err:
        print('[ERROR]: Unable to complete action. {}\n'.format(err))
        raise

    print('\n')
