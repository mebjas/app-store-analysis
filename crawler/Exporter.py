# -------------------------------------------
# Class to export data to csv
# -------------------------------------------
import os
import sys
import csv
import json
from Logger import FileLogger, ConsoleLogger, Logger
from Core import NormalizedData

'''Class to export data to csv'''
class CSVExporter:
    '''Constructor'''
    def __init__(self, outputpath):
        self.__out = outputpath
        self.__ofp = open(outputpath, 'a', encoding="utf-8")
        self.writer = csv.writer(self.__ofp, dialect='excel', lineterminator='\n')

        # TODO: check if the file already exists and retrieve the headers
        self.columns = None

    '''Method to actually write data to csv'''
    def Write(self, row):
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

    '''Method to explicitly close the file stream'''
    def Close(self):
        self.__ofp.close()
        self.__ofp = None

    '''Method to implocitly close the file stream'''
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.__ofp.close()
        except:
            pass

'''final exporter class'''
class Exporter:
    '''Constructor'''
    def __init__(self, exporter):
        self.exporter = exporter

    '''Method to actually write data to csv'''
    def Write(self, row):
        self.exporter.Write(row)

    '''Method to explicitly close the file stream'''
    def Close(self):
        self.exporter.Close()

    '''Method to implocitly close the file stream'''
    def WriteRows(self, rows):
        for row in rows:
            self.exporter.Write(row)