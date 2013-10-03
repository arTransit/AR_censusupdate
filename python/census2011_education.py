###########################################################
# formatCensus2011.py
#
# Read table of census data (converted from ivt file) and 
# create separate tables for each level of geometry.
# Tables are further cleaned and headers renamed.
# 
# Author: Andrew Ross
# Date:   2013 September 17
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
        ["GEOGRAPHY",".Geography"],
        ["15_24TOTAL","15 to 24 years.Total - Highest certificate, diploma or degree"],
        ["15_24NO","15 to 24 years.No certificate, diploma or degree"],
        ["15_24HIGHS","15 to 24 years.High school diploma or equivalent"],
        ["15_24TRADE","15 to 24 years.Apprenticeship or trades certificate or diploma"],
        ["15_24CLLGE","15 to 24 years.College, CEGEP or other non-university certificate or diploma"],
        ["15_24SUB","15 to 24 years.University certificate or diploma below bachelor level"],
        ["15_24FULL","15 to 24 years.University certificate, diploma or degree at bachelor level or above"],
        ["15_24BACH","15 to 24 years.Bachelor's degree"],
        ["15_24ABOVE","15 to 24 years.University certificate, diploma or degree above bachelor level"],
        ["25_54TOTAL","25 to 54 years.Total - Highest certificate, diploma or degree"],
        ["25_54NO","25 to 54 years.No certificate, diploma or degree"],
        ["25_54HIGHS","25 to 54 years.High school diploma or equivalent"],
        ["25_54TRADE","25 to 54 years.Apprenticeship or trades certificate or diploma"],
        ["25_54CLLGE","25 to 54 years.College, CEGEP or other non-university certificate or diploma"],
        ["25_54SUB","25 to 54 years.University certificate or diploma below bachelor level"],
        ["25_54FULL","25 to 54 years.University certificate, diploma or degree at bachelor level or above"],
        ["25_54BACH","25 to 54 years.Bachelor's degree"],
        ["25_54ABOVE","25 to 54 years.University certificate, diploma or degree above bachelor level"],
        ["55_64TOTAL","55 to 64 years.Total - Highest certificate, diploma or degree"],
        ["55_64NO","55 to 64 years.No certificate, diploma or degree"],
        ["55_64HIGHS","55 to 64 years.High school diploma or equivalent"],
        ["55_64TRADE","55 to 64 years.Apprenticeship or trades certificate or diploma"],
        ["55_64CLLGE","55 to 64 years.College, CEGEP or other non-university certificate or diploma"],
        ["55_64SUB","55 to 64 years.University certificate or diploma below bachelor level"],
        ["55_64FULL","55 to 64 years.University certificate, diploma or degree at bachelor level or above"],
        ["55_64BACH","55 to 64 years.Bachelor's degree"],
        ["55_64ABOVE","55 to 64 years.University certificate, diploma or degree above bachelor level"],
        ["OVR65TOTAL","65 years and over.Total - Highest certificate, diploma or degree"],
        ["OVR65NO","65 years and over.No certificate, diploma or degree"],
        ["OVR65HIGHS","65 years and over.High school diploma or equivalent"],
        ["OVR65TRADE","65 years and over.Apprenticeship or trades certificate or diploma"],
        ["OVR65CLLGE","65 years and over.College, CEGEP or other non-university certificate or diploma"],
        ["OVR65SUB","65 years and over.University certificate or diploma below bachelor level"],
        ["OVR65FULL","65 years and over.University certificate, diploma or degree at bachelor level or above"],
        ["OVR65BACH","65 years and over.Bachelor's degree"],
        ["OVR65ABOVE","65 years and over.University certificate, diploma or degree above bachelor level"]
    ]
columnHeaders= [d[0] for d in dataDictionary]     #field names in destination file
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
    searchId = re.search(r"\((\d+)\)", d['.Geography'])
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

    # get first two rows and concatenate to form field names
    csvReader = csv.reader( inputFile )
    header1 = csvReader.next()
    header2 = csvReader.next()
    fieldNames = [ header1[x].strip() + '.' + header2[x].strip() for x in range(len(header1))]

    csvReader = csv.DictReader( inputFile, fieldNames )
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
    print "python " + sys.argv[0] + " <EDUCATION.csv> <OUTPUTSTUB>\n"


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



