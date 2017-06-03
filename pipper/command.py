from pipper import parser
from pipper import installer
from pipper import bundler


ACTIONS = dict(
    install=installer.install_from_args,
    bundle=bundler.run
)


def run(cli_args: list = None):
    """ """

    args = parser.parse(cli_args)

    action = ACTIONS.get(args['action'])
    if action is None:
        raise ValueError(
            'Unrecognized command action "{}"'.format(args['action'])
        )

    action(**args)

