#! /usr/bin/env python3

from argparse import ArgumentParser

import boto3


def parse() -> dict:
    """ """

    parser = ArgumentParser()

    parser.add_argument('package_name')
    parser.add_argument('version')
    parser.add_argument(
        '-p', '--profile',
        dest='aws_profile',
        default='default'
    )
    parser.add_argument(
        '-l', '--lifetime',
        dest='lifetime',
        help='Days to live',
        type=int,
        default=1
    )

    return vars(parser.parse_args())


def run():
    """ """

    args = parse()
    session = boto3.session.Session(profile_name=args['aws_profile'])
    s3_client = session.client('s3')

    key = 'pipper/{name}/{version}/{name}.whl'.format(
        name=args['package_name'],
        version=args['version']
    )

    # Generate the URL to get 'key-name' from 'bucket-name'
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=24 * 3600 * args.get('lifetime'),
        Params={'Bucket': 'pipper-wiw', 'Key': key}
    )

    print(url)


if __name__ == '__main__':
    run()
