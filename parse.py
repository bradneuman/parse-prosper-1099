#!/usr/bin/env python3

import camelot
import re

# Some regexe's for text I found in my form
cashRegex = '\$([0-9]*\.[0-9][0-9])'
boxRegex = 'with *Box *([A-F]) *checked'
box1ERegex = '[B,b]ox *1 *e'

def getColumns(table):
    '''Check the text for the needed headers Proceeds, Other, and Description.
    Return a map from the column type to the numerical column
    '''
    
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
            if 'Other' in cell:
                columns['other'] = col
            if '1a.' in cell and 'Description' in cell:
                columns['description'] = col

    return columns

def readTable(table, columnKey):
    '''Read the entries out of the given table.

    Requires a table and a columnKey, and returns a dict with an appended list of everything we want to find

    '''

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
        if re.search(box1ERegex, cell):
            r = re.search(cashRegex, cell)
            if r:
                res['1e'].append(float(r.groups()[0]))
    return res

def readTables(tables):
    '''
    Iterate through each table in the list of `tables`, read them, and return the aggregated output.
    '''
    pages = []
    for table in tables:
        columnKey = getColumns(table)
        if columnKey:
            page = readTable(table, columnKey)
            # pprint(page)
            pages.append(page)
    return pages

def tabulate(pages):
    ''' Gived the aggregated parsed data from the tables, combine it all appriorately and return the result.
    '''
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


    ret = {'data': totals}
    if errors:
        ret['errors'] = True

    return ret


def report(tabulated):
    ''' given tabulated results, print a report'''

    if 'errors' in tabulated:
        print('*** WARNING: errors during parsing, do not trust results ***')


    print('BOX | {:9} | {:9}'.format('1d', '1e'))
    for box in tabulated['data']:
        if box == 'errors':
            continue
        print('{:3} | {:9,.2f} | {:9,.2f}'.format(box,
                                                  sum(tabulated['data'][box]['1d']),
                                                  sum(tabulated['data'][box]['1e'])))

    print('sum | {:9,.2f} | {:9,.2f}'.format(
        sum([sum(tabulated['data'][b]['1d']) for b in tabulated['data']]),
        sum([sum(tabulated['data'][b]['1e']) for b in tabulated['data']])))

if __name__ == '__main__':
    import sys
    def usage():
        print('''
        usage: {} filename
        
        where filename is exactly the 1099-b form I received one time in 2021 from Prosper.
        Seriously, this code probably won't work, but maybe it'll be an interesting starting point.
        '''.format(sys.argv[0]))

    if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        usage()
        exit(-1)

    tables = camelot.read_pdf(sys.argv[1], pages='all', flavor='stream')
    if not tables:
        print('ERROR: could not read file!\n')              
        usage()
        exit(-1)

    
    parsed = readTables(tables)
    tabulated = tabulate(parsed)
    report(tabulated)
