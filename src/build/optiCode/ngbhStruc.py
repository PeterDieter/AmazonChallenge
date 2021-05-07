import random
import numpy as np

def randomSwapInZone(sequence, zoneList):
    randomZone = random.sample(range(0,len(zoneList)), 1)[0]
    if zoneList[randomZone] > 1:
        cumsumzoneList = np.cumsum(zoneList)
        if randomZone == 0:
            previousZoneCum = 1
        else:
            previousZoneCum = cumsumzoneList[randomZone-1] + 1

        i, j = random.sample(range(0,zoneList[randomZone]), 2)
        if i < j:
            i, j = j, i
        sequence[i+ previousZoneCum], sequence[j + previousZoneCum] = sequence[j + previousZoneCum], sequence[i+ previousZoneCum]
    return sequence, zoneList

def zoneSwap(sequence, zoneList):
    cumsumzoneList = np.cumsum(zoneList)
    randomZone1, randomZone2 = random.sample(range(0, len(zoneList)-2), 2)
    if randomZone1 < randomZone2:
        randomZone1, randomZone2 = randomZone2, randomZone1

    if randomZone1 == 0:
        previousZoneCum1 = 1
    else:
        previousZoneCum1 = cumsumzoneList[randomZone1-1] + 1
    if randomZone2 == 0:
        previousZoneCum2 = 1
    else:
        previousZoneCum2 = cumsumzoneList[randomZone2-1] + 1
    
    # Swap element in these zones
    sequence[previousZoneCum1:previousZoneCum1+zoneList[randomZone1]], sequence[previousZoneCum2:previousZoneCum2+zoneList[randomZone2]] = sequence[previousZoneCum2:previousZoneCum2+zoneList[randomZone2]], sequence[previousZoneCum1:previousZoneCum1+zoneList[randomZone1]]


    # Now change the zoneList
    zoneList[randomZone1],zoneList[randomZone2] = zoneList[randomZone2],zoneList[randomZone1]
    return sequence, zoneList

def inZoneTwoOptChange(sequence, zoneList):
    randomZone = random.sample(range(0, len(zoneList)), 1)[0]
    if zoneList[randomZone] > 1:
        cumsumzoneList = np.cumsum(zoneList)
        if randomZone == 0:
            previousZoneCum = 1
        else:
            previousZoneCum = cumsumzoneList[randomZone-1] + 1
        i, j = random.sample(range(0,zoneList[randomZone]), 2)
        if j < i:
            i, j = j, i
        sequence[previousZoneCum + i:previousZoneCum + j] = sequence[previousZoneCum + j - 1:previousZoneCum + i - 1:-1]
    
    return sequence, zoneList

def zoneNodeInsertion(sequence, zoneList):
    randomZone = random.sample(range(0, len(zoneList)), 1)[0]
    if zoneList[randomZone] > 1:
        cumsumzoneList = np.cumsum(zoneList)
        if randomZone == 0:
            previousZoneCum = 1
        else:
            previousZoneCum = cumsumzoneList[randomZone-1] + 1
        i, j = random.sample(range(0,zoneList[randomZone]), 2)

        temp = sequence[i+ previousZoneCum]
        sequence.pop(i+ previousZoneCum)
        sequence.insert(j+ previousZoneCum, temp)
    return sequence, zoneList


def zoneInsertion(sequence, zoneList):
    cumsumzoneList = np.cumsum(zoneList)
    randomZone1 = random.sample(range(0,len(zoneList)-2), 1)[0]
    randomZone2 = randomZone1+1
    if randomZone1 < randomZone2:
        randomZone1, randomZone2 = randomZone2, randomZone1

    if randomZone1 == 0:
        previousZoneCum1 = 1
    else:
        previousZoneCum1 = cumsumzoneList[randomZone1-1] + 1
    if randomZone2 == 0:
        previousZoneCum2 = 1
    else:
        previousZoneCum2 = cumsumzoneList[randomZone2-1] + 1
    
    sequence[previousZoneCum1:previousZoneCum1+zoneList[randomZone1]], sequence[previousZoneCum2:previousZoneCum2],  = [], sequence[previousZoneCum1:previousZoneCum1+zoneList[randomZone1]]

    # Now change the zoneList
    zoneList.insert(randomZone2,zoneList[randomZone1] )
    del zoneList[randomZone1+1]

    return sequence, zoneList