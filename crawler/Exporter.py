# -------------------------------------------
# Class to export data to different output format
# TODO: think if we need a chain of responsibilities design pattern here?
#       if yes, think of an async method as all of them will involve
#       IO calls
# -------------------------------------------

import os
import sys
import csv
import json
from Logger import FileLogger, ConsoleLogger, Logger
from Core import NormalizedData

class DBExporter:
    '''Class to export data to some online DB'''

    def __init__(self, endpoint, connectionstring):
        '''Constructor'''

        # self.connection = function(endpoint, connectionstring)
        raise "NotImplementedException"

    def Write(self, row):
        '''Method to write a row to the DB connection'''

        raise "NotImplementedException"

    def Close(self):
        '''Method to close the connection'''

        raise "NotImplementedException"

    def __exit__(self, exc_type, exc_value, traceback):
        '''Method to implicitly close the connection'''

        raise "NotImplementedException"

class CSVExporter:
    '''Class to export data to csv'''

    def __init__(self, outputpath):
        '''Constructor'''

        self.__out = outputpath
        self.__ofp = open(outputpath, 'a', encoding="utf-8")
        self.writer = csv.writer(self.__ofp, dialect='excel', lineterminator='\n')

        # TODO: check if the file already exists and retrieve the headers
        self.columns = None

    def Write(self, row):
        '''Method to actually write data to csv'''

        # if columns are not retrieved that means this is the first row
        if not self.columns:
            self.columns = []
            kvp = vars(row)
            for k,v in kvp.items():
                self.columns.append(k)

            self.writer.writerow(self.columns)

        # Now get the actual data and dump it to file
        data = []
        kvp = vars(row)
        for column in self.columns:
            if isinstance(kvp[column], str):
                data.append(kvp[column])
            else:
                data.append(json.dumps(kvp[column]))

        self.writer.writerow(data)

    def Close(self):
        '''Method to explicitly close the file stream'''

        self.__ofp.close()
        self.__ofp = None

    def __exit__(self, exc_type, exc_value, traceback):
        '''Method to implicitly close the file stream'''

        try:
            self.__ofp.close()
        except:
            pass

class Exporter:
    '''final exporter class'''

    def __init__(self, exporter):
        '''Constructor'''

        self.exporter = exporter

    def Write(self, row):
        '''Method to actually write data to csv'''

        self.exporter.Write(row)

    def Close(self):
        '''Method to explicitly close the file stream'''

        self.exporter.Close()

    def WriteRows(self, rows):
        '''Method to implocitly close the file stream'''

        for row in rows:
            self.exporter.Write(row)