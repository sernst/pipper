import os
import zipfile
import json
from pipper.environment import Environment


def make_s3_key(metadata: dict) -> str:
    """ """

    return 'pipper/{}/{}.pipper'.format(
        metadata['name'],
        metadata['safe_version']
    )


def is_already_published(s3_client, metadata: dict) -> bool:
    """ """

    try:
        response = s3_client.list_objects(
            Bucket=metadata['bucket'],
            Prefix=make_s3_key(metadata),
            MaxKeys=1
        )
        return len(response['Contents']) > 0
    except Exception:
        return False


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
    if not force and is_already_published(env.s3_client, metadata):
        print('[SKIPPED]: "{}" version {} is already published'.format(
            metadata['name'],
            metadata['version']
        ))
        return

    print('[PUBLISHING]: "{}" version {}'.format(
        metadata['name'],
        metadata['version']
    ))

    with open(bundle_path, 'rb') as f:
        env.s3_client.put_object(
            ACL='private',
            Body=f,
            Bucket=metadata['bucket'],
            Key=make_s3_key(metadata),
            ContentType='application/zip',
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
