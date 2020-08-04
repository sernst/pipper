from unittest.mock import MagicMock
from unittest.mock import patch

from pipper import command
from pipper.test import utils


@patch('pipper.s3.list_objects')
@utils.PatchSession()
def test_info(boto_mocks: utils.BotoMocks, list_objects: MagicMock):
    """..."""
    list_objects.side_effect = utils.affect_by_identifier(
        list_versions=utils.make_list_objects_response(contents=[])
    )
    command.run(['info', 'fake-package'])


@patch('pipper.s3.list_objects')
@utils.PatchSession()
def test_info_local(boto_mocks: utils.BotoMocks, list_objects: MagicMock):
    """..."""
    list_objects.side_effect = utils.affect_by_identifier(
        list_versions=utils.make_list_objects_response(contents=[])
    )
    command.run(['info', 'fake-package', '--local'])
