# emdrosapp_src
Python 2.7 sources for my Emdros-based programs.
Conversion to Python 3 is in the planning, but will probably have
to go together with a complete overhaul of the packages.

## depency on other repos
In order to work, the programs in this repo assume the presence of
the data and config files in at least one of the directories in 
the **emdrosapp_data** repo.

Detailed documentation on the programs, and on the modules in the **emdros_application** package 
are stored in the **emdrosapp_doc** repo.

## files

* **emdros_application**: the Python 2.7 package providing all functionality for the programs listed below.
* **template.py**: copy and edit this to write new Emdros-based applications.
* **mqlc.py**: an interactive MQL query/command interpreter. 
* **labelman.py**: a program to add descriptive labels to an Emdros database, based on 
    user-supplied text patterns. These files are stored in the **lbl** directory of
    each main directory in the **emdrosapp_data** repo. 
* **unitman.py**: a program to combine low level textual objects into ever larger textual
    units.

## database kernels
All programs can work with various database families (having, e.g., different languages or database setups),
which I call kernels. The kernel is specified with the -k option (default is bhebrew).

## linguistic modes
All programs can work in a number of linguistic modes (specified with the -m option).
Depending on the mode, the programs will work with different object types,
use different labels and text patterns and produce different output layouts.
At present, the modes are:

* **graphical**: concerns the graphemes of which the text is built: capitalization, accents, interpunction, etc.
* **lexical**: concerns word features derived from a lexicon, not from morphology or syntax.
* **morphological**: concerns word features derived from morphology.
* **syntactic**: concerns syntax and text syntax.
* **participants**: concerns participant references and their relations.
* **prosodic**: concerns phenomena connected to versification (cola, verselines, strophes, metre, alliteration, acrostic etc).

## installation and configuration
* Emdros with Python support must be installed on your system (www.emdros.org).
* At least one of the main directories in the **emdrosapp_data** repo must be present on your 
system.
* The file **config.py** in **emdros_application/syscfg** must be edited to match your system.
* For each of these directories, a corresponding config file in 
   **emdros_application/syscfg** must be created and/or edited to match your system.
