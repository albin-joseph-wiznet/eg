from collections import namedtuple
from mock import patch

from eg import core
from test.util_test import _create_config


# ArgumentParser.parse_args() returns an object with fields we can access via
# dot notation. This namedtuple will stand in for that in testing.
MockArgs = namedtuple(
    'Args',
    [
        'config_file',
        'examples_dir',
        'custom_dir',
        'use_color',
        'pager_cmd',
        'squeeze',
        'list',
        'version',
        'program',
        'edit',
    ]
)


def _create_mock_args(
    config_file=None,
    examples_dir=None,
    custom_dir=None,
    use_color=None,
    pager_cmd=None,
    version=False,
    list=False,
    squeeze=None,
    program=None,
    edit=False,
):
    """Helper to create an argument named tuple."""
    return MockArgs(
        config_file=config_file,
        examples_dir=examples_dir,
        custom_dir=custom_dir,
        use_color=use_color,
        pager_cmd=pager_cmd,
        version=version,
        list=list,
        squeeze=squeeze,
        program=program,
        edit=edit,
    )


@patch('sys.argv', new=['eg'])
@patch('argparse.ArgumentParser.print_help')
@patch('argparse.ArgumentParser.exit')
def test_parse_args_fewer_than_two_args_fails(mock_help, mock_exit):
    """
    You always need at least two arguments in argv: eg and a command.
    """
    core._parse_arguments()
    mock_help.assert_called_once_with()
    mock_exit.assert_called_once_with()


@patch('sys.argv', new=['eg', '--color'])
@patch('argparse.ArgumentParser.error')
@patch(
    'argparse.ArgumentParser.parse_args',
    return_value=_create_mock_args(use_color=True)
)
def test_parse_args_requires_version_list_or_program(
    mock_parse_args,
    mock_error
):
    """
    A valid argument configuration requires at least version, list, or program.
    """
    core._parse_arguments()
    mock_error.assert_called_once_with(core._MSG_BAD_ARGS)


@patch('argparse.ArgumentParser.error')
@patch('argparse.ArgumentParser.print_help')
@patch('argparse.ArgumentParser.exit')
def _helper_parses_correctly(
    additional_argv,
    expected_args,
    mock_exit,
    mock_help,
    mock_error
):
    """
    Helper method for assertions about successful argument parsing.
    """
    # For convenience, we will always include a default program here. This
    # saves callers from appending a program to all of their additional_argv,
    # and it is assumed that the special casing for when a program is passed vs
    # not will be handled elsewhere. This is a helper for asserting that our
    # calling API is as expected.
    #
    # It isn't clear if the ArgumentParser object is supposed to expose the
    # fact that it calls sys.argv for testing. We might be breaking
    # encapsulation of the API a bit, but it facilitates our own API testing
    # enough that it seems like a reasonable risk.
    default_program = 'du'
    argv = ['eg'] + additional_argv + [default_program]

    with patch('sys.argv', new=argv):
        actual_args = core._parse_arguments()
        assert actual_args.config_file == expected_args.config_file
        assert actual_args.custom_dir == expected_args.custom_dir
        assert actual_args.examples_dir == expected_args.examples_dir
        assert actual_args.list == expected_args.list
        assert actual_args.pager_cmd == expected_args.pager_cmd
        assert actual_args.use_color == expected_args.use_color
        assert actual_args.squeeze == expected_args.squeeze
        assert actual_args.version == expected_args.version
        assert actual_args.edit == expected_args.edit
        # Note that here we use the default, as described above.
        assert actual_args.program == default_program

        # Now make sure we didn't call any other parser methods
        assert mock_exit.call_args_list == []
        assert mock_help.call_args_list == []
        assert mock_error.call_args_list == []


def test_parses_correctly_if_just_program():
    """
    Parses correctly when only a program, with no options, are given.
    """
    expected_args = _create_mock_args()
    _helper_parses_correctly([], expected_args)


def test_parses_version_correctly():
    """
    Parses the long and short version flags.
    """
    expected_args = _create_mock_args(version=True)

    _helper_parses_correctly(['-v'], expected_args)
    _helper_parses_correctly(['--version'], expected_args)


def test_parses_config_file_correctly():
    """
    Parses the long and short config file flags.
    """
    config_file = 'path/to/.egrc'
    expected_args = _create_mock_args(config_file=config_file)

    _helper_parses_correctly(['-f', config_file], expected_args)
    _helper_parses_correctly(['--config-file', config_file], expected_args)


def test_parses_examples_dir_correctly():
    """
    Parses the long and short example dir flags.
    """
    examples_dir = 'path/to/examples'
    expected_args = _create_mock_args(examples_dir=examples_dir)

    _helper_parses_correctly(['--examples-dir', examples_dir], expected_args)


def test_parses_custom_dir_correctly():
    """
    Parses the long and short custom dir flags.
    """
    custom_dir = 'path/to/custom'
    expected_args = _create_mock_args(custom_dir=custom_dir)

    _helper_parses_correctly(['-c', custom_dir], expected_args)
    _helper_parses_correctly(['--custom-dir', custom_dir], expected_args)


