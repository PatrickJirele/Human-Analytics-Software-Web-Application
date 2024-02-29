import pandas as pd
import os
import matplotlib.pyplot as plt

fileName = 'preprocessed.csv'
dir = os.path.dirname(__file__)
originalPath = os.path.join(dir, fileName)
df = pd.read_csv(originalPath)

def makeAndStoreGraph(name, fileName):
    dict = df[name].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    for i, val in enumerate(vals):
        vals[i] = int(val)
    fig, ax = plt.subplots()
    ax.pie(vals, labels=keys, autopct='%1.1f%%')
    path = os.path.join(dir, 'graphs')
    path = os.path.join(path, fileName)
    fig.savefig(path)
    
def yearsBarChart(fileName):
    unsortedDict = df['Years At Western'].value_counts().to_dict()
    keysMax = max(list(unsortedDict.keys()))
    for i in range(keysMax+1):
        if (i not in unsortedDict.keys()):
            unsortedDict[i] = 0
    sortedDict = dict(sorted(unsortedDict.items()))
    keys = list(sortedDict.keys())
    vals = list(sortedDict.values())
    fig, axs = plt.subplots()
    axs.bar(keys, vals) 
    path = os.path.join(dir, 'graphs')
    path = os.path.join(path, fileName)
    fig.savefig(path)
    
    
    
        

makeAndStoreGraph('Race/Ethnicity', 'raceEth.png')
makeAndStoreGraph('Gender', 'gender.png')
makeAndStoreGraph('Employee Type', 'employeeType.png')
yearsBarChart('years.png')