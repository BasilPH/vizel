import glob
import os.path
import re
from operator import itemgetter

import click
import networkx as nx
import six
from graphviz import Digraph


class Logger:
    """
    This class wraps `click.echo` and provides two log-levels: info and warning.

    The class is instantiated with `Logger.initialize`. If `suppress_warnings=True` is passed, all calls to `warning`
    will not result in any output.

    After initialization the singleton instance needs to be retrieved with `Logger.get`.
    """

    __instance = None

    def __init__(self, suppress_warnings):
        self.suppress_warnings = suppress_warnings
        Logger.__instance = self

    @staticmethod
    def initialize(suppress_warnings):
        """
        Initialize the Logger singleton instance.

        :param suppress_warnings: If set to `True`, all calls to `warning` will not result in any output.
        :return: None
        """
        Logger(suppress_warnings)

    @staticmethod
    def get():
        """
        Returns a singleton Logger instance. `Logger.initialize` must have been called at least once before.

        :return: Logger instance
        """
        if Logger.__instance is None:
            raise Exception("Logger not initialized. Call `initialize` first.")
        return Logger.__instance

    def info(self, message):
        """
        Prints a message to stdout using `click.echo`.

        :param message: Info message to be printed.
        :return: None
        """
        click.echo(message)

    def warning(self, message):
        """
        Prints a message to stderr using `click.echo`. If `suppress_warnings=True`, nothing is printed.
        :param message: Warning message to be printed.
        :return: None
        """
        if not self.suppress_warnings:
            click.echo(message, err=True)


@click.group()
def main():
    """
     See the stats and connections of your Zettelkasten.
     \f

    :return: None
    """
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

    logger = Logger.get()

    references = []
    with open(zettel_path, "r") as zettel_file:
        zettel_text = zettel_file.read()

        # Internally we only want to deal with unicode
        if six.PY2:
            zettel_text = unicode(zettel_text, errors="strict")

    reference_texts = re.findall(reference_regexp, zettel_text)
    for reference_text in reference_texts:
        matching_zettel_filenames = []
        for zettel_filename in zettel_filenames:
            if zettel_filename.startswith(reference_text):
                matching_zettel_filenames.append(zettel_filename)

        if len(matching_zettel_filenames) == 1:
            references += matching_zettel_filenames
        elif len(matching_zettel_filenames) > 1:
            logger.warning(
                'Skipping non-unique reference "{}" in {}. Candidates: {}'.format(
                    reference_text, os.path.basename(zettel_path), ", ".join(matching_zettel_filenames)
                )
            )
        else:
            logger.warning(
                'No matching Zettel for reference "{}" in {}'.format(reference_text, os.path.basename(zettel_path))
            )
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
        [os.path.basename(f) for f in glob.glob(os.path.join(zettel_directory_path, "*[.md|.txt]"))]
    )

    # Extract references for the [[ID]] link format
    # Look for [[, and then match anything that isn't ]]. End with ]].
    references += _extract_valid_references("\[\[([^\]\]]+)\]\]", zettel_path, zettel_filenames)

    # Extract references for the markdown link format
    # Look for [, and then match anything that isn't ]. Then look for ( and match anything that isn't ). End with ).
    references += _extract_valid_references("\[[^\]]+\]\(([^\)]+)\)", zettel_path, zettel_filenames)

    return references


def _get_short_description(zettel_filename):
    """
    Creates a short description out of the Zettel filename.
    :param zettel_filename: Filename of the Zettel
    :return: 50 character long string
    """

    # Create a short, 50 character, description
    replace_with_space = ["_", "-"]
    remove = [".md", ".txt"]
    short_des = zettel_filename

    for replace_char in replace_with_space:
        short_des = short_des.replace(replace_char, " ")

    for remove_char in remove:
        short_des = short_des.replace(remove_char, "")

    return short_des


def _get_digraph(zettel_directory_path):
    """
    Parses the Zettel in `zettel_directory` and returns a digraph.

    :param zettel_directory_path Path to directory where the Zettel are stored.
    :return DiGraph object representing the Zettel graph.
    """
    logger = Logger.get()
    digraph = nx.DiGraph()

    for zettel_path in sorted(glob.glob(os.path.join(zettel_directory_path, "*[.md|.txt]"))):

        zettel_filename = os.path.basename(zettel_path)
        short_des = _get_short_description(zettel_filename)

        digraph.add_node(zettel_filename, short_description=short_des, path=zettel_path)

        try:
            for reference_zettel_filename in _load_references(zettel_path, zettel_directory_path):
                if zettel_filename != reference_zettel_filename:
                    digraph.add_edge(zettel_filename, reference_zettel_filename)
        except UnicodeDecodeError as e:
            logger.warning("Skipping {}: {}".format(zettel_filename, e))
    return digraph


