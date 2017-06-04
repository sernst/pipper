import os
from argparse import ArgumentParser

package_directory = os.path.dirname(os.path.realpath(__file__))


def read_file(*args) -> str:
    """ """

    path = os.path.join(package_directory, *args)
    with open(path, 'r') as f:
        return f.read()


def populate_with_credentials(parser: ArgumentParser) -> ArgumentParser:

    parser.add_argument(
        '-p', '--profile',
        dest='aws_profile',
        help=read_file('resources', 'profile_flag.txt')
    )

    parser.add_argument(
        '-c', '--credentials',
        dest='aws_credentials',
        nargs=2,
        default=[],
        help=''
    )

    parser.add_argument(
        '-b', '--bucket',
        dest='bucket',
        help='Name of the bucket containing the pipper packages'
    )

    return parser


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

    return populate_with_credentials(parser)


def populate_bundle(parser: ArgumentParser) -> ArgumentParser:
    """ """

    parser.description = read_file('resources', 'bundle_action.txt')

    parser.add_argument('package_directory')
    parser.add_argument(
        '-o', '--output',
        dest='output_directory'
    )

    return parser


def populate_publish(parser: ArgumentParser) -> ArgumentParser:
    """ """

    parser.description = read_file('resources', 'publish_action.txt')

    parser.add_argument(
        'target_path',
        help='Path of the pipper file or directory containing the pipper file'
    )

    parser.add_argument(
        '-f', '--force',
        dest='force',
        action='store_true',
        default=False,
        help='Force publishing even if the version has already been published'
    )

    return populate_with_credentials(parser)


def populate_info(parser: ArgumentParser) -> ArgumentParser:
    """ """

    parser.description = read_file('resources', 'info_action.txt')

    parser.add_argument(
        'package_name',
        help='Name of the package about which to retrieve information'
    )

    parser.add_argument(
        '-l', '--local',
        dest='local_only',
        action='store_true',
        default=False,
        help='Only get local package information'
    )

    parser.add_argument(
        '-r', '--remote',
        dest='remote_only',
        action='store_true',
        default=False,
        help='Only get remote package information'
    )

    return populate_with_credentials(parser)


def parse(cli_args: list = None) -> dict:
    """ """

    parser = ArgumentParser(
        description=read_file('resources', 'command_description.txt'),
        add_help=True
    )

    subparsers = parser.add_subparsers(help='Command actions', dest='action')

    populate_install(subparsers.add_parser('install'))
    populate_bundle(subparsers.add_parser('bundle'))
    populate_publish(subparsers.add_parser('publish'))
    populate_info(subparsers.add_parser('info'))

    out = vars(parser.parse_args(cli_args))
    out['parser'] = parser
    return out
