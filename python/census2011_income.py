###########################################################
# formatCensus2011.py
#
# Read table of census data (converted from ivt file) and 
# create separate tables for each level of geometry.
# Tables are further cleaned and headers renamed.
# 
# Author: Andrew Ross
# Date:   2013 September 30
#

import sys
import os
import re
import csv


provinceCodes = {'BC':59}
geoLevels = [
        {'name':'Province', 'code':'PR', 'codeLength':2},
        {'name':'Census Division', 'code':'CD', 'codeLength':4},
        {'name':'Census Subdivision', 'code':'CSD', 'codeLength':7},
        {'name':'Dissemination area', 'code':'DA', 'codeLength':8} ]
columnHeaders= "PRUID,TTOTINC,TWTHOUTINC,TWTHINC,TUNDR5000,T5TO10000,T10TO15000,T15TO20000,T20TO25000,T30TO35000,T40TO50000,T50TO60000,T60TO80000,T80TO100,TOVER100,TMEDIAN,TAVERAGE"
nullRecord= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
dataColumns = [
        'Geography',
        'Total - Total income in 2010',
        'Without income',
        'With income',
        'Under $5,000',
        '$5,000 to $9,999',
        '$10,000 to $14,999',
        '$15,000 to $19,999',
        '$20,000 to $29,999',
        '$30,000 to $39,999',
        '$40,000 to $49,999',
        '$50,000 to $59,999',
        '$60,000 to $79,999',
        '$80,000 to $99,999',
        '$100,000 and over',
        'Median income $',]

def createOutputFiles( stub ):
    openFiles = []
    for i in geoLevels:
        newFile = stub + '_' + i['code'] + '.csv'
        print ">>createOutputFiles - creating: " + newFile
        f = open( newFile, 'w' )
        openFiles.append( f )
    return openFiles


def writeHeader( fileList ):
    for f in fileList:
        f.write( columnHeaders +'\n' )


def formatData( d ):
    rowId = False
    row = [d[i] for i in dataColumns]
    searchId = re.search(r"\((\d+)\)", d['Geography'])
    if searchId:
        if int(searchId.groups()[0][0:2]) == provinceCodes['BC']:
            if checkData( row ):
                rowId = int( searchId.groups()[0] ) 
    return rowId,row


def checkData( d ):
    return True
    try:
        total = int( float(d[1]))
        s = sum( [int(float(i)) for i in d[2:]] )
    except:
        print ">>intfloatERROR: "
        print d
        return False
    else:
        if abs(total - s) < 50:
            return True
        else:
            print ">>difference: " + str( abs(total-s))
            return False


def getDictionaryFromCSV( inputFile ):
    print ">>getDictionaryFromCSV:" + inputFile.name
    csvDictionary = {}
    csvReader = csv.DictReader( inputFile )
    csvReader.fieldnames = [field.strip() for field in csvReader.fieldnames]
    for line in csvReader:
        rowId, data = formatData( line )
        if rowId:
            csvDictionary[ rowId ] = data
        else:
            #print "rejected: " + ','.join(data)
            pass
            
    return csvDictionary


def outputRecord( id, name, rA, outputFiles):
    combinedRecord = [id, name, int( float(rA[0]) )] + rA
    for i in range(0, len(geoLevels)):
        if id < 10 ** geoLevels[i]['codeLength']:
            outputFiles[i].write( ','.join( [str(f) for f in combinedRecord] ) + '\n')
            break


def processCensus( inputFiles, outputFiles ):
    #process input files as CSVs
    [csvA] = [getDictionaryFromCSV( file ) for file in inputFiles]

    for id in sorted( csvA.keys() ):
        outputRecord( id, csvA[id][0], csvA[id][1:], outputFiles ) 


def closeFiles( fileList ):
    for f in fileList:
        print ">>closeFiles - closing:" + f.name 
        f.close()


def getCommandLine():
    if (len(sys.argv) ==3):
        if os.path.isfile( sys.argv[1] ):
            return sys.argv[1],sys.argv[2]
    return "",""


def printUsage():
    print "Usage:"
    print "python " + sys.argv[0] + " <INPUT.csv> <OUTPUTSTUB>\n"


if __name__ == "__main__":
    print "Format Census 2011"

    inputFileNameA,outputStub = getCommandLine()
    if (not inputFileNameA):
        printUsage()
        sys.exit(1)

    else:
        print "Reading: %s" % (inputFileNameA)
        print "Exporting: %s" % outputStub

        inputFiles = []
        inputFiles.append( open( inputFileNameA ))
        outputFiles = createOutputFiles( outputStub )

        writeHeader( outputFiles )
        processCensus( inputFiles, outputFiles )
        closeFiles( inputFiles + outputFiles )



