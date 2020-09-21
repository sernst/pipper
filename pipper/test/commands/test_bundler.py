import os
import pathlib
import shutil
import tempfile

import pipper
from pipper import command


def test_bundle():
    """
    Should successfully bundle the hello_pipper project into a pipper
    file in a temporary directory and verify that file exists.
    """
    current_directory = pathlib.Path(os.curdir).absolute()
    directory = tempfile.mkdtemp()
    os.chdir(directory)

    project_directory = (
        pathlib.Path(pipper.__file__)
        .parent.parent
        .joinpath('hello_pipper')
        .absolute()
    )
    try:
        command.run([
            'bundle',
            '--output={}'.format(str(directory)),
            str(project_directory),
        ])
        filename = next(
            (x for x in os.listdir(directory) if x.endswith('.pipper')),
            None
        )
        assert filename
        assert filename.startswith('hello_pipper-v')
    finally:
        shutil.rmtree(directory)
        os.chdir(str(current_directory))
