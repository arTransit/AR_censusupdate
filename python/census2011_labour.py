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
        ["TLABOURF","Total - Labour force status"],
        ["INLABOURF","In the labour force"],
        ["EMPLOYED","Employed"],
        ["UNEMPLOYED","Unemployed"],
        ["NOTINLFRCE","Not in the labour force"],
        ["PARTICRATE","Participation rate"],
        ["EMPRATE","Employment rate"],
        ["UNEMPRATE","Unemployment rate"],
        ["TEMPBYMODE","Total - Mode of transportation"],
        ["DRIVER","Car, truck or van as a driver"],
        ["PASSENGER","Car, truck or van as a passenger"],
        ["TRANSIT","Public transit"],
        ["WALK","Walked"],
        ["BICYCLE","Bicycle"],
        ["MOTORCYCLE","Motorcycle, scooter or moped"],
        ["OTHER","Other methods"]
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



