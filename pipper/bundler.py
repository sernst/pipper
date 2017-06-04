import json
import os
import shutil
import tempfile
import time
import zipfile
from datetime import datetime
from distutils.core import run_setup

from setuptools.dist import Distribution

from pipper.environment import Environment
from pipper import versioning


def zip_bundle(
        bundle_directory: str,
        output_directory: str,
        distribution_data: dict
) -> str:
    """ 
    Creates a pipper zip file from the temporarily stored meta data and wheel
    files and saves that zip file to the output directory location with the
    pipper extension.
    
    :param bundle_directory:
        The directory in which the bundle was assembled, which contains the
        metadata and wheel files
    :param output_directory:
        The directory where the zip bundle will be saved.
    :param distribution_data:
        Information about the package obtained during the wheel building
        process, which includes information retrieved from the setup.py
        file.
        
    :return
        Returns the absolute path to the created zip file.
    """

    filename = '{}-{}.pipper'.format(
        distribution_data['package_name'],
        distribution_data['safe_version']
    )
    zip_path = os.path.join(output_directory, filename)

    with zipfile.ZipFile(zip_path, mode='w') as zipper:
        for filename in os.listdir(bundle_directory):
            path = os.path.join(bundle_directory, filename)
            zipper.write(path, filename)

    return zip_path


def create_meta(
        package_directory: str,
        bundle_directory: str,
        distribution_data: dict
) -> str:
    """ 
    Creates a JSON-formatted metadata file with information about the package 
    being bundled that is saved into the specified output directory.
    
    :param package_directory:
        Directory where the package being bundled resides
    :param bundle_directory:
        Directory where the bundle is being assembled. This is where the 
        metadata file will be written.
    :param distribution_data:
        Information about the package obtained during the wheel building
        process, which includes information retrieved from the setup.py
        file.
        
    :return
        The absolute path to the created metadata file is returned.
    """

    config_path = os.path.join(package_directory, 'pipper.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            'Missing pipper config file at "{}"'.format(config_path)
        )

    with open(config_path, 'r') as f:
        metadata = json.load(f)  # type: dict

    metadata.update(dict(
        name=distribution_data['package_name'],
        version=distribution_data['version'],
        safe_version=distribution_data['safe_version'],
        timestamp=datetime.utcnow().isoformat()
    ))

    path = os.path.join(bundle_directory, 'package.meta')

    with open(path, 'w') as f:
        json.dump(metadata, f)

    return path


def create_wheel(package_directory: str, bundle_directory: str) -> dict:
    """ 
    Creates a universally wheel distribution of the specified package and
    saves that to the bundle directory.
    
    :param package_directory:
        Directory where the package being bundled resides
    :param bundle_directory:
        Directory where the bundle is being assembled. This is where the 
        wheel file will be written.
        
    :return
        Returns a dictionary containing distribution information about the 
        wheel package.
    """

    setup_path = os.path.join(package_directory, 'setup.py')
    if not os.path.exists(setup_path):
        raise FileNotFoundError('No setup.py at "{}"'.format(setup_path))

    result = run_setup(
        script_name=setup_path,
        script_args=['bdist_wheel', '--universal', '-d', bundle_directory]
    )  # type: Distribution

    # Pause to make sure OS releases wheel file before moving it
    time.sleep(1)

    wheel_files = [
        name
        for name in os.listdir(bundle_directory)
        if name.endswith('.whl')
    ]
    wheel_path = os.path.join(bundle_directory, 'package.whl')
    shutil.move(os.path.join(bundle_directory, wheel_files[0]), wheel_path)

    return dict(
        wheel_path=wheel_path,
        package_name=result.get_name(),
        version=result.get_version(),
        safe_version=versioning.serialize(result.get_version())
    )


def run(env: Environment) -> str:
    """ 
    Executes the bundling process on the specified package directory and saves
    the pipper bundle file in the specified output directory.
            
    :param package_directory:
        Directory where the package being bundled resides
    :param output_directory:
        Directory where the bundled file should be written. If this argument
        is not specified, the bundled file will be written to the package
        directory.
    
    :return
        The absolute path to the location of the created bundle file.
    """

    package_directory = env.args.get('package_directory') or '.'
    output_directory = env.args.get('output_directory')

    directory = os.path.realpath(package_directory)
    if not os.path.exists(directory):
        raise NotADirectoryError('No such directory "{}"'.format(directory))

    save_directory = (
        os.path.realpath(output_directory)
        if output_directory else
        directory
    )

    bundle_directory = tempfile.mkdtemp(prefix='pipper-bundle-')

    try:
        distribution_data = create_wheel(directory, bundle_directory)
        create_meta(directory, bundle_directory, distribution_data)
        return zip_bundle(bundle_directory, save_directory, distribution_data)
    except Exception:
        raise
    finally:
        shutil.rmtree(bundle_directory)
