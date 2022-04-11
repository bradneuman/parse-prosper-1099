# parse-prosper-1099
Simple command line tool to parse 1099-B from Prosper Funding (not affiliated)

## This is a work in progress, has not been tested, and should probably not be used


### Libraries
* ~PyPDF2: https://github.com/py-pdf/PyPDF2~ -- couldn't handle the table
* tabula-py and tabulate from instructions at https://www.geeksforgeeks.org/how-to-extract-pdf-tables-in-python/
** Might work but requires java runtime, yuck
* pip install camelot-py
** requries numpy and brew install ghostscript tcl-tk from https://camelot-py.readthedocs.io/en/master/user/install-deps.html

