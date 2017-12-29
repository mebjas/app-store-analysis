# -------------------------------------------
# Classes to deal with logging and monitoring
# -------------------------------------------
import sys
import os
import json
import requests
import time
from Logger import FileLogger, ConsoleLogger, Logger
from Core import Core
from Exporter import Exporter, CSVExporter

'''
Class to deal with state of crawler
So that we can restart from where it exited
'''
class SpiderState:
    '''CONSTRUCTOR'''
    def __init__(self, logger):
        self.logger = logger
        # self.__dict_path = 'meta.dict.bat'
        self.__dict_path = 'dict.txt'
        self.__dict = {}
        self.__deserialize()

        # create a file pointer for append
        self.__ofp = open(self.__dict_path, 'a')
    
    '''Public method to update the state'''
    def Update(self, term):
        self.__dict[term] = True
        self.__ofp.write(term +"\n")

    '''Public Method to check if crawl is needed for a specific term'''
    def CrawlNeeded(self, term):
        return term not in self.__dict

    '''private method to deserialize if metadata exist in file'''
    def __deserialize(self):
        try:
            with open(self.__dict_path, 'r') as ifp:
                lines = [line.rstrip('\n') for line in ifp]
                self.logger.Log("[Success] Deserialisation success for done dict")
                self.logger.Log("[Information] %d items already dealt with, %d left" % (len(lines), (26*26*26 - len(lines))))

                for line in lines:
                    if line.strip() != "":
                        self.__dict[line.strip()] = True

                self.logger.Log("[Success] __done_dict created")

        except BaseException as e:
            self.logger.Log("[Warning] [Probable] Unable to open %s" % self.__dict_path)
            self.logger.Log("[Error] %s" % str(e))
            sys.exit(0)

    # '''EXIT METHOD'''
    def __exit__(self, exc_type, exc_value, traceback):
        self.__ofp.close()

'''Actual spider logic - wait, retries and all'''
class Spider:
    '''Constructor'''
    def __init__(self, logger, core, exporter):
        self.logger = logger
        self.core = core
        self.exporter = exporter

        self.state = SpiderState(logger)
        self.requestPerMin = 20
        self.retryLimit = 10
        self.timeout = 65
        self.cooloffTimeout = 65
        self.params = {'term': None,
            'country': 'US',
            'media': 'software',
            'limit': '200'}

    '''Public method to start the process'''
    def Start(self, verbose=False):
        cycleCount = 0

        for i in range(0, 26):
            for j in range(0, 26):
                for k in range(0, 26):
                    # check if term is already done
                    # crawl only if needed
                    term = chr(97 +i) +chr(97 +j) +chr(97 +k)
                    if self.state.CrawlNeeded(term):
                        self.params['term'] = term
                        self.__crawl()
                        self.state.Update(term)

                        cycleCount = cycleCount + 1

                        if cycleCount >= self.requestPerMin:
                            self.logger.Log("Sleeping for %d seconds" % self.timeout)
                            time.sleep(self.timeout)
                            cycleCount = 0
                    elif verbose:
                        self.logger.Log("Skipping: %s" % term)

    '''Private method to crawl data, load and send to exporter'''
    def __crawl(self, retry = 0):
        if retry == self.retryLimit:
            self.logger.Log("retry limit; exit")
            sys.exit(0)

        self.logger.Log("[info] CRAWL TERM: %s" % self.params['term'])
        data = self.core.Get(self.params)
        if not data.success:
            self.logger.Log("No success, wait for timeout")
            time.sleep(self.cooloffTimeout)
            self.__crawl(retry + 1)

        self.exporter.WriteRows(data.results)