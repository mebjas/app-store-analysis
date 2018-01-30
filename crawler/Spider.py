# -------------------------------------------
# Classes to deal with crawling tasks; Deals with terms that
# are already crawled; Deals with request limit per minutes;
# Handles request failures, retries and cool off intervals
# -------------------------------------------

import sys
import os
import json
import requests
import time
from Logger import FileLogger, ConsoleLogger, Logger
from Core import Core
from Exporter import Exporter, CSVExporter

class SpiderState:
    '''
    Class to deal with state of crawler
    So that we can restart from where it exited
    '''

    def __init__(self, logger):
        '''CONSTRUCTOR'''

        # properties of this class
        self.logger = logger                    # logger chain object
        self.__dict_path = 'dict.txt'           # path of dictionary, meta file
                                                # this file contains keys that are already crawled
        self.__dict = {}                        # Map to hold keys already crawled
        
        # call private method to load the keys already crawled into memory
        self.__deserialize()

        # create a file pointer for append data to meta file, as more data is crawled
        # and loaded;
        self.__ofp = open(self.__dict_path, 'a')
    
    def __deserialize(self):
        '''private method to deserialize if metadata exist in file'''
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

    def __exit__(self, exc_type, exc_value, traceback):
        '''EXIT METHOD'''

        self.__ofp.close()

    def Update(self, term):
        '''
        Public method to update the state
        '''

        self.__dict[term] = True
        self.__ofp.write(term +"\n")

    def IsCrawlNeeded(self, term):
        '''
        Public Method to check if crawl is needed for a specific term
        '''

        return term not in self.__dict

class Spider:
    '''Class that implements actual spider logic wait, retries and all'''

    def __init__(self, logger, core, exporter):
        '''Constructor'''

        self.logger = logger                # chain of loggers
        self.core = core                    # instance of core object
        self.exporter = exporter            # instance of data exporter
        self.state = SpiderState(logger)    # instance of spider state
        self.requestPerMin = 20             # no of requests per minute (config)
                                            # TODO: load from config file
        self.retryLimit = 10                # limit for no of retries
                                            # TODO: load from config file
        self.timeout = 65                   # timeout after request limit reached
                                            # TODO: load from config file
        self.cooloffTimeout = 65            # timeout in case, != 200 status code from server
                                            # TODO: load from config file

        # default params to be sent to APPLE API
        self.params = {
            'term': None,
            'country': 'US',
            'media': 'software',
            'limit': '200'}

    def __crawl(self, retry = 0):
        '''Private method to crawl data, load and send to exporter'''
        if retry >= self.retryLimit:
            self.logger.Log("retry limit; exit")

            # TODO: this below is not the right approach! fix it!
            # @priority: high @labels: nextver
            sys.exit(0)

        self.logger.Log("[info] CRAWL TERM: %s" % self.params['term'])
        data = self.core.Get(self.params)

        if not data.success:
            self.logger.Log("No success, wait for timeout")
            time.sleep(self.cooloffTimeout)
            self.__crawl(retry + 1)

        self.exporter.WriteRows(data.results)

    def Start(self, verbose=False):
        '''Public method to start the process'''
        cycleCount = 0

        for i in range(0, 26):
            for j in range(0, 26):
                for k in range(0, 26):

                    # check if term is already done & crawl only if needed
                    term = chr(97 +i) +chr(97 +j) +chr(97 +k)

                    if self.state.IsCrawlNeeded(term):
                        self.params['term'] = term
                        self.__crawl()
                        self.state.Update(term)

                        cycleCount = cycleCount + 1

                        if cycleCount >= self.requestPerMin:
                            if verbose:
                                self.logger.Log("Sleeping for %d seconds" % self.timeout)

                            time.sleep(self.timeout)
                            cycleCount = 0
                    elif verbose:
                        self.logger.Log("Skipping: %s" % term)