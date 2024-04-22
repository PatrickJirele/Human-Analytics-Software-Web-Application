from appConfig import *

dir = os.path.dirname(__file__)
path = os.path.join(dir,'static', 'datasets', 'current.csv')
displayedDirPath = os.path.join(dir,'static', 'currentlyDisplayed')
dfMain = None

def updateDB():
    return pd.read_csv(path)


def saveImage(fileName, fig, genericTitle, customTitle):
    finalTitle = genericTitle if customTitle == "" or customTitle == None else customTitle
    plt.title(finalTitle)
    
    normalPath = os.path.join(dir, 'static', 'graphs', fileName)
    displayPath = os.path.join(displayedDirPath, fileName)
    fig.savefig(normalPath, bbox_inches="tight")
    if (os.path.exists(displayPath)):
        fig.savefig(displayPath, bbox_inches="tight")
    
def createOther(df, columnName, description = ""):
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
            
    if (len(otheredKeys) > 1):
        description += "The 'Other' category consists of the following categories: <br>" if description == "" else ""
        for key in otheredKeys:
            description += "-" + str(key) + "<br>"
    elif (len(otheredKeys) == 1):
        description = "The 'Other' category consists of one category."
    
    return df, description
    
    
def singleCategoryGraph(type, columnName, fileName, customTitle, useQuantity):
    df, description = createOther(updateDB(),columnName)
    dict = df[columnName].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    fig, ax = plt.subplots()
    genericTitle = ""
    match (type):
        case "Pie":
            xLoc = 1
            yLoc = 0.5 if columnName != 'Department' else 0.15
            explode = [0.01 for _ in range(len(keys))]
            ax.pie(vals, autopct='%1.1f%%', pctdistance=0.85, explode=explode)
            plt.legend(keys, loc=(xLoc, yLoc), bbox_transform=plt.gcf().transFigure)
            plt.subplots_adjust(left=0.0, bottom=0.0, right=1.0)
            genericTitle = "% of Employees per " + columnName
        case "Bar":
            specialCase = (columnName == 'Race Ethnicity' or columnName == 'Department')
            width = 0.8 if not specialCase else 0.6
            if not useQuantity:
                for i in range(len(vals)):
                    vals[i] = (1-(len(df) - vals[i]) / len(df))*100
            plt.bar(keys, vals, width = width)
            plt.xlabel(columnName)
            symbol = "#" if useQuantity else "%"
            plt.ylabel(symbol + " of Employees")
            genericTitle = symbol + " of Employees per " + columnName
            if specialCase:
                plt.xticks(rotation=45, ha='right')
    saveImage(fileName,fig, genericTitle, customTitle)
    return description



def histogram(columnName, fileName, customTitle, useQuantity):
    dfMain = updateDB()
    df = dfMain.copy()
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
    if not useQuantity:
                for i in range(len(vals)):
                    vals[i] = (1-(len(df) - vals[i]) / len(df))*100
    axs.bar(keys, vals, width=1.0)
    plt.xlabel(columnName)
    symbol = "#" if useQuantity else "%"
    plt.ylabel(symbol + " of Employees")
    genericTitle = symbol + " of Employees per " + columnName
    saveImage(fileName, fig, genericTitle, customTitle)
    return ""


def stackedBarChart(mainColumnName, secondaryColumnName, fileName, customTitle, useQuantity):
    df, description = createOther(updateDB(),mainColumnName)
    df, description = createOther(df,secondaryColumnName, description)
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
    
    if not useQuantity:
        for i in range(len(values)):
            for x in range(len(values[i])):
                values[i][x] = (1-(len(df) - values[i][x]) / len(df))*100
    
    fig, ax = plt.subplots()
    bottomTotal = [0 for _ in range(len(xLabels))]
    specialCase = (mainColumnName == 'Race Ethnicity' or mainColumnName == 'Department')
    width = 0.8 if not specialCase else 0.6
    for i in range(len(yLabels)):
        ax.bar(xLabels, values[i], bottom=bottomTotal, label=str(yLabels[i]), width=width)
        for x in range(len(bottomTotal)):
            bottomTotal[x] += values[i][x]
    plt.xlabel(mainColumnName)
    symbol = "#" if useQuantity else "%"
    ax.set_ylabel(symbol + ' of Employees')
    genericTitle = 'Breakdown of ' + symbol + ' of Employees per '+ mainColumnName + ' by ' + secondaryColumnName
    if (specialCase):
        plt.xticks(rotation=45, ha='right')
    xLoc = 1
    yLoc = 0.5 if secondaryColumnName != 'Department' else 0
    plt.legend(loc=(xLoc, yLoc), bbox_transform=plt.gcf().transFigure)
    saveImage(fileName, fig, genericTitle, customTitle)
    return description

def treemap(mainColumnName, secondaryColumnName, fileName, customTitle, useQuantity):
    df, description = createOther(updateDB(),mainColumnName)
    dict = df[mainColumnName].value_counts().to_dict()
    keys = list(dict.keys())
    vals = list(dict.values())
    fig, ax = plt.subplots()
    genericTitle = ""
    area = []
    averageList = []
    for i, key in enumerate(keys):
        size = (1-(len(df) - vals[i]) / len(df))*100
        area.append(int(size))
        keys[i] = key + "\n" + "{:1.1f}".format(size) + "%"
        average = df.loc[(df[mainColumnName] == key), secondaryColumnName].mean()
        averageList.append(average)
    treeDF = pd.DataFrame({"area":area,"keys":keys, "average":averageList})
    cmapOG = plt.cm.get_cmap('Reds')
    cmap = plt.cm.colors.ListedColormap(cmapOG(np.linspace(0.05, 0.9, 200)))
    trc = tr.treemap(ax, treeDF, area="area", labels="keys", fill='average', cmap=cmap,
                     rectprops={'ec':'w', 'lw':2},
                     textprops={'c':'k' ,'reflow':True, 'place':'top left', 'max_fontsize':20})
    
    
    cb = fig.colorbar(trc.mappable, ax=ax, shrink=0.8)
    cb.ax.set_ylabel('Average ' + secondaryColumnName, rotation=270, labelpad=15)
    cb.outline.set_edgecolor('w')
    
    ax.axis('off')
    plt.axis("off")
    genericTitle = "Average " + secondaryColumnName + " Per " + mainColumnName
    genericTitle = "% of Employees per " + mainColumnName + " w/ average " + secondaryColumnName
    saveImage(fileName,fig, genericTitle, customTitle)
    return description

