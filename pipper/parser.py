import argparse
import os
from argparse import ArgumentParser

package_directory = os.path.dirname(os.path.realpath(__file__))


def required_length(minimum: int, maximum: int, optional: bool = False):
    """Returns a custom required length class"""
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            is_allowed = (
                (minimum <= len(values) <= maximum) or
                (optional and not len(values))
            )

            if is_allowed:
                setattr(args, self.dest, values)
                return

            raise argparse.ArgumentTypeError(
                'Argument "{}" must have {}-{} arguments'.format(
                    self.dest,
                    minimum,
                    maximum
                )
            )

    return RequiredLength


def read_file(*args) -> str:
    """ """
    path = os.path.join(package_directory, *args)
    with open(path, 'r') as f:
        return f.read()


def populate_with_common(parser: ArgumentParser) -> ArgumentParser:
    """ """
    parser.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        default=False,
        help='Quiet output only returns necessary information for commands'
    )

    return parser


def populate_with_credentials(parser: ArgumentParser) -> ArgumentParser:
    """ """
    parser.add_argument(
        '-r', '--repository',
        dest='repository_name',
    )

    parser.add_argument(
        '-p', '--profile',
        dest='aws_profile',
        help=read_file('resources', 'profile_flag.txt')
    )

    parser.add_argument(
        '-c', '--credentials',
        dest='aws_credentials',
        nargs='+',
        default=[],
        help='',
        action=required_length(2, 3, True)
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
        dest='configs_path'
    )

    parser.add_argument(
        '--user',
        default=False,
        action='store_true',
        dest='pip_user'
    )

    parser.add_argument(
        '-t', '--target',
        dest='target_directory',
        metavar='<dir>',
        help=(
            'Install packages into <dir>. By default this '
            'will not replace existing files/folders in '
            '<dir>. Use --upgrade to replace existing '
            'packages in <dir> with new versions. '
            'When applied to conda packages, this should '
            'be the root directory of the conda environment '
            'where the libraries will be installed.'
        )
    )

    parser.add_argument(
        '-u', '--upgrade', '--update',
        dest='upgrade',
        action='store_true',
        default=False,
        help='Upgrade existing packages to latest version'
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

    parser.add_argument(
        '--skip-fails',
        dest='skip_fails',
        action='store_true',
        default=False,
        help=' '.join([
            'Raise an exception if publish is skipped because version is',
            'already published.'
        ])
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

    return populate_with_credentials(parser)


def populate_download(parser: ArgumentParser) -> ArgumentParser:
    """ """
    parser.description = read_file('resources', 'download_action.txt')

    parser.add_argument(
        'packages',
        nargs='*'
    )

    parser.add_argument(
        '-d', '--directory',
        dest='save_directory'
    )

    parser.add_argument(
        '-i', '--input',
        dest='configs_path'
    )

    parser.add_argument(
        '-e', '--extract',
        dest='extract',
        action='store_true',
        default=False
    )

    return populate_with_credentials(parser)


def populate_repository(parser: ArgumentParser) -> ArgumentParser:
    """ """

    subparsers = parser.add_subparsers(
        help='Repository actions',
        dest='repository_action'
    )

    remove_parser = subparsers.add_parser('remove')
    remove_parser.add_argument('repository_profile_name')

    exists_parser = subparsers.add_parser('exists')
    exists_parser.add_argument('repository_profile_name')

    subparsers.add_parser('list')

    add_parser = subparsers.add_parser('add')
    add_parser.add_argument('repository_profile_name')
    add_parser.add_argument(
        '-d', '--default',
        dest='default',
        action='store_true',
        default=False
    )
    populate_with_credentials(add_parser)

    modify_parser = subparsers.add_parser('modify')
    modify_parser.add_argument('repository_profile_name')
    modify_parser.add_argument(
        '-d', '--default',
        dest='default',
        action='store_true',
        default=False
    )
    populate_with_credentials(modify_parser)

    return parser


def populate_authorize(parser: ArgumentParser) -> ArgumentParser:
    """ """

    parser.description = read_file('resources', 'authorize_action.txt')

    parser.add_argument(
        'packages',
        nargs='*'
    )

    parser.add_argument(
        '-o', '--output',
        dest='save_path'
    )

    parser.add_argument(
        '-i', '--input',
        dest='configs_path'
    )

    parser.add_argument(
        '-e', '--expires',
        dest='expires_in',
        default=10
    )

    parser.add_argument(
        '-l', '--list',
        dest='list',
        action='store_true',
        default=False,
        help='Compact output as a single-line, space-separated list'
    )

    return populate_with_credentials(parser)


def parse(cli_args: list = None) -> dict:
    """
    Parses command line arguments for consumption by the invoked action
    and returns the parsed arguments as a dictionary.

    :param cli_args:
        Overrides the command line argument inputs. By default the sys args
        will be used.
    """
    parser = ArgumentParser(
        description=read_file('resources', 'command_description.txt'),
        add_help=True
    )

    parser.add_argument(
        '-v', '--version',
        dest='version',
        action='store_true',
        default=False,
        help='Show the pipper version information and then exit'
    )

    subparsers = parser.add_subparsers(help='Command actions', dest='action')

    parsers = [
        populate_install(subparsers.add_parser('install')),
        populate_bundle(subparsers.add_parser('bundle')),
        populate_publish(subparsers.add_parser('publish')),
        populate_info(subparsers.add_parser('info')),
        populate_download(subparsers.add_parser('download')),
        populate_authorize(subparsers.add_parser('authorize')),
        populate_repository(subparsers.add_parser('repository'))
    ]

    for p in parsers:
        populate_with_common(p)

    out = vars(parser.parse_args(cli_args))
    out['parser'] = parser
    return out
