import os
import json
from urllib.parse import urlparse

from pipper import downloader
from pipper import environment
from pipper.environment import Environment


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

    data = downloader.parse_package_id(env, package_id)

    url = env.s3_client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=24 * 3600 * env.args.get('minutes_to_live'),
        Params={'Bucket': 'pipper-wiw', 'Key': data['key']}
    )

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

    print('[SAVED]: {}'.format(path))

    return urls


def run(env: Environment):
    """ 
    """

    package_ids = env.args.get('packages')
    if package_ids:
        return create_many_urls(env, package_ids)

    configs = environment.load_configs(env.args.get('configs_path'))
    return create_many_urls(env, configs.get('dependencies') or [])
