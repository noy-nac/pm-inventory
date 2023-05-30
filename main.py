
import re
import csv

class BinGroup:
    
    def __init__(self):
        self.bins = []
        self.itemSuperset = []

    def addBin(binObj, itemMap):
        self.bins.append[binObj]

    def printReport():


class ItemMap:

    def __init__(self, strictness):
        self.itemMap = dict()
        self.strictness = strictness

    def addItem(self, item, binID):

        addKey = tuple((item, binID))

        self.itemMap[addKey] = []
        
        for k in self.itemMap.keys():
            if k != addKey and stringDist(k[0], item) <= 1.0 - self.strictness:
                self.itemMap[k].append(addKey)
                self.itemMap[addKey].append[k]


class Bin:

    STARTS_WITH_NUMBER = re.compile('(\d+\s.*)|(\(\d+\)\s.*)')
    NUMBER = re.compile('\d+')

    def __init__(self, binID, binTitle):
        self.binID = binID
        self.binTitle = binTitle
        self.items = []
        self.missing = []

    def addItem(self, item):
        quant = 1
        if re.match(Bin.STARTS_WITH_NUMBER, item):
            quant = re.search(Bin.NUMBER, item).group(0)
            quant = int(quant)
        if quant < 1:
            raise Exception('Item quantity is negative or zero', 'item', item, 'quant', quant)

        self.items.append(tuple((quant, item)))

    def getBinID(self):
        return self.binID

    def getBinTitle(self):
        return self.binTitle

    def getItems(self):
        return self.items

    def sortItems(self):
        pass



def getBinList(fileName):
    with open(fileName) as csvFile:
        
        bins = []
        thisBin = None

        csvReader = csv.reader(csvFile)

        # spend header
        next(csvReader)

        for row in csvReader:
            
            bID = row[0]
            bTitle = row[1]
            bItemData = row[2]

            if bID != '' and bTitle != '':

                thisBin = Bin(bID, bTitle)
                bins.append(thisBin)

            thisBin.addItem(bItemData)

        return bins



def stringDist(str1, str2):
    str1 = str1.upper()
    str2 = str2.upper()

    words1 = re.split('\s|\\|,', str1)
    words2 = re.split('\s|\\|,', str2)

    print(words1)
    print(words2)

    dist = 1
    maxDist = 0

    for w1 in words1:
        for w2 in words2:
            dist *= (0.5 + 0.5*hammingProp(w1, w2))
            maxDist+=1
    
    return dist



def hammingProp(str1, str2):
    
    str1_len = len(str1)
    str2_len = len(str2)

    short_str = str1 if str1_len <= str2_len else str2
    long_str  = str2 if str1_len <= str2_len else str1

    short_len = len(short_str)
    long_len = len(long_str)

    offset_max = long_len - short_len

    minDist = 1000000

    for offset in range(0, 1 + offset_max):

        dist = 0

        for i in range(short_len):
            if short_str[i] != long_str[i + offset]:
                dist += 1
        
        minDist = dist if dist < minDist else minDist

    return dist / short_len


print(stringDist("can of worms", "bag of worms"))
print(stringDist("can of worms", "bag of woms"))
print(stringDist("Bag of 15 Plastic Disopsable Pipettes", "2 disposable 1 mL pipettes"))
print(stringDist("Bag of 15 Plastic Disopsable Pipettes", "30 construction paper place mats"))

binsSp23 = getBinList('sp 2023.csv')
binsFa22 = getBinList('fa 2022.csv')

#for b in binsSp23:
#    print(b.getItems())
#for b in binsFa22:#
#    print(b.getItems())

print(len(binsSp23))
print(len(binsFa22))