def test_parses_pager_cmd_correctly():
    """
    Parses the long and short pager cmd flags.
    """
    pager_cmd = 'less -R'
    expected_args = _create_mock_args(pager_cmd=pager_cmd)

    _helper_parses_correctly(['-p', pager_cmd], expected_args)
    _helper_parses_correctly(['--pager-cmd', pager_cmd], expected_args)


def test_parses_edit_correctly():
    """
    Parses the long and short edit flags.
    """
    expected_args = _create_mock_args(edit=True)

    _helper_parses_correctly(['-e'], expected_args)
    _helper_parses_correctly(['--edit'], expected_args)


def test_parses_list_correctly():
    """
    Parses the long and short list flags.
    """
    expected_args = _create_mock_args(list=True)

    _helper_parses_correctly(['-l'], expected_args)
    _helper_parses_correctly(['--list'], expected_args)


def test_parses_use_color_correctly():
    """
    Parses the use color flags.
    """
    expected_args = _create_mock_args(use_color=True)

    _helper_parses_correctly(['--color'], expected_args)


def test_parses_no_color_correctly():
    """
    Parses the no color flags.
    """
    expected_args = _create_mock_args(use_color=False)

    _helper_parses_correctly(['--no-color'], expected_args)


def test_parses_squeeze_correctly():
    """
    Parses the long and short squeeze flags.
    """
    expected_args = _create_mock_args(squeeze=True)

    _helper_parses_correctly(['-s'], expected_args)
    _helper_parses_correctly(['--squeeze'], expected_args)


def test_parses_all_valid_options_simultaneously():
    """
    Parses a large number of valid options at the same time.
    """
    config_file = 'path/to/config/file'
    examples_dir = 'path/to/examples'
    custom_dir = 'path/to/custom'
    pager_cmd = 'less -R'
    argv = [
        '--config-file=' + config_file,
        '--examples-dir',
        examples_dir,
        '-c',
        custom_dir,
        '--squeeze',
        '--no-color',
        '--pager-cmd',
        pager_cmd,
    ]

    expected_args = _create_mock_args(
        config_file=config_file,
        examples_dir=examples_dir,
        custom_dir=custom_dir,
        use_color=False,
        pager_cmd=pager_cmd,
        version=False,
        list=False,
        squeeze=True,
    )

    _helper_parses_correctly(argv, expected_args)


@patch('eg.util.edit_custom_examples')
@patch('eg.core._handle_no_editor')
@patch('eg.core._parse_arguments')
@patch('eg.util.handle_program')
@patch('eg.core._show_version')
@patch('eg.core._show_list_message')
@patch('eg.config.get_resolved_config')
def _helper_run_eg_responds_to_args_correctly(
    args,
    mock_resolved_config,
    mock_show_list,
    mock_show_version,
    mock_handle_program,
    mock_parse_args,
    mock_no_editor,
    mock_edit_custom,
    resolved_config='stand-in-config',
    call_show_list=False,
    call_show_version=False,
    call_handle_program=False,
    call_no_editor=False,
    call_edit_custom=False,
):
    """
    Helper method for verifying the results of calls to run_eg.
    """
    mock_resolved_config.return_value = resolved_config
    mock_parse_args.return_value = args

    core.run_eg()

    if (call_show_list):
        mock_show_list.assert_called_once_with(resolved_config)
    else:
        assert mock_show_list.call_args_list == []

    if (call_show_version):
        mock_show_version.assert_called_once_with()
    else:
        assert mock_show_version.call_args_list == []

    if (call_no_editor):
        mock_no_editor.assert_called_once_with()
    else:
        assert mock_no_editor.call_args_list == []

    if (call_edit_custom):
        mock_edit_custom.assert_called_once_with(args.program, resolved_config)
    else:
        assert mock_edit_custom.call_args_list == []

    if (call_handle_program):
        mock_handle_program.assert_called_once_with(
            args.program, resolved_config
        )
    else:
        assert mock_handle_program.call_args_list == []


def test_shows_version():
    """
    Should show version if args.version is true.
    """
    args = _create_mock_args(version=True)
    _helper_run_eg_responds_to_args_correctly(args, call_show_version=True)


def test_shows_list():
    """
    Should show list of programs if args.list is true.
    """
    args = _create_mock_args(list=True)
    _helper_run_eg_responds_to_args_correctly(args, call_show_list=True)


def test_calls_handle_program():
    """
    Without list and version, should call handle program with our config.
    """
    args = _create_mock_args(program='awk')
    _helper_run_eg_responds_to_args_correctly(args, call_handle_program=True)


def test_run_eg_informs_if_no_editor():
    """
    Inform the user if they've requested to use an editor but we can't find
    one.
    """
    args = _create_mock_args(program='awk', edit=True)
    config_no_editor = _create_config(editor_cmd=None)
    _helper_run_eg_responds_to_args_correctly(
        args, call_no_editor=True, resolved_config=config_no_editor
    )


def test_run_eg_opens_editor():
    """
    If the user requests an edit we should open the editor.
    """
    args = _create_mock_args(program='awk', edit=True)
    config_with_editor = _create_config(editor_cmd='vi -e')
    _helper_run_eg_responds_to_args_correctly(
        args, call_edit_custom=True, resolved_config=config_with_editor
    )
