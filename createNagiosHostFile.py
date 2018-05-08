#!/usr/bin/python
# License: Free as in beer
# Author: j0nix 2016

import csv
import sys
from optparse import OptionParser
import os.path

HOSTSDPATH = '/etc/nagios/hosts.d'

def warn_print(string):
    ''' prints in red'''
    print '\033[1;31m' + string + '\033[1;m'


def getOptions():
    # options/flags definitions and parsing
    desc = "\033[94m\033[1mDescription: Reads csv file and spits out a nagios host config file. Script expects a csv file with first row defining headers that is used as value definitions in nagios config file. If you need an example of csv file just execute script with flag '--create-csv'. Note that the first column in your csv will be used to as the filename for the nagios host config file.\033[0m"

    theend = "\033[94mj0nix 2016\033[0m"

    parser = OptionParser(description=desc,epilog=theend)

    parser.add_option("-f", dest="filename", help="That csv-file [REQUIRED]", metavar="FILE",default='')
    parser.add_option("-d", dest="delimiter", help="Field delimiter [default = semi-colon]",default=';')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="make lots of noise")
    parser.add_option("--create-csv", action="store_true", dest="createcsv", default=False, help="generate a csv with default headers")
    (options, args) = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
    return options


def parseRow(row,header,rownum):
    # Declare that this is the first column
    colnum = 0
    data = "define host {\n"
    for col in row:
    # If this is the first column in row we create a file named as the first column value
        if colnum == 0:
            # Is this column empty? if so we skip that row...
            if not col:
                if options.verbose:
                    warn_print( "\n  >>> MISSING column '%2s' on row %-2s %2s" % (header[colnum],str(rownum),"[ SKIPPING ROW ]"))
                    return False

            wf = os.path.join(HOSTSDPATH, col+".cfg")
            if os.path.isfile(wf):
                warn_print( 'Config file:"%s" already exist\nskipping host / fix this problem and try again' % wf)
                return False
            output = open(wf,'w')

            if options.verbose:
                nagconfstr = ''.join([ "%s:\t\t%s\n" % h for h in zip(header,row) ])
                print '\n %s. [ Saving row nr:%s\n"%s"\nto file: "%s" ]' % (rownum+1,rownum,nagconfstr,wf)

        # Is this column empty? if so we skip it
        if not col:
                # increment column reference
            if options.verbose:
                warn_print( " >>> MISSING column '%2s' on row %-2s %2s" % (header[colnum],str(rownum),"[ SKIPPING COLUMN ]"))
            colnum += 1
            continue

        #Add data that we should save to file
        l = 21 - len(header[colnum])
        convert = '    %-3s %' + str(l) + 's %s\n'
        data += convert % (header[colnum]," ",col)
        colnum += 1

    data += "}\n"
    if options.verbose: print data
    # Write formated rowdata to file
    # If first column was empty we have not opened any file, hence this test
    if not output.closed:
        output.write(data)
        output.close()
    return True


def createConfig(options):

    # Have we requested to generate a csvfile ?
    if options.createcsv:
        csvFile = "csvFile.csv"
        output = open(csvFile,'w')
        data ="host_name;alias;address;hostgroups;use\nexample.int.comhem.com;example;example.int.comhem.com;Server,linux;linux-testing\n"
        print "\n [ Created file %s with default headers and example host ]" % csvFile
        output.write(data)
        output.close()
        exit(0)

    # Have we defined csv file to read ?
    if options.filename:
        # Open & read file
        if os.path.isfile(options.filename):
            if options.verbose:
                print "\n 1. [ Open and read file: %s ]" % (options.filename)
            f=open(options.filename, 'r')
            csv_reader = csv.reader(f,delimiter=options.delimiter)
        else:
            error = options.filename, " does not exist or is not a file"
            sys.exit(error)

        # Declare that we start at first line
        rownum = 0
        # Loop over lines
        for row in csv_reader:
            # If this is the first line, save row for reference values (column names) later
            if rownum == 0:
                header = row
            else:
                parseRow(row,header,rownum)
            rownum += 1
        f.close()
        print "\n %s. [ ALL DONE ]\n" % (rownum+1)

if __name__=="__main__":
    options = getOptions()
    createConfig(options)