def _get_zero_degree_nodes(digraph):
    """
    Get all the nodes that have degree zero

    :param digraph: DiGraph object representing the Zettel graph.
    :return: List of nodes from `digraph` where degree is 0.
    """

    return [node for node, degree in digraph.degree() if degree == 0]


@main.command(short_help="PDF of Zettel graph")
@click.argument("directory", type=click.Path(exists=True, dir_okay=True))
@click.option(
    "--pdf-name",
    default="vizel_graph.pdf",
    help="Name of the PDF file the graph is written into. Default: vizel_graph.pdf",
)
def graph_pdf(directory, pdf_name):
    """
    Generates a PDF of the graph spanned by Zettel in DIRECTORY.
    \f

    :param directory: Directory where all the Zettel are.
    :param pdf_name: Name of the PDF file the graph is written into.
    :return None
    """

    digraph = _get_digraph(directory)

    dot = Digraph(comment="Zettelkasten Graph")

    for (node, data) in digraph.nodes(data=True):
        dot.node(node, data["short_description"])

    for u, v in digraph.edges:
        dot.edge(u, v)

    # Remove the last `.pdf` ending if present
    if pdf_name.endswith(".pdf"):
        pdf_name = pdf_name.rpartition(".pdf")[0]
    dot.render(pdf_name, cleanup=True)


@main.command(short_help="Stats of Zettel graph")
@click.argument("directory", type=click.Path(exists=True, dir_okay=True))
@click.option("-q", "--quiet", is_flag=True, help="Quiet mode")
def stats(directory, quiet):
    """
    Prints the stats of the graph spanned by Zettel in DIRECTORY.

    \b
    Stats calculated :
    - Number of Zettel
    - Number of references between Zettel (including bi-directional and duplicate)
    - Number of Zettel without any reference from or to a Zettel
    - Number of connected components
    \f

    :param quiet: When set to True, warnings will not be printed.
    :param directory: Directory where all the Zettel are.
    :return None
    """
    Logger.initialize(suppress_warnings=quiet)
    logger = Logger.get()
    digraph = _get_digraph(directory)

    logger.info("{} Zettel".format(digraph.number_of_nodes()))
    logger.info("{} references between Zettel".format(digraph.number_of_edges()))

    n_nodes_no_edges = len(_get_zero_degree_nodes(digraph))
    logger.info("{} Zettel with no references".format(n_nodes_no_edges))

    logger.info("{} connected components".format(nx.number_connected_components(digraph.to_undirected())))


@main.command(short_help="Zettel without references")
@click.argument("directory", type=click.Path(exists=True, dir_okay=True))
@click.option("-q", "--quiet", is_flag=True, default=False, help="Quiet mode")
def unconnected(directory, quiet):
    """
    Prints all of the Zettel in DIRECTORY that have no in- or outgoing references.

    \f

    :param directory: Directory where all the Zettel are.
    :param quiet: When set to True, warnings will not be printed.
    :return None
    """
    Logger.initialize(suppress_warnings=quiet)
    logger = Logger.get()
    digraph = _get_digraph(directory)

    zero_degree_nodes = _get_zero_degree_nodes(digraph)

    for node in sorted(zero_degree_nodes):
        logger.info("{}".format(node))


@main.command(short_help="Connected components")
@click.argument("directory", type=click.Path(exists=True, dir_okay=True))
@click.option("-q", "--quiet", is_flag=True, default=False, help="Quiet mode")
def components(directory, quiet):
    """
    Lists the connected components and their Zettel in DIRECTORY.

    \f

    :param directory: Directory where all the Zettel are.
    :param quiet: When set to True, warnings will not be printed.
    :return None
    """
    Logger.initialize(suppress_warnings=quiet)
    logger = Logger.get()
    digraph = _get_digraph(directory)
    undirected_graph = digraph.to_undirected()

    conn_components = nx.connected_components(undirected_graph)

    # Sort the Zettel in each component
    conn_components = [sorted(component) for component in conn_components]

    # Sort the conn_components by their size and break ties with the name of their first Zettel
    conn_components = sorted(conn_components, key=itemgetter(0))
    conn_components = sorted(conn_components, key=len, reverse=True)

    for i, component in enumerate(conn_components, start=1):
        logger.info("# Component {}".format(i))
        for zettel in component:
            logger.info(zettel)

        logger.info("")
