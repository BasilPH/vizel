from vizel.cli import main
from click.testing import CliRunner


def test_stats():
    runner = CliRunner()
    result = runner.invoke(main, ['stats', 'data/'])
    assert result.exit_code == 0
    expected = (
        '5 Zettel\n'
        '6 references between Zettel\n'
        '0 Zettel with no references\n'
        '1 connected components\n'
    )
    assert expected == result.output
