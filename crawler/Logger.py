# -------------------------------------------
# Classes to deal with logging and monitoring
# -------------------------------------------

import sys
import os
from datetime import datetime
from abc import ABC, abstractmethod

class BaseLogger(ABC):
    '''Base logger class'''

    def __init__(self):
        '''Constructor'''

        self.__nextLogger = None
        super().__init__()

    def AddNextLogger(self, logger):
        '''Method to add next logger to the chain of responsibility'''

        if self.__nextLogger:
            raise 'Next Logger already set';

        self.__nextLogger = logger

    def passToNextLogger(self, message):
        '''Method to pass log to next logger in chain'''

        if self.__nextLogger:
            self.__nextLogger.Log(message)

    def constructMessage(self, message):
        '''Method to construct the message'''
        '''TODO: add code to deal with warning error enums'''

        return "[ " +datetime.now().strftime("%Y-%m-%d %H:%M:%S") +" ] " +message +"\n"

class FileLogger(BaseLogger):
    '''File logger class'''
    
    def __init__(self, filepath):
        '''Constructor'''

        self.__path = filepath
        self.__ofp = open(filepath, 'a')
        super().__init__()

    def Log(self, message):
        '''Public logging method'''

        self.__ofp.write(self.constructMessage(message))
        self.passToNextLogger(message)

    def __exit__(self, exc_type, exc_value, traceback):
        '''Exit method'''

        self.__ofp.close()

class ConsoleLogger(BaseLogger):
    '''Console Logger class'''
    
    def __init__(self):
        '''Constructor'''

        super().__init__()

    def Log(self, message):
        '''Public logging method'''

        print (self.constructMessage(message))
        self.passToNextLogger(message)

class Logger:
    '''Logger class'''
    
    def __init__(self, logger):
        '''Constructor'''

        self.__logger = logger

    def __enter__(self):
        '''entry method'''

        return self

    def Log(self, message):
        '''main logging method'''
    
        self.__logger.Log(message)