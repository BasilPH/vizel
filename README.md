# VIZEL

A tool to visualise the connections between Zettel in a Zettelkasten.

## Getting Started


### Zettelkasten structure

Currently only the format used by
[The Archive](https://zettelkasten.de/the-archive/) is supported:

* The IDs of Zettel are 12 digit numbers (e.g. `202003302203`)
* The Zettel files have a `.md` extension and the filename of each
  Zettel starts with an ID (e.g.
  `202003302203_This_is_an_example_Zettel.md`).
* All of your Zettel are in one directory and not spread amongst
  multiple folders.

### Installing

The project uses [Poetry](https://python-poetry.org/).

1. Install Poetry.
2. Clone or download this repository.
3. Run `poetry install` in the root of this project.

### Usage

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
  --help  Show this message and exit.
```

#### unconnected
```
Usage: vizel unconnected [OPTIONS] DIRECTORY

  Prints all of the Zettel in DIRECTORY that have no in- or outgoing
  references.

Options:
  --help  Show this message and exit.
```

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework
  used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read
[CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426)
for details on our code of conduct, and the process for submitting pull
requests to us.

## Versioning

This project uses [SemVer](http://semver.org/) for versioning. For the
versions available, see the
[tags on the repository](https://github.com/BasilPH/vizel/tags).

## Authors

* **Basil Philipp** - *Owner*

## License

This project is licensed under the MIT License - see the
[LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thank you Christian Tietze and Sascha Fast for creating
  [The Archive](https://zettelkasten.de/the-archive/) app and writing
  the [book](https://zettelkasten.de/book/de/) (German only).
