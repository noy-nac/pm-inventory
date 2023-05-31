
from os import close
import re
import csv

class ItemMap:

    def __init__(self, strictness):
        self.itemMap = dict()
        self.strictness = strictness

    def addItem(self, item, binID):

        #print('in add item')

        addKey = tuple((item, binID))

        self.itemMap[addKey] = []
        
        for k in self.itemMap.keys():
            if k != addKey and stringDist(k[0][1], item[1]) <= 1.0 - self.strictness:
                self.itemMap[k].append(addKey)
                self.itemMap[addKey].append(k)

    def __getitem__(self, key):
        return self.itemMap[key]

    def getItemMap(self):
        return self.itemMap

    def printSubstitutionReport(self, maxSubs, item):
        subsList = self.itemMap[item]
        for i in range(min(len(subsList),3)):
            print('              #', subsList[i][1], ' -- ', subsList[i][0][1])




class BinGroup:
    
    def __init__(self):
        self.binList = [] # kept sorted internally
        self.itemSuperset = []

    def addBin(self, binObj):
        #print('addBin')
        pos = len(self.binList)
        for b in self.binList:
            if binObj.getBinID() < b.getBinID():
                pos -= 1
            else:
                break

        self.binList.insert(pos, binObj)

        # TODO - be less lazy???
        for item in binObj.getItems():
            self.itemSuperset.append(tuple((item, binObj.getBinID())))

    def printGroupReport(self, itemMap):

        print("BIN GROUP REPORT")
        pos = 1
        for b in self.binList:
            print('\n')
            print("{:0>3}.".format(pos), "/", b.getBinTitle(), "-- ID #", b.getBinID())

            b.printInventoryReport()
            b.printDiscrepancyReport(self.itemSuperset, itemMap)
            pos += 1


class Bin:

    STARTS_WITH_QUANT = re.compile('(\d+\s[^(ML)L(CM)M(KM)G(KG)(FT)(IN)(YD)(LB)(LBS)(FOOT)(INCH)(YARD)(OZ)X].*)|(\(\d+\)\s[^(ML)L(CM)M(KM)G(KG)(FT)(IN)(YD)(LB)(LBS)(FOOT)(INCH)(YARD)(OZ)X].*)')
    NUMBER = re.compile('\d+')

    def __init__(self, binID, binTitle):
        self.binID = binID
        self.binTitle = binTitle
        self.itemList = []
        self.missing = []

    def addItem(self, item):
        quant = 1
        if re.match(Bin.STARTS_WITH_QUANT, item.upper()):
            quant = re.search(Bin.NUMBER, item).group(0)
            quant = int(quant)
        if quant < 1:
            raise Exception('Item quantity is negative or zero', 'item: `', item, '` / quant:', quant)

        self.itemList.append(tuple((quant, item)))
    
    def printDiscrepancyReport(self, itemSuperset, itemMap):
        print("       Missing: ")

        for item in itemSuperset:

            found = False
            for likeItem in itemMap[item]:
                if likeItem[0] in self.itemList:
                    found = True
                    break

            if not found:
                print("         ", item[0][1], "/ check bins: ")
                itemMap.printSubstitutionReport(3, item)

    def printInventoryReport(self):
        print("       Contains: ")
        
        for item in self.itemList:
            print("         ", item[1])

    def getBinID(self):
        return self.binID

    def getBinTitle(self):
        return self.binTitle

    def getItems(self):
        return self.itemList




def getBinList(fileName):
    with open(fileName) as csvFile:
        
        binList = []
        thisBin = None

        csvReader = csv.reader(csvFile)

        # spend header
        next(csvReader)

        count = 1

        for row in csvReader:
            bID = row[0]
            bTitle = row[1]
            bItemData = row[2]

            if bID != '' and bTitle != '':

                thisBin = Bin(bID, bTitle)
                binList.append(thisBin)

            if bItemData == '':
                continue
            
            thisBin.addItem(bItemData)

        return binList

def getBinGroups(binList):

    binCount = len(binList)

    binGroupList = []

    closenessMatrix = []

    for i in range(0, binCount):
        closenessMatrix.append([])

        for j in range(i + 1, binCount):
            closenessMatrix[i].append(stringDist(binList[i].getBinTitle(), binList[j].getBinTitle()))

    needsGroup = [True for b in binList]

    # not ideal but whateves
    for i in range(0, binCount):

        if needsGroup[i]:

            thisGroup = BinGroup()
            binGroupList.append(thisGroup)

            thisGroup.addBin(binList[i])
            needsGroup[i] = False

            closenessArray = closenessMatrix[i]

            for j in range(0, len(closenessArray)):

                if closenessArray[j] < 0.10:
                    thisGroup.addBin(binList[i + j + 1])
                    needsGroup[i + j + 1] = False
    
    return binGroupList




