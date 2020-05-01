import pytest
from vizel.cli import main
from click.testing import CliRunner
from os import stat, unlink, path


@pytest.fixture(params=['data/zettelkasten_md/', 'data/zettelkasten_txt/'])
def zettelkasten_directory(request):
    return request.param


def test_stats(zettelkasten_directory):
    runner = CliRunner()
    result = runner.invoke(main, ['stats', zettelkasten_directory])

    assert result.exit_code == 0
    expected_output = (
        '4 Zettel\n'
        '3 references between Zettel\n'
        '1 Zettel with no references\n'
        '2 connected components\n'
    )
    assert result.output == expected_output


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


def test_unconnected(zettelkasten_directory):
    runner = CliRunner()
    result = runner.invoke(main, ['unconnected', zettelkasten_directory])

    assert result.exit_code == 0

    expected_file_ending = zettelkasten_directory.rpartition('_')[2].rstrip('/')
    expected_output = (
        '202005011017\t202005011017_All_by_myself.{}\n'.format(expected_file_ending)
    )
    assert result.output == expected_output
