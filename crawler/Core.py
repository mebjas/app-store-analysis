# -------------------------------------------
# Classes to help with core crawling tasks 
# Involves making HTTP requests to APPLE API Endpoint
# retreiving results and returns json objects
#
# NOTE: these classes don't handle retries they have to be
# explicitly handled as per business logic
# -------------------------------------------

import os
import sys
import json
import requests
import codecs
from Logger import FileLogger, ConsoleLogger, Logger

class NormalizedData:
    '''
    Normalized data model for data retrieved from apple apis
    TODO: introduce properties for icons
    '''

    def __init__(self, row):
        '''Constructor'''

        self.kind = row['kind']
        self.features = row['features']
        self.advisories = row['advisories']
        self.trackCensoredName = row['trackCensoredName']
        self.fileSizeBytes = row['fileSizeBytes']
        self.contentAdvisoryRating = row['contentAdvisoryRating']
        self.genreIds = row['genreIds']
        self.currentVersionReleaseDate = row['currentVersionReleaseDate']
        self.currency = row['currency']
        self.wrapperType = row['wrapperType']
        self.version = row['version']
        self.artistName = row['artistName']
        self.artistId = row['artistId']
        self.genres = row['genres']
        self.description = row['description']
        self.trackName = row['trackName']
        self.bundleId = row['bundleId']
        self.isVppDeviceBasedLicensingEnabled = row['isVppDeviceBasedLicensingEnabled']
        self.primaryGenreName = row['primaryGenreName']
        self.releaseDate = row['releaseDate']
        self.minimumOsVersion = row['minimumOsVersion']
        self.primaryGenreId = row['primaryGenreId']
        
        try:
            self.price = row['price']
            self.formattedPrice = row['formattedPrice']
        except:
            self.price = 0
            self.formattedPrice = 0

        try:
            self.averageUserRating = row['averageUserRating']
            self.userRatingCount = row['userRatingCount']
        except:
            self.averageUserRating = None
            self.userRatingCount = None

        try:
            self.avgUserRatingCV = row['averageUserRatingForCurrentVersion']
            self.userRatingCountCV = row['userRatingCountForCurrentVersion']
        except:
            self.avgUserRatingCV = None
            self.userRatingCountCV = None

        try:
            self.sellerUrl = row['sellerUrl']
        except:
            self.sellerUrl = None

        try:
            self.releaseNotes = row['releaseNotes']
        except:
            self.releaseNotes = None

class CoreResponse:
    '''
    Data Model for response of request
    '''

    def __init__(self, success, headers=False):
        '''Constructor'''

        self.success = success
        self.headers = headers
        self.results = []

    def Set(self, result):
        '''Sets the results property'''

        for row in result['results']:
            self.results.append(NormalizedData(row))

        return self

    def SetResponseCode(self, code):
        '''Method to set response code'''

        self.code = code
        return self

    def GetHeaders(self):
        '''Gets the header property'''

        return self.headers

class Core:
    '''
    Class to abstract out http request response
    '''

    def __init__(self, baseurl, logger):
        '''Constructor'''

        self.__base = baseurl
        self.logger = logger

    def __getUrl(self, params):
        '''private method to generate url based on params'''

        i = 0
        url = self.__base
        for k,v in params.items():
            if i > 0:
                url = url +'&'
            i = i + 1

            url = url + k +'=' +v
        return url

    def Get(self, params):
        '''
        Gets the data from apple apis based on params
        @returns data with results if response is OK (200)
        @returns data with no reslts if response is not OK (200)
        '''

        url = self.__getUrl(params)
        self.logger.Log("Requesting: %s" % url)

        req = requests.get(url)
        if req.status_code == requests.codes.ok:
            ret = CoreResponse(True, req.headers)
            return ret.Set(req.json())
        else:
            ret = CoreResponse(False, req.headers)
            return ret.SetResponseCode(req.status_code)