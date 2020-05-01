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
