# -------------------------------------------
# Classes to core crawling and HTTP task and data
# Normalization
# -------------------------------------------
import os
import sys
import json
import requests
import codecs
from Logger import FileLogger, ConsoleLogger, Logger

'''Normalized data model'''
class NormalizedData:
    '''Constructor'''
    def __init__(self, row):
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
        self.price = row['price']
        self.description = row['description']
        self.trackName = row['trackName']
        self.bundleId = row['bundleId']
        self.isVppDeviceBasedLicensingEnabled = row['isVppDeviceBasedLicensingEnabled']
        self.primaryGenreName = row['primaryGenreName']
        self.releaseDate = row['releaseDate']
        self.minimumOsVersion = row['minimumOsVersion']
        self.formattedPrice = row['formattedPrice']
        self.primaryGenreId = row['primaryGenreId']
        

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

'''Data Model for response of request'''
class CoreResponse:
    def __init__(self, success, headers=False):
        self.success = success
        self.headers = headers

    def Set(self, result):
        self.results = []
        for row in result['results']:
            self.results.append(NormalizedData(row))

        return self

    def SetResponseCode(self, code):
        self.code = code
        return self

    def GetHeaders(self):
        return self.headers

'''Class to abstract out http request response'''
class Core:
    def __init__(self, URL, logger):
        self.__base = URL
        self.logger = logger
    
    def Get(self, params):
        url = self.__getUrl(params)
        self.logger.Log("Requesting: %s" % url)

        req = requests.get(url)
        if req.status_code == requests.codes.ok:
            ret = CoreResponse(True, req.headers)
            return ret.Set(req.json())
        else:
            ret = CoreResponse(False, req.headers)
            return ret.SetResponseCode(req.status_code)

    def __getUrl(self, params):
        i = 0
        url = self.__base
        for k,v in params.items():
            if i > 0:
                url = url +'&'
            i = i + 1

            url = url + k +'=' +v
        return url
