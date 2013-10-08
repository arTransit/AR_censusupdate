###########################################################
# formatCensus2011.py
#
# Read table of census data (converted from ivt file) and 
# create separate tables for each level of geometry.
# Tables are further cleaned and headers renamed.
# 
# Author: Andrew Ross
# Date:   2013 October 4
#


import sys
import os
import re
import csv


provinceCodes = {'BC':59}
geoLevels = [
        {'name':'Province', 'code':'PR', 'codeLength':2},
        {'name':'City', 'code':'CITY', 'codeLength':3},
        {'name':'Census Division', 'code':'CD', 'codeLength':4},
        {'name':'Census Subdivision', 'code':'CSD', 'codeLength':7},
        {'name':'Dissemination area', 'code':'DA', 'codeLength':8}
    ]
dataDictionary = [
        ["UID",""],
        ["GEOGRAPHY","Geography"],
        ["TTOTINCPOP","Total - Total income in 2010"],
        ["TWTHOUTINC","Without income"],
        ["TWTHINC","With income"],
        ["TUNDR5000","Under $5,000"],
        ["T5TO10000","$5,000 to $9,999"],
        ["T10TO15000","$10,000 to $14,999"],
        ["T15TO20000","$15,000 to $19,999"],
        ["T20TO30000","$20,000 to $29,999"],
        ["T30TO40000","$30,000 to $39,999"],
        ["T40TO50000","$40,000 to $49,999"],
        ["T50TO60000","$50,000 to $59,999"],
        ["T60TO80000","$60,000 to $79,999"],
        ["T80TO100000","$80,000 to $99,999"],
        ["TOVER100","$100,000 and over"],
        ["TMEDIAN","Median income $"],
        ["TAVERAGE","Average income $"],
        ["FTOTINCFAM","Total - Economic family total income in 2010"],
        ["FUNDER5","Under $5,000"],
        ["F5TO10000","$5,000 to $9,999"],
        ["F10TO15000","$10,000 to $14,999"],
        ["F15TO20000","$15,000 to $19,999"],
        ["F20TO30000","$20,000 to $29,999"],
        ["F30TO40000","$30,000 to $39,999"],
        ["F40TO50000","$40,000 to $49,999"],
        ["F50TO60000","$50,000 to $59,999"],
        ["F60TO80000","$60,000 to $79,999"],
        ["F80TO100000","$80,000 to $99,999"],
        ["FOVER100","$100,000 and over"],
        ["FMEDIAN","Median family income $"],
        ["FAVERAGE","Average family income $"]
    ]
columnHeaders= [d[0] for d in dataDictionary] #field names in destination file
dataColumns = [d[1] for d in dataDictionary[1:] ] #field names in origin file


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
        f.write( ','.join( columnHeaders ) +'\n' )


def formatData( d ):
    rowId = False
    row = [d[i] for i in dataColumns]
    searchId = re.search(r"\((\d+)\)", d['Geography'])
    if searchId:
        _rowId = int(searchId.groups()[0])
        if checkData( _rowId, row ): rowId = _rowId
    return rowId,row


def checkData( id, d ):
    if (900 < id < 980) or (id == provinceCodes['BC']):
        try:
            float( d[1] )  # are numbers valid?
            return True
        except ValueError:
            return False
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
    combinedRecord = [id, name ] + rA 
    for i in range(0, len(geoLevels)):
        if id < 10 ** geoLevels[i]['codeLength']:
            outputFiles[i].write( ','.join( [str(f) for f in combinedRecord] ) + '\n')
            break


def processCensus( inputFiles, outputFiles ):
    #process input files as CSVs
    csvA = getDictionaryFromCSV( inputFiles[0] )

    for id in csvA.keys():
        outputRecord( id, csvA[id][0], csvA[id][1:], outputFiles ) 


def closeFiles( fileList ):
    for f in fileList:
        print ">>closeFiles - closing:" + f.name 
        f.close()


def getCommandLine():
    if (len(sys.argv) ==3):
        if os.path.isfile( sys.argv[1] ) :
            return sys.argv[1],sys.argv[2]
    return "",""


def printUsage():
    print "Usage:"
    print "python " + sys.argv[0] + " <INCOME.csv> <OUTPUTSTUB>\n"


if __name__ == "__main__":
    print "Format Census 2011: Language module"

    inputFileNameA,outputStub = getCommandLine()
    if (not inputFileNameA) :
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



