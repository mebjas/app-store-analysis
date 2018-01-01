from Logger import FileLogger, ConsoleLogger, Logger
from Core import Core
from Exporter import Exporter, CSVExporter
from Spider import Spider

### TODO: add a self managing code, that will run the things, and upon
### failure, move the files to appropriate location and restart
BASEURL = 'https://itunes.apple.com/search?'

reincarnation = 0

while True:
    try:
        reincarnation = reincarnation + 1
        print ("Reincarnation: ", reincarnation)
        # logging things
        flog = FileLogger('./log.txt')
        flog.AddNextLogger(ConsoleLogger())
        logger = Logger(flog)

        # base url for the core
        core = Core(BASEURL, logger)

        # exporter
        exporter = Exporter(CSVExporter("out.csv"))

        spider = Spider(logger, core, exporter)
        spider.Start()
        print ("Task Over")
        break
    except:
        print (sys.exc_info()[0])
        print ("Some exception: restarting")
        continue
