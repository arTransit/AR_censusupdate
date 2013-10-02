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
        {'name':'Census Division', 'code':'CD', 'codeLength':4},
        {'name':'Census Subdivision', 'code':'CSD', 'codeLength':7},
        {'name':'Dissemination area', 'code':'DA', 'codeLength':8} ]
columnHeaders= "UID,NAME,TOTALPOP,MTPOP,M0_4,M5_9,M10_14,M15_19,M20_24,M25_29,M30_34,M35_39,M40_44,M45_49,M50_54,M55_59,M60_64,M65_69,M70_74,M75_79,M80_84,M85_89,M90_94,M95_99,MOVER100,FTPOP,F0_4,F5_9,F10_14,F15_19,F20_24,F25_29,F30_34,F35_39,F40_44,F45_49,F50_54,F55_59,F60_64,F65_69,F70_74,F75_79,F80_84,F85_89,F90_94,F95_99,FOVER100"
nullRecord= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
dataColumns = [
        'Geography',
        'Total - Age',
        '0 to 4 years',
        '5 to 9 years',
        '10 to 14 years',
        '15 to 19 years',
        '20 to 24 years',
        '25 to 29 years',
        '30 to 34 years',
        '35 to 39 years',
        '40 to 44 years',
        '45 to 49 years',
        '50 to 54 years',
        '55 to 59 years',
        '60 to 64 years',
        '65 to 69 years',
        '70 to 74 years',
        '75 to 79 years',
        '80 to 84 years',
        '85 to 89 years',
        '90 to 94 years',
        '95 to 99 years',
        '100 years and over' ]


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


def outputRecord( id, name, rA, rB, outputFiles):
    combinedRecord = [id, name, int( float(rA[0]) + float(rB[0]) )] + rA + rB 
    for i in range(0, len(geoLevels)):
        if id < 10 ** geoLevels[i]['codeLength']:
            outputFiles[i].write( ','.join( [str(f) for f in combinedRecord] ) + '\n')
            break


def processCensus( inputFiles, outputFiles ):
    #process input files as CSVs
    csvA,csvB = [getDictionaryFromCSV( file ) for file in inputFiles]

    for id in sorted( set(csvA.keys() + csvB.keys())):
        if (id in csvA.keys()) & (id in csvB.keys()):
            outputRecord( id, csvA[id][0], csvA[id][1:], csvB[id][1:], outputFiles ) 
        elif (id in csvA.keys()):
            print ">>processCensus: missing B:" + str(id)
            outputRecord( id, csvA[id][0], csvA[id][1:], nullRecord, outputFiles ) 
        else:  # id in csvB.keys()
            print ">>processCensus: missing A:" + str(id)
            outputRecord( id, csvB[id][0], nullRecord, csvB[id][1:], outputFiles ) 


def closeFiles( fileList ):
    for f in fileList:
        print ">>closeFiles - closing:" + f.name 
        f.close()


def getCommandLine():
    if (len(sys.argv) ==4):
        if os.path.isfile( sys.argv[1] ) & os.path.isfile( sys.argv[2] ):
            return sys.argv[1],sys.argv[2],sys.argv[3]
    return "","",""


def printUsage():
    print "Usage:"
    print "python " + sys.argv[0] + " <INPUT_MALE.csv> <INPUT_FEMALE.csv> <OUTPUTSTUB>\n"


if __name__ == "__main__":
    print "Format Census 2011"

    inputFileNameA,inputFileNameB,outputStub = getCommandLine()
    if (not inputFileNameA) & (not inputFileNameB):
        printUsage()
        sys.exit(1)

    else:
        print "Reading: %s, %s" % (inputFileNameA, inputFileNameB)
        print "Exporting: %s" % outputStub

        inputFiles = []
        inputFiles.append( open( inputFileNameA ))
        inputFiles.append( open( inputFileNameB ))
        outputFiles = createOutputFiles( outputStub )

        writeHeader( outputFiles )
        processCensus( inputFiles, outputFiles )
        closeFiles( inputFiles + outputFiles )



