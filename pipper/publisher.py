import os
import zipfile
import json

from pipper import s3
from pipper import versioning
from pipper.environment import Environment


def is_already_published(env: Environment, metadata: dict) -> bool:
    """ """

    return s3.key_exists(
        s3_client=env.s3_client,
        bucket=env.bucket,
        key=versioning.make_s3_key(metadata['name'], metadata['version'])
    )


def read_metadata(bundle_path: str) -> dict:
    """ """

    with zipfile.ZipFile(bundle_path) as zipper:
        contents = zipper.read('package.meta')

    return json.loads(contents)


def get_pipper_files_in(target_directory: str) -> list:
    """ """

    directory = os.path.realpath(target_directory)

    def to_path_entry(filename: str) -> dict:
        path = os.path.join(directory, filename)
        return {'time': os.path.getmtime(path), 'path': path}

    path_entries = [
        to_path_entry(filename)
        for filename in os.listdir(directory)
        if filename.endswith('.pipper')
    ]
    path_entries.sort(key=lambda entry: entry['time'])

    return [e['path'] for e in path_entries if os.path.isfile(e['path'])]


def from_pipper_file(env: Environment, bundle_path: str):
    """ """

    metadata = read_metadata(bundle_path)

    print('[SYNCING]: "{}"'.format(metadata['name']))

    force = env.args.get('force')
    if not force and is_already_published(env, metadata):
        print('[SKIPPED]: "{}" version {} is already published'.format(
            metadata['name'],
            metadata['version']
        ))
        return

    print('[PUBLISHING]: "{}" version {}'.format(
        metadata['name'],
        metadata['version']
    ))

    content_length = os.path.getsize(bundle_path)

    with open(bundle_path, 'rb') as f:
        env.s3_client.put_object(
            ACL='private',
            Body=f,
            Bucket=env.bucket,
            Key=versioning.make_s3_key(
                metadata['name'],
                metadata['version']
            ),
            ContentType='application/zip',
            ContentLength=content_length,
            Metadata={
                'package': json.dumps(metadata),
                'version': metadata['version'],
                'safe_version': metadata['safe_version'],
                'name': metadata['name'],
                'timestamp': metadata['timestamp']
            }
        )


def run(env: Environment):
    """ """

    target_path = os.path.realpath(env.args['target_path'])

    if not os.path.exists(target_path):
        raise FileNotFoundError('No such path "{}"'.format(target_path))

    bundle_path = (
        get_pipper_files_in(target_path)[-1]
        if os.path.isdir(target_path) else
        target_path
    )

    return from_pipper_file(env, bundle_path)
