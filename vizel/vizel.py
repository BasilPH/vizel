import re
from pathlib import Path

import networkx as nx
import click
from graphviz import Digraph


def load_references(zettel_text):
    """
    Parses `zettel_text` for references to other Zettel.
    :param zettel_text String of the Zettel content.

    return: List of Zettel id's that `zettel_text` references.
    """
    return re.findall('\[\[(\w{12})\]\]', zettel_text)


def get_zettel_id(zettel_path):
    """
    Returns the ID of the Zettel that lies at `zettel_path`.
    :param zettel_path: PosixPath object that points to a Zettel.
    :return: The ID of the Zettel or NONE. 
    """
    match = re.search('(\w{12}).*\.md', zettel_path.name)

    if match:
        return match.group(1)
    else:
        return None


def get_digraph(zettel_directory_path):
    """
    Parses the Zettel in `zettel_directory` and returns a digraph.

    :param zettel_directory_path PosixPath to directory where the Zettel are stored.

    return: DiGraph object representing the Zettel graph.
    """

    digraph = nx.DiGraph()

    for zettel_path in zettel_directory_path.glob('*.md'):
        zettel_id = get_zettel_id(zettel_path)

        digraph.add_node(zettel_id)

        with open(zettel_path, 'r') as zettel_file:
            zettel_text = zettel_file.read()

            for reference_id in load_references(zettel_text):
                digraph.add_edge(zettel_id, reference_id)

    return digraph


def draw_digraph(digraph, output_file_string):
    """
    Draw the networkx digraph.
    :param graph: networkx DiGraph object.
    :param output_file_string: String that represents the output path.
    :return: None
    """

    dot = Digraph(comment='Zettelkasten Graph')

    for node in digraph.nodes:
        dot.node(node)

    for u, v in digraph.edges:
        dot.edge(u, v)

    dot.render(output_file_string, cleanup=True)


def print_stats(digraph):
    """
    Prints the stats of `digraph` to console.
    :param digraph: networkx DiGraph object.
    :return: None
    """

    n_nodes_no_edges = len([node for node, degree in digraph.degree() if degree == 0])
    click.echo(f'{n_nodes_no_edges} Zettel with no references')

    click.echo(f'{nx.number_connected_components(digraph.to_undirected())} connected components')


@click.command()
@click.argument('directory', type=click.Path(exists=True, dir_okay=True))
@click.option('--pdf-name', default='zettelkasten_vizel')
@click.option('--print-pdf', 'flag_print_pdf', is_flag=True)
@click.option('--print-stats', 'flag_print_stats', is_flag=True)
def vizel(directory, pdf_name, flag_print_pdf, flag_print_stats):
    """Visualize a digraph of Zettel stored in DIRECTORY"""

    digraph = get_digraph(Path(directory))

    if flag_print_pdf:
        draw_digraph(digraph, pdf_name)

    if flag_print_stats:
        print_stats(digraph)


if __name__ == '__main__':
    vizel()
