import json
import os
import re
from datetime import timedelta
from urllib.parse import urlparse

from pipper import downloader
from pipper import environment
from pipper.environment import Environment

DELTA_REGEX = re.compile('(?P<number>[0-9]+)\s*(?P<unit>[a-zA-Z]+)')


def to_time_delta(age: str) -> timedelta:
    """ 
    Converts an age string into a timedelta object, parsing the number and 
    units of the age. Valid units are:
        * hour, hrs, hr, h
        * minutes, mins, min, m
        * seconds, secs, sec, s

    Examples:
        1s -> 1 second
        24mins -> 24 minutes
        3hours -> 3 hours
    """

    try:
        result = DELTA_REGEX.search(age)
        unit = result.group('unit').lower()
        number = int(result.group('number'))
    except Exception:
        unit = 's'
        number = 600

    return timedelta(
        hours=number if unit.startswith('h') else 0,
        minutes=number if unit.startswith('m') else 0,
        seconds=number if unit.startswith('s') else 0
    )


def parse_url(pipper_url: str) -> dict:
    """ 
    Parses a wheel url into a dictionary containing information about the wheel 
    file
    """

    url_data = urlparse(pipper_url)
    path_parts = url_data.path.strip('/').split('/')

    return dict(
        url=pipper_url,
        wheel_filename=path_parts[-1],
        version=path_parts[-2].replace('-', '.'),
        package_name=path_parts[-3]
    )


def create_url(env: Environment, package_id: str) -> str:
    """ """

    data = downloader.parse_package_id(
        env=env,
        package_id=package_id,
        use_latest_version=True
    )
    delta = to_time_delta(env.args.get('expires_in'))

    url = env.s3_client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=int(delta.total_seconds()),
        Params={'Bucket': env.bucket, 'Key': data['key']}
    )

    if not env.quiet:
        print('[AUTHORIZED]: {} -> {}'.format(data['name'], url))
    return url


def create_many_urls(env: Environment, package_ids: list) -> dict:
    """ """

    urls = {pid: create_url(env, pid) for pid in package_ids}
    save_path = env.args.get('save_path')

    if not save_path:
        return urls

    configs = dict(
        dependencies=[url for url in urls.values()]
    )

    path = os.path.realpath(save_path)
    with open(path, 'w') as f:
        json.dump(configs, f)

    if not env.quiet:
        print('[SAVED]: {}'.format(path))

    return urls


def run(env: Environment):
    """Execute the authorize command"""

    package_ids = env.args.get('packages')
    if package_ids:
        urls = create_many_urls(env, package_ids)
    else:
        configs = environment.load_configs(env.args.get('configs_path'))
        urls = create_many_urls(env, configs.get('dependencies') or [])

    if env.quiet:
        print(' '.join(urls.values()))
    return urls
