# TextGridTools

Read, write, and manipulate Praat TextGrid files with Python

Copyright (C) 2011-2016 Hendrik Buschmeier, Marcin Włodarczak

## Installation

Installation with python distribute (stable version)

    pip install tgt

Installation via github (development version)

    git clone https://github.com/hbuschme/TextGridTools.git
    cd TextGridTools
    python setup.py install

## Documentation

Buschmeier, H. &amp; Włodarczak, M. (2013). TextGridTools: A TextGrid processing and analysis toolkit for Python. In <em>Proceedings der 24. Konferenz zur Elektronischen Sprachsignalverarbeitung</em>, pp. 152–157, Bielefeld, Germany. [<a href="https://pub.uni-bielefeld.de/download/2561620/2563287">pdf</a>]</p>

Current documentation can be viewed at https://textgridtools.readthedocs.io/en/stable/.

Alternatively, the API can be browsed with `pydoc` (e.g., `pydoc tgt.IntervalTier`), or documentation can be generated locally, using Sphinx, in the following way:

    cd doc
    make html # creates html documentation in doc/build/html/
