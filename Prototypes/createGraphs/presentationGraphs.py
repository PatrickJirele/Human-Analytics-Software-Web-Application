import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

fileName = 'preprocessed.csv'
dir = os.path.dirname(__file__)
originalPath = os.path.join(dir, fileName)
df = pd.read_csv(originalPath)

def makeAndStoreGraph(name, fileName):
    dict = df[name].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    otherCount = 0
    otheredRows = []
    for i, val in enumerate(vals):
        num = int(val)
        if (num >= 10):
            vals[i]
        else:
            otherCount += num
            otheredRows.append(i)


    for i in otheredRows:
        try:
            del vals[i]
            del keys[i]
        except:
            pass
     
    
    if (otherCount > 0):
        keys.append("Other")
        vals.append(otherCount)
    
    fig, ax = plt.subplots(figsize=[13,6])
    ax.pie(vals, labels=keys, autopct='%1.1f%%')
    path = os.path.join(dir, 'graphs')
    path = os.path.join(path, fileName)
    fig.savefig(path)

def yearsBarChart(fileName):
    unsortedDict = df['Years At Western'].value_counts().to_dict()
    keysMax = max(list(unsortedDict.keys()))
    keysMin = min(list(unsortedDict.keys()))
    for i in range(keysMax+1):
        if (i not in unsortedDict.keys()):
            unsortedDict[i] = 0
    sortedDict = dict(sorted(unsortedDict.items()))
    keys = list(sortedDict.keys())
    vals = list(sortedDict.values())
    fig, axs = plt.subplots()
    axs.bar(keys, vals, width=1.0) 
    path = os.path.join(dir, 'graphs')
    path = os.path.join(path, fileName)
    fig.savefig(path, dpi=100)

    
    
def bar(name, fileName):
    dict = df[name].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    otherCount = 0
    otheredRows = []
    for i, val in enumerate(vals):
        num = int(val)
        if (num >= 10):
            vals[i]
        else:
            otherCount += num
            otheredRows.append(i)


    for i in otheredRows:
        try:
            del vals[i]
            del keys[i]
        except:
            pass
     
    
    if (otherCount > 0):
        keys.append("Other")
        vals.append(otherCount)
    fig, axs = plt.subplots()
    axs.bar(keys, vals) 
    path = os.path.join(dir, 'graphs')
    path = os.path.join(path, fileName)
    fig.savefig(path, dpi=100)
 
        

makeAndStoreGraph('Department', 'department.png')
bar('Gender', 'gender.png')
yearsBarChart('years.png')