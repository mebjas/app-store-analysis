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
        self.__dict_path = 'meta.dict.bat'
        ## this item will store the items that
        ## have been scrapped and stored already
        self.__deserialize()
    
    '''Public method to update the state'''
    def Update(self, i, j, k):
        self.dict['start'] = [i, j, k]
        self.__serialize()

    '''private method to deserialize if metadata exist in file'''
    def __deserialize(self):
        try:
            with open(self.__dict_path, 'r') as ifp:
                self.dict = json.load(ifp)
                self.logger.Log("[Success] Deserialisation success")
                self.logger.Log("Item Count: %d" % (len(self.dict.items())))
        except BaseException as e:
            self.logger.Log("[Warning] Unable to open %s" % self.__dict_path)
            self.logger.Log("[Error] %s" % str(e))
            self.dict = {'start': [0, 12, 16]}
            

    '''PRIVATE METHOD to serialize state object'''
    def __serialize(self):
        try:
            with open(self.__dict_path, 'w') as ofp:
                json.dump(self.dict, ofp)
                self.logger.Log("[Success] Serialization success")
        except BaseException as e:
            self.logger.Log("[Warning] Unable to write %s" % self.__dict_path)
            self.logger.Log("[Info] dump of state: %s" % json.dumps(self.dict))
            self.logger.Log("[Error] %s" % str(e))

    '''EXIT METHOD'''
    def __exit__(self, exc_type, exc_value, traceback):
        self.Serialize()

'''Actual spider logic - wait, retries and all'''
class Spider:
    '''Constructor'''
    def __init__(self, logger, core, exporter):
        self.logger = logger
        self.core = core
        self.exporter = exporter

        self.state = SpiderState(logger)
        self.requestPerMin = 15
        self.retryLimit = 10
        self.timeout = 65
        self.cooloffTimeout = 300
        self.params = {'term': None,
            'country': 'US',
            'media': 'software',
            'limit': '200'}

    '''Public method to start the process'''
    def Start(self):
        cycleCount = 0

        start = [i for i in self.state.dict['start']]

        for i in range(start[0], 26):
            for j in range(start[1], 26):
                for k in range(start[2], 26):
                    self.params['term'] = chr(97 +i) +chr(97 +j) +chr(97 +k)
                    self.__crawl()
                    self.state.Update(i, j, k)

                    cycleCount = cycleCount + 1
                    if cycleCount >= self.requestPerMin:
                        self.logger.Log("Sleeping for %d seconds" % self.timeout)
                        time.sleep(self.timeout)
                        cycleCount = 0

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