from unittest.mock import MagicMock
from unittest.mock import patch

from pipper import command
from pipper.test import utils


@patch('pipper.installer.install')
@utils.PatchSession()
def test_install(
        boto_mocks: utils.BotoMocks,
        install: MagicMock
):
    """..."""
    command.run(['install', 'foo'])
