def objectiveValue(ttMatrix, sequence):
    totalCosts = 0
    for j in range(len(sequence)-1):
        totalCosts += ttMatrix[sequence[j], sequence[j+1]]
    return totalCosts