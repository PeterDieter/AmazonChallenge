import random
import numpy as np

def randomSwapInZone(sequence, zoneList):
    randomZone = np.random.choice(np.arange(0, len(zoneList)), p=(np.array(zoneList)-1)/(sum(zoneList)-len(zoneList)))
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


def inZoneTwoOptChange(sequence, zoneList):
    randomZone = np.random.choice(np.arange(0, len(zoneList)), p=(np.array(zoneList)-1)/(sum(zoneList)-len(zoneList)))
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
    randomZone = np.random.choice(np.arange(0, len(zoneList)), p=(np.array(zoneList)-1)/(sum(zoneList)-len(zoneList)))
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