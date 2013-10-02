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
        {'name':'Dissemination area', 'code':'DA', 'codeLength':8}
    ]
# nullRecord= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
dataDictionary = [
        ["UID",""],
        ["GEOGRAPHY","Geography"],
        ["TMOTHTONG","Total - Detailed mother tongue"],
        ["M_SNGLERES","Single responses"],
        ["M_ENGLISH","English"],
        ["M_FRENCH","French"],
        ["M_NONOFFI","Non-official languages"],
        ["M_ALGONQUI","Algonquin"],
        ["M_ATIKAMEK","Atikamekw"],
        ["M_BLACKFOO","Blackfoot"],
        ["M_CARRIER","Carrier"],
        ["M_CHILCOTI","Chilcotin"],
        ["M_CREE","Cree languages"],
        ["M_SIOUAN","Siouan languages"],
        ["M_DENE","Dene"],
        ["M_DOGRIB","Tlicho (Dogrib)"],
        ["M_GITKSAN","Gitksan"],
        ["M_INUINNAQ","Inuinnaqtun"],
        ["M_INUKTITU","Inuktitut"],
        ["M_KUTCHIN","Gwich'in"],
        ["M_MALECITE","Malecite"],
        ["M_MIKMAQ","Mi'kmaq"],
        ["M_MOHAWK","Mohawk"],
        ["M_MONTAGNA","Innu/Montagnais"],
        ["M_NISGAA","Nisga'a"],
        ["M_NSLAVE","North Slavey (Hare)"],
        ["M_OJIBWAY","Ojibway"],
        ["M_OJICREE","Oji-Cree"],
        ["M_SHUSWAP","Shuswap (Secwepemctsin)"],
        ["M_SSLAVE","South Slavey"],
        ["M_TLINGIT","Tlingit"],
        ["M_ITALIAN","Italian"],
        ["M_PORTUGUE","Portuguese"],
        ["M_ROMANIAN","Romanian"],
        ["M_SPANISH","Spanish"],
        ["M_DANISH","Danish"],
        ["M_DUTCH","Dutch"],
        ["M_FLEMISH","Flemish"],
        ["M_FRISIAN","Frisian"],
        ["M_GERMAN","German"],
        ["M_NORWEGIA","Norwegian"],
        ["M_SWEDISH","Swedish"],
        ["M_YIDDISH","Yiddish"],
        ["M_BOSNIAN","Bosnian"],
        ["M_BULGARIA","Bulgarian"],
        ["M_CROATIAN","Croatian"],
        ["M_CZECH","Czech"],
        ["M_MACEDONI","Macedonian"],
        ["M_POLISH","Polish"],
        ["M_RUSSIAN","Russian"],
        ["M_SERBIAN","Serbian"],
        ["M_SERBCROA","Serbo-Croatian"],
        ["M_SLOVAK","Slovak"],
        ["M_SLOVENIA","Slovenian"],
        ["M_UKRAINIA","Ukrainian"],
        ["M_LATVIAN","Latvian"],
        ["M_LITHUANI","Lithuanian"],
        ["M_ESTONIAN","Estonian"],
        ["M_FINNISH","Finnish"],
        ["M_HUNGARIA","Hungarian"],
        ["M_GREEK","Greek"],
        ["M_ARMENIAN","Armenian"],
        ["M_TURKISH","Turkish"],
        ["M_AMHARIC","Amharic"],
        ["M_ARABIC","Arabic"],
        ["M_HEBREW","Hebrew"],
        ["M_MALTESE","Maltese"],
        ["M_SOMALI","Somali"],
        ["M_TIGRIGNA","Tigrigna"],
        ["M_BENGALI","Bengali"],
        ["M_GUJARATI","Gujarati"],
        ["M_HINDI","Hindi"],
        ["M_KURDISH","Kurdish"],
        ["M_PANJABI","Panjabi (Punjabi)"],
        ["M_PASHTO","Pashto"],
        ["M_PERSIAN","Persian (Farsi)"],
        ["M_SINDHI","Sindhi"],
        ["M_SINHALA","Sinhala (Sinhalese)"],
        ["M_URDU","Urdu"],
        ["M_MALAYALA","Malayalam"],
        ["M_TAMIL","Tamil"],
        ["M_TELUGU","Telugu"],
        ["M_JAPANESE","Japanese"],
        ["M_KOREAN","Korean"],
        ["M_CANTONES","Cantonese"],
        ["M_CHINESE","Chinese, n.o.s."],
        ["M_MANDARIN","Mandarin"],
        ["M_TAIWANES","Taiwanese"],
        ["M_LAO","Lao"],
        ["M_KHMER","Khmer (Cambodian)"],
        ["M_VIETNAME","Vietnamese"],
        ["M_BISAYAN","Bisayan languages"],
        ["M_ILOCANO","Ilocano"],
        ["M_MALAY","Malay"],
        ["M_TAGALOG","Tagalog (Pilipino, Filipino)"],
        ["M_AKAN","Akan (Twi)"],
        ["M_SWAHILI","Swahili"],
        ["M_CREOLES","Creoles"],
        ["M_OTHER","Other languages"],
        ["M_MULTIPLE","Multiple responses"],
        ["M_ENGFRE","English and French"],
        ["M_ENGNONO","English and non-official language"],
        ["M_FRENONO","French and non-official language"],
        ["M_ENGFRENO","English, French and non-official language"]
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
        if int(searchId.groups()[0][0:2]) == provinceCodes['BC']:
            if checkData( row ):
                rowId = int( searchId.groups()[0] ) 
    return rowId,row


def checkData( d ):
    try:
        float( d[1] )
        return True
    except ValueError:
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
    print "python " + sys.argv[0] + " <LANGUAGE.csv> <OUTPUTSTUB>\n"


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



