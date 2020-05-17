import re
import glob
import os.path
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


def _get_short_description(zettel_filename):
    """
    Creates a short description out of the Zettel filename.
    :param zettel_filename: Filename of the Zettel
    :return: 50 character long string
    """

    # Create a short, 50 character, description
    replace_with_space = ['_', '-']
    remove = ['.md', '.txt']
    short_des = zettel_filename

    for replace_char in replace_with_space:
        short_des = short_des.replace(replace_char, ' ')

    for remove_char in remove:
        short_des = short_des.replace(remove_char, '')

    return short_des


def _get_digraph(zettel_directory_path):
    """
    Parses the Zettel in `zettel_directory` and returns a digraph.

    :param zettel_directory_path Path to directory where the Zettel are stored.
    :return DiGraph object representing the Zettel graph.
    """

    digraph = nx.DiGraph()

    for zettel_path in glob.glob(os.path.join(zettel_directory_path, '*[.md|.txt]')):

        zettel_filename = os.path.basename(zettel_path)
        short_des = _get_short_description(zettel_filename)

        digraph.add_node(zettel_filename, short_description=short_des, path=zettel_path)

        with open(zettel_path, 'r') as zettel_file:
            zettel_text = zettel_file.read()

            for reference_id in _load_references(zettel_text):
                digraph.add_edge(zettel_filename, reference_id)

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
@click.option('--pdf-name', default='vizel_graph.pdf',
              help='Name of the PDF file the graph is written into. Default: vizel_graph.pdf')
def graph_pdf(directory, pdf_name):
    """
    Generates a PDF of the graph spanned by Zettel in DIRECTORY.
    \f

    :param directory: Directory where all the Zettel are.
    :param pdf_name: Name of the PDF file the graph is written into.
    :return None
    """

    digraph = _get_digraph(directory)

    dot = Digraph(comment='Zettelkasten Graph')

    for (node, data) in digraph.nodes(data=True):
        dot.node(node, data['short_description'])

    for u, v in digraph.edges:
        dot.edge(u, v)

    # Remove the last `.pdf` ending if present
    if pdf_name.endswith('.pdf'):
        pdf_name = pdf_name.rpartition('.pdf')[0]
    dot.render(pdf_name, cleanup=True)


@main.command(short_help='Stats of Zettel graph')
@click.argument('directory', type=click.Path(exists=True, dir_okay=True))
def stats(directory):
    """
    Prints the stats of the graph spanned by Zettel in DIRECTORY.

    \b
    Stats calculated :
    - Number of Zettel
    - Number of references between Zettel (including bi-directional and duplicate)
    - Number of Zettel without any reference from or to a Zettel
    - Number of connected components
    \f

    :param directory: Directory where all the Zettel are.
    :return None
    """

    digraph = _get_digraph(directory)

    click.echo('{} Zettel'.format(digraph.number_of_nodes()))
    click.echo('{} references between Zettel'.format(digraph.number_of_edges()))

    n_nodes_no_edges = len(_get_zero_degree_nodes(digraph))
    click.echo('{} Zettel with no references'.format(n_nodes_no_edges))

    click.echo('{} connected components'.format(nx.number_connected_components(digraph.to_undirected())))


@main.command(short_help='Zettel without references')
@click.argument('directory', type=click.Path(exists=True, dir_okay=True))
def unconnected(directory):
    """
    Prints all of the Zettel in DIRECTORY that have no in- or outgoing references.

    \f

    :param directory: Directory where all the Zettel are.
    :return None
    """

    digraph = _get_digraph(directory)

    zero_degree_nodes = _get_zero_degree_nodes(digraph)

    for node in zero_degree_nodes:
        filename = os.path.basename(digraph.nodes[node]['path'])
        click.echo('{}\t{}'.format(node, filename))
