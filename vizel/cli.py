import re
from pathlib import Path

import networkx as nx
import click
from graphviz import Digraph


@click.group()
def main():
    # TODO Collect directory here and create digraph object
    pass


def _load_references(zettel_text):
    """
    Parses `zettel_text` for references to other Zettel.

    :param zettel_text String of the Zettel content.
    :return List of Zettel id's that `zettel_text` references.
    """
    return re.findall('\[\[(\w{12})\]\]', zettel_text)


def _get_zettel_id(zettel_path):
    """
    Returns the ID of the Zettel that lies at `zettel_path`.

    :param zettel_path: PosixPath object that points to a Zettel.
    :return The ID of the Zettel or NONE. 
    """
    # TODO Also support text files
    match = re.search('(\w{12}).*\.md', zettel_path.name)

    if match:
        return match.group(1)
    else:
        return None


def _get_digraph(zettel_directory_path):
    """
    Parses the Zettel in `zettel_directory` and returns a digraph.

    :param zettel_directory_path PosixPath to directory where the Zettel are stored.
    :return DiGraph object representing the Zettel graph.
    """

    digraph = nx.DiGraph()

    for zettel_path in zettel_directory_path.glob('*.md'):
        zettel_id = _get_zettel_id(zettel_path)

        # Create a short, 50 character, description on two lines
        zettel_short_description = zettel_id + '\n' + zettel_path.name.replace('_', ' ').replace('.md', '')[13:63]

        digraph.add_node(zettel_id, short_description=zettel_short_description, path=zettel_path)

        with open(zettel_path, 'r') as zettel_file:
            zettel_text = zettel_file.read()

            for reference_id in _load_references(zettel_text):
                digraph.add_edge(zettel_id, reference_id)

    return digraph


def _get_zero_degree_nodes(digraph):
    """
    Get all the nodes that have degree zero

    :param digraph: DiGraph object representing the Zettel graph.
    :return: List of nodes from `digraph` where degree is 0. 
    """

    return [node for node, degree in digraph.degree() if degree == 0]


@main.command(short_help='PDF of Zettel graph')
@click.argument('directory', type=click.Path(exists=True, dir_okay=True))
@click.option('--pdf-name', default='vizel_graph',
              help='Name of the PDF file the graph is written into. Default: vizel_graph')
def graph_pdf(directory, pdf_name):
    """
    Generates a PDF of the graph spanned by Zettel in DIRECTORY.
    \f

    :param directory: Directory where all the Zettel are.
    :param pdf_name: Name of the PDF file the graph is written into.
    :return None
    """

    digraph = _get_digraph(Path(directory))

    dot = Digraph(comment='Zettelkasten Graph')

    for (node, data) in digraph.nodes(data=True):
        dot.node(node, data['short_description'])

    for u, v in digraph.edges:
        dot.edge(u, v)

    dot.render(pdf_name, cleanup=True)


@main.command()
@click.argument('directory', type=click.Path(exists=True, dir_okay=True))
def print_stats(directory):
    """
    Prints the stats of the Zettel graph

    :param directory: Directory where all the Zettel are.
    :return None
    """

    digraph = _get_digraph(Path(directory))

    click.echo(f'{digraph.number_of_nodes()} Zettel')
    click.echo(f'{digraph.number_of_edges()} references between Zettel')

    n_nodes_no_edges = len(_get_zero_degree_nodes(digraph))
    click.echo(f'{n_nodes_no_edges} Zettel with no references')

    click.echo(f'{nx.number_connected_components(digraph.to_undirected())} connected components')


@main.command()
@click.argument('directory', type=click.Path(exists=True, dir_okay=True))
def print_unconnected(directory):
    """
    Prints all of the Zettel that have no in- or outgoing connections

    :param directory: Directory where all the Zettel are.
    :return None
    """

    digraph = _get_digraph(Path(directory))

    zero_degree_nodes = _get_zero_degree_nodes(digraph)

    for node in zero_degree_nodes:
        filename = digraph.nodes[node]['path'].name
        click.echo(f'{node}\t{filename}')
