import os
import tempfile
import requests
from urllib.parse import urlparse


def parse_url(wheel_url: str) -> dict:
    """ 
    Parses a wheel url into a dictionary containing information about the wheel 
    file
    """

    url_data = urlparse(wheel_url)
    path_parts = url_data.path.strip('/').split('/')

    return dict(
        url=wheel_url,
        wheel_filename=path_parts[-1],
        version=path_parts[-2].replace('-', '.'),
        package_name=path_parts[-3]
    )


def to_temp_file(url: str) -> str:
    """
    """

    url_data = parse_url(url)
    directory = tempfile.mkdtemp(prefix='pipper-')
    path = os.path.join(directory, 'package.whl')
    return save(url, path)


def save(url: str, local_path: str) -> str:
    """ 
    """

    response = requests.get(url)
    with open(local_path, 'wb') as f:

        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    return local_path
