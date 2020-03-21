import re
from pathlib import Path
import networkx as nx


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


def get_graph(zettel_directory_path):
    """
    Parses the Zettel in `zettel_directory` and returns a graph.

    :param zettel_directory_path PosixPath to directory where the Zettel are stored.

    return: Dictionary representing the Zettel graph.
    """

    DG = nx.DiGraph()

    for zettel_path in zettel_directory_path.glob('*.md'):
        zettel_id = get_zettel_id(zettel_path)

        DG.add_node(zettel_id)

        with open(zettel_path, 'r') as zettel_file:
            zettel_text = zettel_file.read()

            for reference_id in load_references(zettel_text):
                DG.add_edge(zettel_id, reference_id)

    return DG

