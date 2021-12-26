![Vizel](assets/vizel_banner@2x.jpg)

[![Build Status](https://travis-ci.com/BasilPH/vizel.svg?branch=master)](https://travis-ci.com/BasilPH/vizel)

See the stats and connections of your Zettelkasten.

![Demo](assets/vizel_demo.gif)

## Getting Started

### Required Zettelkasten structure

Vizel tries to be format agnostic without requiring configuration.

Vizel makes the following assumptions:

* The Zettel files have an `.md` or `.txt` extension.
* All Zettel are in one single directory.
* References use the `[[REFERENCE]]` or `[LABEL](REFERENCE)` format.
* References of a Zettel pointing to itself are ignored.

Vizel was first developed for the format used by the
[The Archive](https://zettelkasten.de/the-archive/). Other formats are
now supported as well, thanks to the help from the community.

### Installing

Run `pip install vizel`. Vizel supports Python 2.7 and 3.6 - 3.10.

If you get an error about missing graphviz when running the `graph-pdf`
command, you might need to install it with

` brew install graphviz` on OS X or

`sudo apt-get install graphviz` on Ubuntu.

## Usage

`vizel` has the following commands:

#### graph-pdf

```
vizel graph-pdf [OPTIONS] DIRECTORY

Generates a PDF displaying the graph created spanned by Zettel and their connections in the folder DIRECTORY.

Options:
  --pdf-name TEXT  Name of the PDF file the graph is written into. Default:
                   vizel_graph
  --help  Show this message and exit.
```

#### stats

```

Usage: vizel stats [OPTIONS] DIRECTORY

  Prints the stats of the graph spanned by Zettel in DIRECTORY.

  Stats calculated:
  - Number of Zettel
  - Number of references between Zettel (including bi-directional and duplicate)
  - Number of Zettel without any reference from or to a Zettel
  - Number of connected components
  
Options:
  -q, --quiet  Quiet mode
  --help       Show this message and exit.
```

##### A note on connected components

The fewer connected components your Zettelkasten has, the better. The
ideal number is 1. It means that you can reach any Zettel by following
links. This, in turn, should increase the likelihood of making new
semantic connections.

Connected components are a concept from graph theory. In the context of
a Zettelkasten and vizel, a connected component is a set of Zettel,
which can be reached from any other Zettel in the same component by
following links. Those links do not need to be direct but can pass
through other Zettel. The direction of the links also doesn't matter.

Two Zettel are not in the same component if there is no way to reach one
from the other through links.

Connected components will show up as separate clusters of Zettel when
using `graph-pdf`. Use the `components` command to get a list of your
components, and the Zettel contained in each.

#### unconnected

```
Usage: vizel unconnected [OPTIONS] DIRECTORY

  Prints all of the Zettel in DIRECTORY that have no in- or outgoing
  references.

Options:
  -q, --quiet  Quiet mode
  --help       Show this message and exit.
```

#### components

```
Usage: vizel components [OPTIONS] DIRECTORY

  Lists the connected components and their Zettel in DIRECTORY.

Options:
  -q, --quiet  Quiet mode
  --help       Show this message and exit.
```

## Built With

* [NetworkX](https://networkx.github.io/): Network analysis in Python
* [click](https://click.palletsprojects.com): Python composable
  command-line interface toolkit
* [Graphviz](https://github.com/xflr6/graphviz): Simple Python interface
  for Graphviz

## Updates & Contributing

Feel free to open issues and pull-requests. Subscribe to the
[vizel newsletter](https://tinyletter.com/vizel) to be informed about
new releases and features in development.

You can reach out to me for feedback or questions on
[Twitter](https://twitter.com/BasilPH) or through
[my website](https://interdimensional-television.com/).

If you've found vizel useful, please consider
[sponsoring](https://github.com/sponsors/BasilPH) maintenance and
further development. Or
[buying me a coffee](https://www.buymeacoffee.com/interdimension).


### Development install

The project uses [Poetry](https://python-poetry.org/).

1. Install Poetry.
2. Clone this repository.
3. Run `poetry install` in the root of this project.

### Running tests

Run `py.test` in the `tests` directory.


## Versioning

Vizel uses [SemVer](http://semver.org/) for versioning. For the versions
available, see the
[tags on the repository](https://github.com/BasilPH/vizel/tags).

## Authors

* **Basil Philipp** - *Owner*

## License

This project is licensed under GNU GPLv3.

## Acknowledgments

* Thank you Christian Tietze and Sascha Fast for creating
  [The Archive](https://zettelkasten.de/the-archive/) app and writing a
  [book](https://zettelkasten.de/book/de/) (German only) on the
  Zettelkasten method.

