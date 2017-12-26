from Logger import FileLogger, ConsoleLogger, Logger
from Core import Core
from Exporter import Exporter, CSVExporter
from Spider import Spider

# logging things
flog = FileLogger('./log.txt')
flog.AddNextLogger(ConsoleLogger())
logger = Logger(flog)

# base url for the core
BASEURL = 'https://itunes.apple.com/search?'
core = Core(BASEURL, logger)

# exporter
exporter = Exporter(CSVExporter("out.csv"))

spider = Spider(logger, core, exporter)
spider.Start()