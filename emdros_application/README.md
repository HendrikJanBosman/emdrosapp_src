# emdros_application

The Python 2.7 package providing the functionality of the programs in the **emdrosapp_src** repo.

## syscfg: bootstrap configuration files
The Python files in this directory need to be edited to match the path names on your system and the Emdros backend you will be using
(default is SQLite 3). **config.py** contains general settings; the other named Python files contain settings for the corresponding
kernels.

The file **options.cfg** contains settings for command line arguments for all programs.
It is best left alone, unless you know what you are doing.

## mql_engine
This subpackage contains the following modules:
* **MQLEngine.py**: provides the **MQLEngine** object, which provides simple methods for frequently used database operations.
* **PySheaf.py**: provides the **PySheaf** , **PyStraw** and **PyObject** objects, which are Pythonesque versions of the corresponding
EmdrosPy objects.
* **PyTable.py**: Provides the **PyTable** object.
* **PySetOfMonads.py**: Provides the **SetOfMonads** object.
* **Query.py**: Provides the **Query** object, which can manipulate MQL queries (notably: add search domains, GET phrases).
