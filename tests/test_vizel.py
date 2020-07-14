from os import stat, unlink, path

import pytest
import six
from click.testing import CliRunner

from vizel.cli import main


@pytest.fixture(params=['data/zettelkasten_md/', 'data/zettelkasten_txt/'])
def zettelkasten_directory(request):
    # Path to the `tests` folder
    base_dir = path.dirname(path.abspath(__file__))
    return path.join(base_dir, request.param)


@pytest.fixture()
def stderr_expected(zettelkasten_directory):
    # Python 2.7 has a different default codec and therefore a different UnicodeDecodeError message
    python2_unicode_decode_message = ('Skipping 202006112225_broken_utf8.{ext}: \'ascii\' codec can\'t decode'
                                      ' byte 0xff in position 0: ordinal not in range(128)\n')
    python3_unicode_decode_message = ('Skipping 202006112225_broken_utf8.{ext}: \'utf-8\' codec can\'t decode'
                                      ' byte 0xff in position 0: invalid start byte\n')

    expected_file_ending = zettelkasten_directory.rpartition('_')[2].rstrip('/')

    stderr_out = (
        'No matching Zettel for reference "03272020061037-eda-artifacts.{ext}" '
        'in 03272020061037-electrodermal-activity.{ext}\n'
        'No matching Zettel for reference "LINK" in 03272020061037-electrodermal-activity.{ext}\n'
        'No matching Zettel for reference "202005171153" in 202002241029_Broken_references_Zettel.{ext}\n'
        'Skipping non-unique reference "2020" in 202002241029_Broken_references_Zettel.{ext}. Candidates: '
        '202002241029_Broken_references_Zettel.{ext}, 202002251025_This_is_the_first_test_zettel.{ext}, '
        '202003211727_This_is_the_second_test_zettel.{ext}, 202005011017_All_by_myself.{ext}, '
        '202006112225_broken_utf8.{ext}\n'
    )

    stderr_out += python2_unicode_decode_message if six.PY2 else python3_unicode_decode_message

    return stderr_out.format(ext=expected_file_ending)


def test_stats(zettelkasten_directory, stderr_expected):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, ['stats', zettelkasten_directory])

    assert result.exit_code == 0
    stdout_output = (
        '7 Zettel\n'
        '6 references between Zettel\n'
        '2 Zettel with no references\n'
        '3 connected components\n'
    )
    assert result.stdout == stdout_output

    assert result.stderr == stderr_expected


def test_graph_pdf_default(zettelkasten_directory):
    runner = CliRunner()
    pdf_path = 'vizel_graph.pdf'
    result = runner.invoke(main, ['graph-pdf', zettelkasten_directory])

    assert result.exit_code == 0
    assert stat(pdf_path).st_size > 0

    unlink(pdf_path)


def test_graph_pdf_set_name(tmp_path, zettelkasten_directory):
    runner = CliRunner()
    pdf_path = path.join(str(tmp_path), 'zettelkasten_custom_name.pdf')
    result = runner.invoke(main, ['graph-pdf', zettelkasten_directory, '--pdf-name', pdf_path])

    assert result.exit_code == 0
    assert stat(pdf_path).st_size > 0

    unlink(pdf_path)


def test_unconnected(zettelkasten_directory, stderr_expected):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, ['unconnected', zettelkasten_directory])

    assert result.exit_code == 0

    expected_file_ending = zettelkasten_directory.rpartition('_')[2].rstrip('/')

    stdout_expected = (
        '202005011017_All_by_myself.{ext}\n'
        '202006112225_broken_utf8.{ext}\n'
    )
    assert result.stdout == stdout_expected.format(ext=expected_file_ending)

    assert result.stderr == stderr_expected.format(ext=expected_file_ending)


def test_components(zettelkasten_directory, stderr_expected):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, ['components', zettelkasten_directory])

    assert result.exit_code == 0

    expected_file_ending = zettelkasten_directory.rpartition('_')[2].rstrip('/')

    stdout_expected = (
        '# Component 1\n'
        '202002241029_Broken_references_Zettel.{ext}\n'
        '202002251025_This_is_the_first_test_zettel.{ext}\n'
        '202003211727_This_is_the_second_test_zettel.{ext}\n\n'
        '# Component 2\n'
        '03242020003215-eda-explained.{ext}\n'
        '03272020061037-electrodermal-activity.{ext}\n\n'
        '# Component 3\n'
        '202005011017_All_by_myself.{ext}\n\n'
        '# Component 4\n'
        '202006112225_broken_utf8.{ext}\n\n'
    )
    assert result.stdout == stdout_expected.format(ext=expected_file_ending)

    assert result.stderr == stderr_expected.format(ext=expected_file_ending)
