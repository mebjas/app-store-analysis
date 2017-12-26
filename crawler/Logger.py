# -------------------------------------------
# Classes to deal with logging and monitoring
# -------------------------------------------
import sys
import os
from datetime import datetime
from abc import ABC, abstractmethod

'''Base logger class'''
class BaseLogger(ABC):
    '''Constructor'''
    def __init__(self):
        self.__nextLogger = None
        super().__init__()

    '''Method to add next logger to the chain of responsibility'''
    def AddNextLogger(self, logger):
        if self.__nextLogger:
            raise 'Next Logger already set';

        self.__nextLogger = logger

    '''Method to pass log to next logger in chain'''
    def passToNextLogger(self, message):
        if self.__nextLogger:
            self.__nextLogger.Log(message)

    '''TODO: add code to deal with warning error enums'''
    '''Method to construct the message'''
    def constructMessage(self, message):
        return "[ " +datetime.now().strftime("%Y-%m-%d %H:%M:%S") +" ] " +message +"\n"

'''File logger class'''
class FileLogger(BaseLogger):
    def __init__(self, filepath):
        self.__path = filepath
        self.__ofp = open(filepath, 'a')
        super().__init__()

    def Log(self, message):
        self.__ofp.write(self.constructMessage(message))
        self.passToNextLogger(message)

    def __exit__(self, exc_type, exc_value, traceback):
        self.__ofp.close()

'''Console Logger class'''
class ConsoleLogger(BaseLogger):
    def __init__(self):
        super().__init__()

    def Log(self, message):
        print (self.constructMessage(message))
        self.passToNextLogger(message)

'''Abstract Logger class'''
class Logger:
    def __init__(self, logger):
        self.__logger = logger

    def __enter__(self):
        return self

    def Log(self, message):
        self.__logger.Log(message)