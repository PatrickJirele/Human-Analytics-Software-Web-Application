import os
from appConfig import *

matplotlib.use('Agg')
dir = os.path.dirname(__file__)
path = os.path.join(dir,'static', 'datasets', 'current.csv')
displayedDirPath = os.path.join(dir,'static', 'currentlyDisplayed')
dfMain = pd.read_csv(path)

def updateDataset():
    dfMain = pd.read_csv(path)
    return dfMain

def saveImage(fileName, fig):
    normalPath = os.path.join(dir, 'static', 'graphs', fileName)
    displayPath = os.path.join(displayedDirPath, fileName)
    fig.savefig(normalPath, bbox_inches="tight")
    if (os.path.exists(displayPath)):
        fig.savefig(displayPath, bbox_inches="tight")
    
def createOther(df, columnName):
    dict = df[columnName].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    otherCount = 0
    otheredKeys = []
    for i, val in enumerate(vals):
        num = int(val)
        if num < OTHER_MIN_COUNT or ((len(df) - num) / len(df)) > (100 - OTHER_MIN_PERCENT) / 100:
            otherCount += num
            otheredKeys.append(keys[i])
            
    for i in range(len(df)):
        value = df.loc[i,columnName]
        if value in otheredKeys:
            df.loc[i,columnName]= "Other"
    return df
    
def singleCategoryGraph(type, columnName, fileName):
    dfMain = updateDataset()
    df = createOther(dfMain.copy(),columnName)
    dict = df[columnName].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    fig, ax = plt.subplots() 
    match (type):
        case "pie":
            xLoc = 1
            yLoc = 0.5 if columnName != 'Department' else 0.15
            explode = [0.01 for _ in range(len(keys))]
            ax.pie(vals, autopct='%1.1f%%', explode=explode)
            plt.legend(keys, loc=(xLoc, yLoc), bbox_transform=plt.gcf().transFigure)
            plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0)
            plt.title("% of Employees per " + columnName)
        case "treemap":
            for i, key in enumerate(keys):
                keys[i] = key + "\n" + "{:1.1f}".format((1-(len(df) - vals[i]) / len(df))*100) + "%"
            squarify.plot(vals, label=keys)    
            plt.axis("off")
            plt.title("% of Employees per " + columnName)
        case "bar":
            specialCase = (columnName == 'Race Ethnicity' or columnName == 'Department')
            width = 0.8 if not specialCase else 0.6
            plt.bar(keys, vals, width = width)
            plt.xlabel(columnName)
            plt.ylabel("# of Employees")
            plt.title("# of Employees per " + columnName)
            if specialCase:
                plt.xticks(rotation=45, ha='right')
    saveImage(fileName,fig)

def histogram(columnName, fileName):
    df = updateDataset()
    unsortedDict = df[columnName].value_counts().to_dict()
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
    plt.xlabel(columnName)
    plt.ylabel("# of Employees")
    plt.title("# of Employees per " + columnName)
    saveImage(fileName, fig)


def stackedBarChart(mainColumnName, secondaryColumnName, fileName):
    df = updateDataset()
    df = createOther(df,mainColumnName)
    df = createOther(df,secondaryColumnName)
    dict = {}
    subDict = {}
    xLabels = df[mainColumnName].unique()
    xLabels = ['N/A' if pd.isna(i) else i for i in xLabels]
    yLabels = df[secondaryColumnName].unique()
    yLabels = ['N/A' if pd.isna(i) else i for i in yLabels]
    
    for value in yLabels:
        subDict[value] = 0
    
    for value in xLabels:
        valuesDict = {}
        valuesDict['values'] = subDict.copy()
        dict[value] = valuesDict
    
    for index in df.index:
        mainValue = df[mainColumnName][index]
        secondaryValue = df[secondaryColumnName][index]
        dict[mainValue]['values'][secondaryValue] += 1
        
    values = []
    for yLabel in yLabels:
        values.append([dict[xLabel]['values'][yLabel] for xLabel in xLabels])

    fig, ax = plt.subplots()
    bottomTotal = [0 for _ in range(len(xLabels))]
    specialCase = (mainColumnName == 'Race Ethnicity' or mainColumnName == 'Department')
    width = 0.8 if not specialCase else 0.6
    for i in range(len(yLabels)):
        ax.bar(xLabels, values[i], bottom=bottomTotal, label=str(yLabels[i]), width=width)
        for x in range(len(bottomTotal)):
            bottomTotal[x] += values[i][x]
    plt.xlabel(mainColumnName)
    ax.set_ylabel('# of Employees')
    ax.set_title('Breakdown of # of Employees per '+ mainColumnName + ' by ' + secondaryColumnName)
    if (specialCase):
        plt.xticks(rotation=45, ha='right')
    xLoc = 1
    yLoc = 0.5 if secondaryColumnName != 'Department' else 0
    plt.legend(loc=(xLoc, yLoc), bbox_transform=plt.gcf().transFigure)
    saveImage(fileName, fig)
