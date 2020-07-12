import glob
import os.path
import re

import click
import networkx as nx
import six
from graphviz import Digraph


@click.group()
def main():
    # TODO Collect directory here and create digraph object
    pass


def _extract_valid_references(reference_regexp, zettel_path, zettel_filenames):
    """
    Extracts references from a Zettel that match a reference and that point to exactly one existing file.

    Throws a UnicodeDecodeError if the file content can't be converted to unicode.

    :param reference_regexp: Regexp that matches the references with one matching group.
    :param zettel_path: Path to the Zettel we parse for references.
    :param zettel_filenames: List of filenames in the Zettel directory.
    :return: Filenames of Zettel that are referenced.
    """
    references = []
    with open(zettel_path, 'r') as zettel_file:
        zettel_text = zettel_file.read()

        # Internally we only want to deal with unicode
        if six.PY2:
            zettel_text = unicode(zettel_text, errors='strict')

    reference_texts = re.findall(reference_regexp, zettel_text)
    for reference_text in reference_texts:
        matching_zettel_filenames = []
        for zettel_filename in zettel_filenames:
            if zettel_filename.startswith(reference_text):
                matching_zettel_filenames.append(zettel_filename)

        if len(matching_zettel_filenames) == 1:
            references += matching_zettel_filenames
        elif len(matching_zettel_filenames) > 1:
            click.echo(
                'Skipping non-unique reference "{}" in {}. Candidates: {}'.format(reference_text,
                                                                                  os.path.basename(zettel_path),
                                                                                  ', '.join(
                                                                                      matching_zettel_filenames)),
                err=True)
        else:
            click.echo(
                'No matching Zettel for reference "{}" in {}'.format(reference_text, os.path.basename(zettel_path)),
                err=True)
    return references


def _load_references(zettel_path, zettel_directory_path):
    """
    Parses the content of `zettel_path` for references to other Zettel.

    :param zettel_path: Path to the Zettel we parse for references.
    :param zettel_directory_path Path to directory where the Zettel are stored.
    :return List of filenames of referenced Zettel.
    """
    references = []
    zettel_filenames = sorted(
        [os.path.basename(f) for f in glob.glob(os.path.join(zettel_directory_path, '*[.md|.txt]'))])

    # Extract references for the [[ID]] link format
    # Look for [[, and then match anything that isn't ]]. End with ]].
    references += _extract_valid_references('\[\[([^\]\]]+)\]\]', zettel_path, zettel_filenames)

    # Extract references for the markdown link format
    # Look for [, and then match anything that isn't ]. Then look for ( and match anything that isn't ). End with ).
    references += _extract_valid_references('\[[^\]]+\]\(([^\)]+)\)', zettel_path, zettel_filenames)

    return references


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

    for zettel_path in sorted(glob.glob(os.path.join(zettel_directory_path, '*[.md|.txt]'))):

        zettel_filename = os.path.basename(zettel_path)
        short_des = _get_short_description(zettel_filename)

        digraph.add_node(zettel_filename, short_description=short_des, path=zettel_path)

        try:
            for reference_zettel_filename in _load_references(zettel_path, zettel_directory_path):
                if zettel_filename != reference_zettel_filename:
                    digraph.add_edge(zettel_filename, reference_zettel_filename)
        except UnicodeDecodeError as e:
            click.echo('Skipping {}: {}'.format(zettel_filename, e), err=True)
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

    for node in sorted(zero_degree_nodes):
        click.echo('{}'.format(node))
