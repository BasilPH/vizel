from vizel.vizel import load_references, get_digraph
from pathlib import Path


def test_load_references():
    with open('../tests/data/202002251025_This_is_the_first_test_zettel.md', 'r') as test_zettel_file:
        test_zettel_text = test_zettel_file.read()

        assert load_references(test_zettel_text) == ['202002241029', '202003211727', '202003211643', ]


def test_get_graph():
    graph = get_digraph(Path('data'))

    assert graph.number_of_nodes() == 5
    assert graph.number_of_edges() == 6