def stringDist(str1, str2):
    str1 = str1.upper()
    str2 = str2.upper()

    words1 = re.split('\s|\\|,|\(|\)|/|\."', str1)
    words2 = re.split('\s|\\|,|\(|\)|/|\."', str2)

    # remove every thing before the word `of`
    try:
        words1 = words1[words1.index('OF')+1:]
    except ValueError:
        pass
    try:
        words2 = words2[words2.index('OF')+1:]
    except ValueError:
        pass

    # remove numbers
    words1 = [w for w in words1 if not re.match(Bin.NUMBER, w)]
    words2 = [w for w in words2 if not re.match(Bin.NUMBER, w)]

    #print(words1)
    #print(words2)

    dist = 1
    maxDist = 0
    epsilon = 0.01

    for w1 in words1:
        for w2 in words2:
            mhp = minHammingProp(w1, w2)

            # helps with sortability
            # multiple perfect word matches trigger epsilon to decrease
            # meaning the final average is lower
            if mhp < epsilon:
                mhp = epsilon
                epsilon = epsilon / 2

            dist += mhp ** -1
            maxDist+=1
    
    return maxDist / dist

def minHammingProp(str1, str2):
    
    str1_len = len(str1)
    str2_len = len(str2)

    short_str = str1 if str1_len <= str2_len else str2
    long_str  = str2 if str1_len <= str2_len else str1

    short_len = len(short_str)
    long_len = len(long_str)

    if short_len <= 0 or long_len <= 0:
        return 1

    offset_max = long_len - short_len

    minDist = 1000000

    for offset in range(0, 1 + offset_max):

        dist = 0

        for i in range(short_len):
            if short_str[i] != long_str[i + offset]:
                dist += 1
        
        minDist = dist if dist < minDist else minDist

    return (minDist + offset_max/2) / long_len


#print(stringDist("Electric Circuits", "Electric Circuits (paper circuits/scribble bots)"))
#print(stringDist("Electric Circuits", "Earth Scienc Kit"))
#print(stringDist("Earth Science Kit", "Electric Circuits (paper circuits/scribble bots)"))
#
#print(stringDist("can of worms", "bag of worms"))
#print(stringDist("can of worms", "bag of woms"))
#print(stringDist("Bag of 15 Plastic Disopsable Pipettes", "2 disposable 1 mL pipettes"))
#print(stringDist("Bag of 15 Plastic Disopsable Pipettes", "30 construction paper place mats"))

#print(stringDist("brown paper lunch bags", ""))

print('Loading inventory files into memory')
binsSp23 = getBinList('sp 2023.csv')
binsFa22 = getBinList('fa 2022.csv')
binList = []

for b in binsSp23:
    binList.append(b)
for b in binsFa22:
    binList.append(b)
print('Inventory files loaded as BinList of length', len(binList))

print('Using inventory BinList to create an ItemMap')
itemMap = ItemMap(0.9)

count = 1
for b in binList:
    for i in b.getItems():
        itemMap.addItem(i, b.getBinID())
        count += 1

        if (count % 100) == 0:
            print("    processed", count, "items")

#for b in binsFa22:
#    for i in b.getItems():
#        itemMap.addItem(i, b.getBinID())
#        count += 1
#
#        if (count % 100) == 0:
#            print("    processed", count, "items")

print('ItemMap loaded sucessfully, contains', len(itemMap.getItemMap()), 'items')

#for k,v in im.getItemMap().items():
#    print(k, v)

print('Parsing BinList into BinGroups')

binGroupList = getBinGroups(binList)

print('Parsed out',len(binGroupList),' BinGroups from', len(binList), 'bins')

#bg = BinGroup()

#counter = 0
#for b in binsSp23:
    #if(counter > 2):
    #    break
#    bg.addBin(b, itemMap)
#    counter += 1

#for b in binsSp23:
#    bg.addBin(b)
#for b in binsFa22:
#    bg.addBin(b)

print('Printing report')

for binGroup in binGroupList:
    binGroup.printGroupReport(itemMap)

#for b in binsSp23:
#    print(b.getItems())
#for b in binsFa22:#
#    print(b.getItems())






