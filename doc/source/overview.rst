
Overview
========

`Praat <http://www.praat.org>`_  has become a de-facto standard tool for phonetic analysis, transcription of speech, and classification of speech events. To this end, it provides an intuitive point-and-click user interface for selecting intervals or points in the audio data and for labelling these with arbitrary text, which is then displayed time-aligned alongside the waveform. Praat supports annotation on multiple independent tiers, allowing for application of multidimensional annotation schemata, annotations with different degrees of granularity, or for independent transcriptions of individual participants in a dialogue recording. 

Much of Praat's usefulness comes from its programmability via a simple embedded scripting language, ‘Praat script,’ which allows full access to Praat's functions and data structures. Coupled with basic control flow mechanisms, Praat script allows automatisation of tedious and time consuming tasks. However, in spite of its many virtues and its ease of use, Praat script lacks basic features of modern programming languages, such as return statements in functions, iterators, or even basic data structures such as lists or hash tables. Additionally, not being a general-purpose language, it falls short of functionality which is not directly tied to Praat itself, such as plotting or statistical analysis.

These limitations are particularly evident when Praat script is used to manipulate Praat's native annotation objects, stored in plain text 'TextGrid' files. Such tasks often do not require any of Praat's advanced audio analysis features but would greatly benefit from access to specialised text processing tools and simple integration with external data analysis libraries. Faced with lack of such functionality, Praat users wishing to carry out more complex analyses on their annotations are forced to first export their data into some intermediate format, such as comma-separated files, before importing them into a data analysis framework of their choice.

To overcome these shortcomings, we have developed 'TextGridTools,' a Python package offering functions to parse, manipulate and query Praat annotations. TextGridTools implements all of TextGrid-related objects, such as interval and point tiers, as native Python classes and offers a clean API for accessing their attributes. Additional functions are available to perform more complex operations, such as calculation of inter-annotator agreement measures between several annotation tiers.

Coupled with Python's expressive syntax, TextGridTools allows for more compact and human-readable program code than that of Praat script. Additionally, with access to a fully-fledged programming language, users are able to carry out their analyses in one step, without Praat script serving as a mere exporting tool. Using TextGridTools annotations can be accessed directly from a Python program and processed using one of Python's many data analysis libraries (e.g., `NumPy <http://www.numpy.org>`_, `SciPy <http://www.scipy.org>`_, `Matplotlib <http://www.matplotlib.org>`_, `RPy <http://www.rpy.sourceforge.net>`_ or `pandas <http://www.pandas.pydata.org/>`_, cf. [#]_).

TextGridTools is released under the GNU General Public Licence v3.0, and hosted on `GitHub <https://github.com/hbuschme/TextGridTools>`_ allowing users to contribute their changes and extend the existing functionality.  TextGridTools is compatible with both Python 2 and Python 3.

For a longer overview as well as for citing TextGridTools,  see [#]_ (`PDF <http://pub.uni-bielefeld.de/download/2561620/2563287>`_).

Installation
------------

TextGridTools is part of the `Python Package Index <https://pypi.python.org/pypi/tgt/1.0>`_ repository . To get the latest stable version run ``pip install tgt``.

To get the latest development version, use the GitHub repository: ``git clone https://github.com/hbuschme/TextGridTools.git``.


.. [#] McKinney, W. (2012). *Python for Data Analysis: Agile Tools for Real World Data*. Sebastopol, CA: O'Reilly.

.. [#] Buschmeier, H. and Włodarczak, M. (2013). TextGridTools: A TextGrid Processing and Analysis Toolkit for Python. In P. Wagner (ed.) *Tagungsband der 24. Konferenz zur Elektronischen Sprachsignalverarbeitung (ESSV 2013)*. Dresden: TUDpress, pp. 152-157.
