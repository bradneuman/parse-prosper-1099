# parse-prosper-1099
Simple command line tool to parse 1099-B from Prosper Funding (not affiliated)

# I AM NOT A TAX PROFESSIONAL. USE THIS TOOL AT YOUR OWN RISK

## Usage

Don't use this, seriously I wrote it to parse one single PDF one single time. If you want to try it though:

* Install the deps below
* ./parse.py <pdffilename>

Now if you see any errors or warnings, don't trust the results, it probably broke.

If not, compare the sum row with the total numbers at the top, and if they match, then hey it _might_ have
just worked, and now you have the totals you need for a tax program like TurboTax


## Dependencies
* pip install camelot-py
** requries numpy and brew install ghostscript tcl-tk from https://camelot-py.readthedocs.io/en/master/user/install-deps.html

## Future work
If I need to procrastinate again next tax season, maybe I'll make it export a direct csv in a format turbotax
can import to avoid the need to attach the paperwork
