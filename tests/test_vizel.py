from pathlib import Path

from vizel.cli import main
from click.testing import CliRunner


def test_stats():
    runner = CliRunner()
    result = runner.invoke(main, ['stats', 'data/'])

    assert result.exit_code == 0
    expected = (
        '4 Zettel\n'
        '3 references between Zettel\n'
        '1 Zettel with no references\n'
        '2 connected components\n'
    )
    assert expected == result.output


def test_graph_pdf_default(tmp_path):
    runner = CliRunner()
    pdf_path = Path('vizel_graph.pdf')
    result = runner.invoke(main, ['graph-pdf', 'data/'])

    assert result.exit_code == 0
    assert pdf_path.stat().st_size > 0

    pdf_path.unlink()


def test_graph_pdf_set_name(tmp_path):
    runner = CliRunner()
    pdf_path = tmp_path / 'zettelkasten_custom_name.pdf'
    result = runner.invoke(main, ['graph-pdf', 'data/', '--pdf-name', f'{pdf_path}'])

    assert result.exit_code == 0
    assert pdf_path.stat().st_size > 0
