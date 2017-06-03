import os
from argparse import ArgumentParser

package_directory = os.path.dirname(os.path.realpath(__file__))


def read_file(*args) -> str:
    """ """

    path = os.path.join(package_directory, *args)
    with open(path, 'r') as f:
        return f.read()


def populate_install(parser: ArgumentParser) -> ArgumentParser:
    """ """

    parser.description = read_file('resources', 'install_action.txt')

    parser.add_argument(
        'packages',
        nargs='*'
    )

    parser.add_argument(
        '-i', '--input',
        dest='package_path'
    )

    return parser


def populate_bundle(parser: ArgumentParser) -> ArgumentParser:
    """ """

    parser.description = read_file('resources', 'bundle_action.txt')

    parser.add_argument('package_directory')
    parser.add_argument(
        '-o', '--output',
        dest='output_directory'
    )

    return parser


def parse(cli_args: list = None) -> dict:
    """ """

    parser = ArgumentParser(
        description=read_file('resources', 'command_description.txt'),
        add_help=True
    )

    parser.add_argument(
        '-p', '--profile',
        dest='aws_profile',
        default='default',
        help=read_file('resources', 'profile_flag.txt')
    )

    parser.add_argument(
        '-c', '--credentials',
        dest='credentials',
        nargs=2,
        default=None,
        help=''
    )

    subparsers = parser.add_subparsers(help='Command actions', dest='action')

    populate_install(subparsers.add_parser('install'))
    populate_bundle(subparsers.add_parser('bundle'))

    return vars(parser.parse_args(cli_args))
