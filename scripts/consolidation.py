import sys
import os
import csv
import hashlib

path = "../dataset/"
outputpath = "../dataset/data.csv"

# fingerprint dictionary
fpdict = {}

# output file pointer
ofp = open(outputpath, "w", encoding="utf-8")
writer = csv.writer(ofp, dialect='excel', lineterminator='\n')
headerWritten = False

# method to find fingerprint
def getFp(row, delim=";"):
    return hashlib.md5(delim.join(row).encode('utf-8')).hexdigest()

countTotal = 0
countWritten = 0

headersIndex = {}
for i in range(1, 10):
    _path = path + "out." +str(i) +".csv"
    print ("[information] Reading: %s" % _path)


    with open(_path, "r", encoding="utf-8") as ifp:
        headerRow = False
        reader = csv.reader(ifp)

        headers = []
        for row in reader:
            if not headerRow:

                # write header if not written yet
                if not headerWritten:
                    writer.writerow(row)

                    # this is the first time the header is written
                    # so find the index for each header and create a map
                    for j, r in enumerate(row):
                        headersIndex[r] = j

                    headerWritten = True

                # create a list where ith index will store
                # where in the final row the element should be
                # palced; [i] -> j
                l = len(headersIndex)
                for j, r in enumerate(row):
                    if r not in headersIndex:
                        headersIndex[r] = l
                        l = l + 1
                    headers.append(headersIndex[r])

                headerRow = True
                continue

            # create an empty tmp row
            _trow = ['' for k in range(0, len(row))]

            # place the elements at jth position in their
            # respective mapping;
            for j, r in enumerate(row):
                _trow[headers[j]] = r

            fp = getFp(_trow)
            if fp not in fpdict:
                writer.writerow(_trow)
                countWritten = countWritten + 1
                fpdict[fp] = True

            countTotal = countTotal + 1

ofp.close()

print ("Total: %d" % countTotal)
print ("Unique: %d" % countWritten)
print ("Duplication: %0.3f %%" % ((countTotal - countWritten) / countTotal * 100))