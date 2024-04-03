# parse-prosper-1099
Simple command line tool to parse 1099-B from Prosper Funding (not affiliated)

# I AM NOT A TAX PROFESSIONAL. USE THIS TOOL AT YOUR OWN RISK

## 2023 tax year update!
Apparently this code is broken with newer version of python, like 3.12. I don't know why and don't have time
to look into it, so I set up a venv using 3.9 (I also didn't check if any version in between would work):

```
$ python3.9 -m venv ./venv
$ source venv/bin/activate
$ pip install camelot-py
$ pip install opencv-python
```

Then you can try running as below. Make sure to use `python parse.py` so you get the python from the venv

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
* If I need to procrastinate again next tax season, maybe I'll make it export a direct csv in a format turbotax can import to avoid the need to attach the paperwork
* Add some proper version to figure out whatever broke in tax year 2023 (april 2024) with my local setup
* Don't import everything so early so `--help` is fast

