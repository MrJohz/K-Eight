import os, os.path
import re
import gzip
import random
import numbers
import datetime

#############################################
### HELPER FUNCTIONS ########################
#############################################

def getFileName():
    """Returns the date in YYYY-MM-DD format, prepended by 'regionsdd-'"""
    d = datetime.datetime.today()
    strDate = '{:%Y-%m-%d}'.format(d)
    return 'regionsdd-' + strDate + '.xml.gz'

def getTag(line):
    patt = "(<)(.*?)(>)"
    matches = re.search(patt, line)
    if not matches:
        print line
    return matches.group(2)

def removeTag(line, tag=None):
    if not tag:
        tag = getTag(line)
    tagLength = len(tag)
    tagLength += 2
    return line.strip()[tagLength:-(tagLength+1)]

#############################################
### ERROR CLASSES ###########################
#############################################

class DumpHandlerError(Exception):
    pass

class DumpIOError(DumpHandlerError, IOError):
    pass

#############################################
### MAIN CLASSES ############################
#############################################

class ApiHandler(object):
    def __init__(self, userAgent):
        from urllib import FancyURLopener
        class ApiOpener(FancyURLopener, object):
            version = userAgent
        self.apiOpener = ApiOpener()

    def getDump(self):
        fileName = getFileName()
        link = 'http://www.nationstates.net/pages/regions.xml.gz'
        dir = "./tools/nstoolkit/dumps/"
        dirname = os.path.join(dir, fileName)
        if fileName in os.listdir(dir):
            pass
        else:
            self.apiOpener.retrieve(link, dirname)
        return RegionDump(dirname)

class RegionDump(object):
    def __init__(self, fileName=getFileName()):
        open(os.path.abspath(fileName)).close()
        self.dumpFile = gzip.open(fileName, 'rb')
        self._regionStarts = []
        self._regionPos = 0
        self._examineFile()

    def _examineFile(self):
        pos = self.dumpFile.tell()
        for line in self.dumpFile:
            if line.strip() == "<REGION>":
                self._regionStarts.append(pos)
            pos = self.dumpFile.tell()
        self.dumpFile.seek(0)

    def regions(self):
        nextLine = False
        for line in self.dumpFile:
            if line.strip() == "<REGION>":
                nextLine = True
            elif nextLine:
                yield removeTag(line, 'NAME')
                nextLine = False
            elif line.strip() == "</REGION>":
                self._regionPos += 1

    def iterAttr(self, attribute):
        nextLine = False
        for line in self.dumpFile:
            if line.strip() == "<REGION>":
                nextLine = True
            elif nextLine and line.startswith('<NAME>'):
                name = removeTag(line, 'NAME')
            elif nextLine and line.startswith('<'+attribute.upper()+'>'):
                try:
                    yield name, removeTag(line, attribute.upper())
                except NameError:
                    continue
            elif line.strip() == "</REGION>":
                self._regionPos += 1
        

    def seek(self, offset, whence=0):
        self.dumpFile.seek(offset, whence)

    def regionseek(self, offset, whence=0):
        whence = int(whence)
        if whence == 1:
            self._regionPos += offset
            if postion > len(self._regionStarts) - 1:
                self._regionPos = len(self._regionStarts) - 1

        elif whence == 2:
            self._regionPos = len(self._regionStarts)
            self._regionPos += offset
            if self._regionPos > len(self._regionStarts) - 1:
                self._regionPos = len(self._regionStarts) - 1
        else:
            self._regionPos = 0
            self._regionPos += offset
            if self._regionPos > len(self._regionStarts) - 1:
                self._regionPos = len(self._regionStarts) - 1

        pos = self._regionStarts[self._regionPos]
        self.dumpFile.seek(pos)

    def next(self):
        region = False
        linesList = []
        while not linesList:
            for line in self.dumpFile:
                if line.strip() == "<REGION>":
                    region = True
                elif line.strip() == "</REGION>":
                    region = False
                    self._regionPos += 1
                    break
                elif region:
                    #linesList[getTag(line)] = removeTag(line)
                    linesList.append(line)
        return linesList
