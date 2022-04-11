
# pdffile = "/Users/bradneuman/Downloads/prosper-2021-1099-b.pdf"
pdffile = "prosper-2021-1099-b.pdf"

# from tabula import read_pdf
# from tabulate import tabulate

# #reads table from pdf file
# df = read_pdf("/Users/bradneuman/Downloads/prosper-2021-1099-b.pdf",pages="all") #address of pdf file
# print(tabulate(df))

from pprint import pprint
import camelot
import re

try:
    print(tables)
except NameError as ne:
    # extract all the tables in the PDF file
    tables = camelot.read_pdf(pdffile, pages='all', flavor='stream')

    print(tables)

# print the first table as Pandas DataFrame
# print(tables[0].df)

# if len(tables) < 1:
#     print("unable to parse any table")
#     return None
# if len(tables) > 1:
#     print("not sure how to handle multiple tables, bailing")
#     return None

cashRegex = '\$([0-9]*\.[0-9][0-9])'
boxRegex = 'with *Box *([A-F]) *checked'

def getColumns(table):
    ''' Check the text for the needed headers "Proceeds" and "Other" '''

    
    df = table.df
    sz = df.shape
    if len(sz) != 2:
        print("invalid datashape: {}".format(sz))
        return None

    columns = {}

    # find "proceeds" and "other" columns
    for row in range(sz[0]):
        for col in range(sz[1]):
            cell = df[col][row]
            if '1d.' in cell and 'Proceeds' in cell:
                columns['proceeds'] = col
                # print("found at {}, {}: {}".format(col, row, cell))
            if 'Other' in cell:
                columns['other'] = col
                # print("found at {}, {}: {}".format(col, row, cell))
            if '1a.' in cell and 'Description' in cell:
                columns['description'] = col
                # print("found at {}, {}: {}".format(col, row, cell))

    return columns


def readTable(table, columnKey):
    ''' Tabulate the table '''

    res = {'1d': [],
           '1e': [],
           '1a': [],
           'box': 'unknown'}

    df = table.df
    sz = df.shape

    # First sum up all the proceeds in 1.d
    for row in range(sz[0]):
        ## proceeds are just listed in the row, and should be the only matches?

        ## it looks like all actual proceeeds should match row with a description, so cehck for that
        ## Just check that it has a few letters
        letters = sum(c.isalpha() for c in df[columnKey['description']][row])
        hasDescription = letters > 3 # TODO: magic numbers
        if hasDescription and row > 3:
            res['1a'].append(df[columnKey['description']][row])
        
        r = re.search(cashRegex, df[columnKey['proceeds']][row])
        hasProceeds = False
        if r:
            hasProceeds = True

            if not hasDescription:
                # print(f'assuming this is the summary row: {r.groups()[0]}')
                res['summary_1d'] = float(r.groups()[0])
            else:
                res['1d'].append(float(r.groups()[0]))

        for col in range(sz[1]):
            # Check for the categorization filing box
            r = re.search(boxRegex, df[col][row])
            if r:
                res['box'] = r.groups()[0]

        # now, find the 1.e entries in 'other'
        cell = df[columnKey['other']][row]
        if re.search('[B,b]ox *1 *e', cell):
            r = re.search(cashRegex, cell)
            if r:
                res['1e'].append(float(r.groups()[0]))


    # if res['box'] != 'unknown':
    #     print ('Read table for "box {} checked"'.format(res['box']))
    # else:
    #     print ('could not figure out which "filing box" was checked in this table')
    # print (f'found {num1d} proceeds totalling {sum1d}')
    # print (f'and {num1e} cost bases totally {sum1e}')
    # print (f'(and also {num1a} description rows)')
    return res

def readPages(tables):
    ''' iterate through each table in the input and return the parsed version '''
    pages = []
    for table in tables:
        columnKey = getColumns(table)
        if columnKey:
            page = readTable(table, columnKey)
            # pprint(page)
            pages.append(page)
    return pages

def tabulate(pages):
    ''' given parsed pages, combine them all into a report '''
    totals = {}
    errors = False

    for page in pages:
        if 'box' not in page:
            print('WARNING: page is missing a box! This means the parse probably failed!')
            errors = True
        else:
            box = page['box']
            if box not in totals:
                # Initialize
                totals[box] = {'1d': [], '1e': [], '1a': []}

            if 'summary_1d' in page:
                ## There should be exactly one summary per box type
                if 'summary_1d' in totals[box]:
                    print('WARNING: got a second summary for the same box type! had {}, got {}'.format(
                        totals[box]['summary_1d'],
                        page['summary_1d']))
                    errors = True
                else:
                    totals[box]['summary_1d'] = page['summary_1d']

            # Now append to the correct box
            for key in ['1a', '1d', '1e']:
                totals[box][key].extend(page[key])

    # now check everything at the end
    for box in totals:

        ## Do the computed and parsed summaried match?
        if 'summary_1d' not in totals[box]:
            print(f'WARNING: box {box} did not have a summary of 1d')
            errors = True
        else:
            computed_sum = sum(totals[box]['1d'])
            if abs(computed_sum - totals[box]['summary_1d']) > 0.01:
                print('WARNING: box {} had a summary 1d of {} but a computed sum of {}'.format(
                      box,
                      totals[box]['summary_1d'],
                      computed_sum))
                errors = True

        ## Do we have the same numbers of everything?
        if len(totals[box]['1a']) != len(totals[box]['1d']) or len(totals[box]['1d']) != len(totals[box]['1e']):
            print('WARNING: different numbers of parsed entries! I dont think the pages are usually split,'
                  'so this is bad')
            errors = True
            print('in Box {}: Found {} entries for box 1a, {} entries for 1d, and {} for 1e'.format(
                box,
                len(totals[box]['1a']),
                len(totals[box]['1d']),
                len(totals[box]['1e'])))
                
    if errors:
        totals['errors'] = True

    return totals

def report(tabulated):
    ''' given tabulated results, print a report'''

    if 'errors' in tabulated:
        print('*** WARNING: errors during parsing, do not trust results ***')


    print('BOX | {:9} | {:9}'.format('1d', '1e'))
    for box in tabulated:
        if box == 'errors':
            continue
        print('{:3} | {:9,.2f} | {:9,.2f}'.format(box,
                                                  sum(tabulated[box]['1d']),
                                                  sum(tabulated[box]['1e'])))

    print('sum | {:9,.2f} | {:9,.2f}'.format(sum([sum(tabulated[b]['1d']) for b in tabulated]),
                                             sum([sum(tabulated[b]['1e']) for b in tabulated])))

